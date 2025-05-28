import os
import uuid

from django.db import models

from job.helpers import get_job_folder_path
from job.services.file_service import get_thumbnail_folder


class JobFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey("Job", related_name="files", on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # Stores path like "Job-12345/somefile.pdf"
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("deleted", "Deleted")],
        default="active",
    )
    print_on_jobsheet = models.BooleanField(default=True)

    @property
    def full_path(self):
        """Full system path to the JOB FOLDER."""
        return get_job_folder_path(self.job.job_number)

    @property
    def url(self):
        """URL to serve the file (if using Django to serve media)."""
        return f"/jobs/files/{self.file_path}"  # We'll need to add this URL pattern

    @property
    def thumbnail_path(self):
        """Return path to thumbnail if one exists."""
        # This property seems to correctly build its path using get_thumbnail_folder
        # and self.filename. Ensure get_thumbnail_folder uses settings.DROPBOX_WORKFLOW_FOLDER.
        from django.conf import settings  # Ensure settings are available
        if self.status == "deleted":
            return None

        # Assuming get_thumbnail_folder constructs a path relative to DROPBOX_WORKFLOW_FOLDER
        # or an absolute path that includes it.
        # Example: /path/to/dropbox/Job-XYZ/.thumbnails/filename.thumb.jpg
        thumb_folder = get_thumbnail_folder(self.job.job_number)  # This needs to be correct
        if not thumb_folder:  # Handle if get_thumbnail_folder can return None
            return None

        thumb_path = os.path.join(thumb_folder, f"{self.filename}.thumb.jpg")
        return thumb_path if os.path.exists(thumb_path) else None

    @property
    def _get_actual_file_disk_path(self):
        """
        Internal helper to get the absolute disk path of the file.
        self.file_path is relative to settings.DROPBOX_WORKFLOW_FOLDER.
        Example: self.file_path = "Job-123/somefile.pdf"
        """
        from django.conf import settings
        if not hasattr(settings, 'DROPBOX_WORKFLOW_FOLDER') or not settings.DROPBOX_WORKFLOW_FOLDER:
            # Log this critical configuration error
            # import logging
            # logger = logging.getLogger(__name__)
            # logger.error("DROPBOX_WORKFLOW_FOLDER is not configured in settings.")
            return None
        return os.path.join(settings.DROPBOX_WORKFLOW_FOLDER, self.file_path)

    @property
    def is_accessible(self):  # Renamed from is_locally_accessible
        """Checks if the file physically exists on disk."""
        if self.status == "deleted":  # App-level logical deletion
            return False

        actual_path = self._get_actual_file_disk_path
        if actual_path is None:
            return False  # Configuration issue

        return os.path.exists(actual_path)

    @property
    def size(self):
        """Return size of file in bytes if it exists on disk."""
        if self.status == "deleted":
            return None

        actual_path = self._get_actual_file_disk_path
        if actual_path is None:
            return None  # Configuration issue

        return os.path.getsize(actual_path) if os.path.exists(actual_path) else None

    class Meta:
        db_table = "workflow_jobfile"
        ordering = ["-uploaded_at"]
