from rest_framework import serializers

from job.models import JobFile


class JobFileSerializer(serializers.ModelSerializer):
    is_accessible = serializers.BooleanField(read_only=True)  # Add this line

    class Meta:
        model = JobFile
        fields = [
            "id",
            "filename",
            "file_path",
            "mime_type",
            "uploaded_at",
            "status",
            "print_on_jobsheet",
            "is_accessible",  # Add this line
        ]
        read_only_fields = [
            "id",
            "filename",
            "file_path",
            "mime_type",
            "uploaded_at",
            "is_accessible",
        ]
