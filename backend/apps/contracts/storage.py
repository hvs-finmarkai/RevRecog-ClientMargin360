import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional

from django.conf import settings


class StorageError(Exception):
    pass


class StorageUploadError(StorageError):
    pass


class StorageDownloadError(StorageError):
    pass


class StorageDeleteError(StorageError):
    pass


class StorageNotFoundError(StorageError):
    pass


class StorageBackend(ABC):

    @abstractmethod
    def upload(self, file: BinaryIO, path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def download(self, path: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def delete(self, path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def exists(self, path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_url(self, path: str) -> str:
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):

    def __init__(self):
        self.base_path = Path(getattr(settings, 'MEDIA_ROOT', '/tmp/media')) / 'contracts'
        self.base_url = getattr(settings, 'MEDIA_URL', '/media/')
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload(self, file: BinaryIO, path: str) -> str:
        try:
            full_path = self.base_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'wb') as destination:
                if hasattr(file, 'chunks'):
                    for chunk in file.chunks():
                        destination.write(chunk)
                else:
                    shutil.copyfileobj(file, destination)
            return self.get_url(path)
        except (IOError, OSError) as e:
            raise StorageUploadError(f"Failed to upload file to {path}: {e}")

    def download(self, path: str) -> bytes:
        full_path = self.base_path / path
        if not full_path.exists():
            raise StorageNotFoundError(f"File not found: {path}")
        try:
            return full_path.read_bytes()
        except (IOError, OSError) as e:
            raise StorageDownloadError(f"Failed to download file from {path}: {e}")

    def delete(self, path: str) -> bool:
        full_path = self.base_path / path
        if not full_path.exists():
            return False
        try:
            full_path.unlink()
            return True
        except (IOError, OSError) as e:
            raise StorageDeleteError(f"Failed to delete file at {path}: {e}")

    def exists(self, path: str) -> bool:
        return (self.base_path / path).exists()

    def get_url(self, path: str) -> str:
        return f"{self.base_url}contracts/{path}"


class S3StorageBackend(StorageBackend):

    def __init__(self):
        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise StorageError("boto3 is required for S3 storage backend. Install with: pip install boto3")

        self.bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
        self.region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
        self.prefix = os.environ.get('AWS_S3_KEY_PREFIX', 'contracts/')
        self.custom_domain = os.environ.get('AWS_S3_CUSTOM_DOMAIN', '')

        if not self.bucket_name:
            raise StorageError("AWS_STORAGE_BUCKET_NAME environment variable is required")

        config = Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'standard'}
        )

        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region,
            config=config
        )

    def _get_key(self, path: str) -> str:
        return f"{self.prefix}{path}"

    def upload(self, file: BinaryIO, path: str) -> str:
        try:
            import io
            key = self._get_key(path)
            if hasattr(file, 'chunks'):
                buffer = io.BytesIO()
                for chunk in file.chunks():
                    buffer.write(chunk)
                buffer.seek(0)
                self.client.upload_fileobj(buffer, self.bucket_name, key)
            else:
                self.client.upload_fileobj(file, self.bucket_name, key)
            return self.get_url(path)
        except Exception as e:
            raise StorageUploadError(f"Failed to upload file to S3 at {path}: {e}")

    def download(self, path: str) -> bytes:
        try:
            import io
            key = self._get_key(path)
            buffer = io.BytesIO()
            self.client.download_fileobj(self.bucket_name, key, buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            if 'NoSuchKey' in str(e):
                raise StorageNotFoundError(f"File not found in S3: {path}")
            raise StorageDownloadError(f"Failed to download file from S3 at {path}: {e}")

    def delete(self, path: str) -> bool:
        try:
            key = self._get_key(path)
            if not self.exists(path):
                return False
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            raise StorageDeleteError(f"Failed to delete file from S3 at {path}: {e}")

    def exists(self, path: str) -> bool:
        try:
            key = self._get_key(path)
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def get_url(self, path: str) -> str:
        key = self._get_key(path)
        if self.custom_domain:
            return f"https://{self.custom_domain}/{key}"
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"


class MinIOStorageBackend(StorageBackend):

    def __init__(self):
        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise StorageError("boto3 is required for MinIO storage backend. Install with: pip install boto3")

        self.endpoint_url = os.environ.get('MINIO_ENDPOINT_URL', 'http://localhost:9000')
        self.bucket_name = os.environ.get('MINIO_BUCKET_NAME', 'contracts')
        self.access_key = os.environ.get('MINIO_ACCESS_KEY', '')
        self.secret_key = os.environ.get('MINIO_SECRET_KEY', '')
        self.prefix = os.environ.get('MINIO_KEY_PREFIX', 'contracts/')

        if not self.access_key or not self.secret_key:
            raise StorageError("MINIO_ACCESS_KEY and MINIO_SECRET_KEY environment variables are required")

        config = Config(
            signature_version='s3v4',
            retries={'max_attempts': 3, 'mode': 'standard'}
        )

        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=config
        )

        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except Exception:
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
            except Exception as e:
                raise StorageError(f"Failed to create MinIO bucket: {e}")

    def _get_key(self, path: str) -> str:
        return f"{self.prefix}{path}"

    def upload(self, file: BinaryIO, path: str) -> str:
        try:
            import io
            key = self._get_key(path)
            if hasattr(file, 'chunks'):
                buffer = io.BytesIO()
                for chunk in file.chunks():
                    buffer.write(chunk)
                buffer.seek(0)
                self.client.upload_fileobj(buffer, self.bucket_name, key)
            else:
                self.client.upload_fileobj(file, self.bucket_name, key)
            return self.get_url(path)
        except Exception as e:
            raise StorageUploadError(f"Failed to upload file to MinIO at {path}: {e}")

    def download(self, path: str) -> bytes:
        try:
            import io
            key = self._get_key(path)
            buffer = io.BytesIO()
            self.client.download_fileobj(self.bucket_name, key, buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            if 'NoSuchKey' in str(e) or '404' in str(e):
                raise StorageNotFoundError(f"File not found in MinIO: {path}")
            raise StorageDownloadError(f"Failed to download file from MinIO at {path}: {e}")

    def delete(self, path: str) -> bool:
        try:
            key = self._get_key(path)
            if not self.exists(path):
                return False
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            raise StorageDeleteError(f"Failed to delete file from MinIO at {path}: {e}")

    def exists(self, path: str) -> bool:
        try:
            key = self._get_key(path)
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def get_url(self, path: str) -> str:
        key = self._get_key(path)
        return f"{self.endpoint_url}/{self.bucket_name}/{key}"


_storage_backend_instance: Optional[StorageBackend] = None


def get_storage_backend() -> StorageBackend:
    global _storage_backend_instance

    if _storage_backend_instance is not None:
        return _storage_backend_instance

    backend_type = os.environ.get('STORAGE_BACKEND', 'local').lower()

    backends = {
        'local': LocalStorageBackend,
        's3': S3StorageBackend,
        'minio': MinIOStorageBackend,
    }

    if backend_type not in backends:
        raise StorageError(f"Unknown storage backend: {backend_type}. Options: {list(backends.keys())}")

    try:
        _storage_backend_instance = backends[backend_type]()
    except ImportError:
        _storage_backend_instance = LocalStorageBackend()

    return _storage_backend_instance
