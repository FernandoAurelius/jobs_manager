import logging
import os

from django.http import FileResponse, JsonResponse  # JsonResponse might not be needed if using DRF Response
from rest_framework import status
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from job.models import Job, JobFile
from job.serializers import JobFileSerializer  # Ensure this import is present

logger = logging.getLogger(__name__)


class BinaryFileRenderer(BaseRenderer):
    media_type = "*/*"
    format = "file"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class JobFileView(APIView):
    renderer_classes = [JSONRenderer, BinaryFileRenderer]

    def save_file(self, job, file_obj, print_on_jobsheet):
        """
        Save file to disk and create or update JobFile record.
        Returns serialized JobFile data or an error dictionary.
        """
        job_folder = os.path.join(
            settings.DROPBOX_WORKFLOW_FOLDER, f"Job-{job.job_number}"
        )
        os.makedirs(job_folder, exist_ok=True)

        file_path = os.path.join(job_folder, file_obj.name)
        logger.info(
            "Attempting to save file: %s for job %s", file_obj.name, job.job_number
        )

        # Extra logging before writing
        logger.debug("File size (bytes) received from client: %d", file_obj.size)

        # If file_obj.size is 0, we can abort or raise a warning:
        if file_obj.size == 0:
            logger.warning(
                "Aborting save because the uploaded file size is 0 bytes: %s",
                file_obj.name,
            )
            return {  # This remains an error dict, handled by the caller
                "error": f"Uploaded file {file_obj.name} is empty (0 bytes), not saved."
            }

        try:
            bytes_written = 0
            with open(file_path, "wb") as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
                    bytes_written += len(chunk)

            logger.info("Wrote %d bytes to disk at %s", bytes_written, file_path)

            # Check final file size on disk
            file_size_on_disk = os.path.getsize(file_path)
            if file_size_on_disk < file_obj.size:
                logger.error(
                    "File on disk is smaller than expected! (on disk: %d, expected: %d)",
                    file_size_on_disk,
                    file_obj.size,
                )
                return {  # Error dict
                    "error": f"File {file_obj.name} is corrupted or incomplete."
                }
            else:
                logger.debug("File on disk verified with correct size.")

            relative_path = os.path.relpath(file_path, settings.DROPBOX_WORKFLOW_FOLDER)

            job_file, created = JobFile.objects.update_or_create(
                job=job,
                filename=file_obj.name,  # Assuming filename is unique per job for update_or_create
                defaults={
                    "file_path": relative_path,
                    "mime_type": file_obj.content_type,
                    "print_on_jobsheet": print_on_jobsheet,
                    "status": "active",  # Ensure new/updated files are active
                },
            )
            logger.info(
                "%s JobFile: %s (print_on_jobsheet=%s)",
                "Created" if created else "Updated",
                job_file.filename,
                job_file.print_on_jobsheet,
            )
            serializer = JobFileSerializer(job_file)
            return serializer.data  # Return serialized data

        except Exception as e:
            logger.exception("Error processing file %s: %s", file_obj.name, str(e))
            return {  # Error dict
                "error": f"Error uploading {file_obj.name}: {str(e)}"
            }

    def post(self, request):
        """
        Handle file uploads. Creates new JobFile records.
        """
        logger.debug("Processing POST request to upload files (creating new).")
        job_number = request.data.get("job_number")
        if not job_number:
            return Response(
                {"status": "error", "message": "Job number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            job = Job.objects.get(job_number=job_number)
        except Job.DoesNotExist:
            return Response(
                {"status": "error", "message": "Job not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        files = request.FILES.getlist("files")
        if not files:
            return Response(
                {"status": "error", "message": "No files uploaded"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print_on_jobsheet_str = request.data.get("print_on_jobsheet", "true")
        print_on_jobsheet = print_on_jobsheet_str.lower() in ["true", "1"]

        uploaded_files_data = []
        errors = []

        for file_obj in files:
            result = self.save_file(job, file_obj, print_on_jobsheet)
            if "error" in result:
                errors.append(result["error"])
            else:
                # result is now serialized data
                uploaded_files_data.append(result)

        if errors:
            return Response(
                {
                    "status": "partial_success" if uploaded_files_data else "error",
                    "uploaded": uploaded_files_data,  # This is now an array of serialized objects
                    "errors": errors,
                },
                status=(
                    status.HTTP_207_MULTI_STATUS
                    if uploaded_files_data
                    else status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "status": "success",
                "uploaded": uploaded_files_data,  # Array of serialized objects
                "message": "Files uploaded successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_by_number(self, job_number):
        """
        Return the file list of a job.
        """
        try:
            job = Job.objects.get(job_number=job_number)
        except Job.DoesNotExist:
            return Response(
                {"status": "error", "message": "Job not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        job_files = JobFile.objects.filter(job=job)
        if not job_files.exists():
            return Response([], status=status.HTTP_200_OK)

        response_data = []
        for file_obj in job_files:
            response_data.append(
                {
                    "id": str(file_obj.id),
                    "filename": file_obj.filename,
                    "file_path": file_obj.file_path,
                    "print_on_jobsheet": file_obj.print_on_jobsheet,
                    "is_accessible": file_obj.is_accessible,
                }
            )
        return Response(response_data, status=status.HTTP_200_OK)

    def _get_by_path(self, file_path):
        """
        Serve a specific file for download.
        """
        full_path = os.path.join(settings.DROPBOX_WORKFLOW_FOLDER, file_path)

        if not os.path.exists(full_path):
            return Response(
                {"status": "error", "message": "File not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            response = FileResponse(open(full_path, "rb"))

            import mimetypes

            content_type, _ = mimetypes.guess_type(full_path)
            if content_type:
                response["Content-Type"] = content_type

            response["Content-Disposition"] = (
                f'inline; filename="{os.path.basename(file_path)}"'
            )
            return response
        except Exception as e:
            logger.exception(f"Error serving file {file_path}")
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request, file_path=None, job_number=None):
        """
        Based on the request, serve a file for download or return the file list of the job.
        """
        if job_number:
            return self._get_by_number(job_number)
        elif file_path:
            return self._get_by_path(file_path)
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid request, provide file_path or job_number",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request):
        """
        Update an existing job file.
        Can update file content (replace) or just metadata (print_on_jobsheet).
        Expects job_number.
        If file content: expects 'files' (single file) in request.FILES.
        If metadata only: expects 'filename' and 'print_on_jobsheet' in request.data.
        """
        logger.debug("Processing PUT request to update an existing file.")

        job_number = request.data.get("job_number")
        if not job_number:
            return Response({"error": "Job number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(job_number=job_number)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        file_obj_from_request = request.FILES.get("files")  # For replacing file content
        filename_from_data = request.data.get("filename")  # For identifying file if not replacing content

        job_file = None

        if file_obj_from_request:
            # Updating file content (and potentially print_on_jobsheet)
            # Identify JobFile by job and the name of the uploaded file
            try:
                job_file = JobFile.objects.get(job=job, filename=file_obj_from_request.name)
            except JobFile.DoesNotExist:
                # If PUT is used to upload a new file if it doesn't exist (upsert-like for content)
                # This part of logic can be debated: should PUT create if not exists?
                # For now, let's assume PUT updates an existing JobFile identified by filename.
                logger.error(f"File '{file_obj_from_request.name}' not found for job {job_number} to update content.")
                return Response({"error": f"File '{file_obj_from_request.name}' not found for this job."}, status=status.HTTP_404_NOT_FOUND)

            print_on_jobsheet = str(request.data.get("print_on_jobsheet", str(job_file.print_on_jobsheet))).lower() in ["true", "1"]

            # Use save_file to handle disk operations and DB update
            # save_file will call update_or_create, effectively updating the existing job_file
            result = self.save_file(job, file_obj_from_request, print_on_jobsheet)

            if "error" in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)  # Or 500 if server error during save

            # result is already serialized data from save_file
            return Response(result, status=status.HTTP_200_OK)

        elif filename_from_data:
            # Updating metadata only (print_on_jobsheet)
            try:
                job_file = JobFile.objects.get(job=job, filename=filename_from_data)
            except JobFile.DoesNotExist:
                logger.error(f"File '{filename_from_data}' not found for job {job_number} to update metadata.")
                return Response({"error": f"File '{filename_from_data}' not found for this job."}, status=status.HTTP_404_NOT_FOUND)

            if 'print_on_jobsheet' not in request.data:
                return Response({"error": "print_on_jobsheet is required for metadata update."}, status=status.HTTP_400_BAD_REQUEST)

            print_on_jobsheet = str(request.data.get("print_on_jobsheet")).lower() in ["true", "1"]

            if job_file.print_on_jobsheet != print_on_jobsheet:
                job_file.print_on_jobsheet = print_on_jobsheet
                job_file.save(update_fields=['print_on_jobsheet'])
                logger.info(f"Updated print_on_jobsheet for {job_file.filename} to {print_on_jobsheet}")

            serializer = JobFileSerializer(job_file)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Either a file or filename must be provided for PUT."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, file_path=None):
        """
        Soft delete a job file by its ID. (file_path param is actually the job_file.id)
        Marks the file status as 'deleted' and removes from disk.
        Returns the serialized JobFile object.
        """
        job_file_id = file_path  # Parameter name from URL pattern

        try:
            job_file = JobFile.objects.get(id=job_file_id)

            full_disk_path = job_file._get_actual_file_disk_path  # Use model property

            if full_disk_path and os.path.exists(full_disk_path):
                try:
                    os.remove(full_disk_path)
                    logger.info("Deleted physical file from disk: %s", full_disk_path)
                except OSError as e:
                    logger.error(f"Error removing file from disk {full_disk_path}: {e}")
                    # Decide if this error should halt the soft delete.
                    # For now, we'll log and continue with soft delete.

            job_file.status = "deleted"
            job_file.save(update_fields=['status'])

            logger.info(
                "Soft-deleted JobFile record ID: %s (filename: %s, status set to 'deleted')",
                job_file_id,
                job_file.filename,
            )

            serializer = JobFileSerializer(job_file)
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return object with 200 OK

        except JobFile.DoesNotExist:
            logger.error("JobFile not found with id for deletion: %s", job_file_id)
            return Response(
                {"status": "error", "message": "File not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.exception("Error during soft delete of file ID %s: %s", job_file_id, str(e))
            return Response(
                {"status": "error", "message": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
