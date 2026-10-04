"""
Thin abstraction over Django's default storage backend. Exists as its own
service (rather than calling `default_storage` directly from
IngestionService) so that swapping local disk storage for S3/GCS in
production is a config change (DEFAULT_FILE_STORAGE / STORAGES setting),
and so tests can mock storage without touching Django settings.
"""

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile


class StorageService:
    def save(self, relative_path: str, uploaded_file: UploadedFile) -> str:
        """Saves the uploaded file and returns the storage path used."""
        return default_storage.save(relative_path, uploaded_file)

    def absolute_path(self, storage_path: str) -> str:
        return default_storage.path(storage_path)

    def delete(self, storage_path: str) -> None:
        if default_storage.exists(storage_path):
            default_storage.delete(storage_path)
