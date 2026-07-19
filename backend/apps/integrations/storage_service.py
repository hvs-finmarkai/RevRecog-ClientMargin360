import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Optional


class FileServiceError(Exception):
    pass


class FileValidationError(FileServiceError):
    pass


class FileScanError(FileServiceError):
    pass


class FileNotFoundError(FileServiceError):
    pass


class FileDeleteError(FileServiceError):
    pass


ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 25 * 1024 * 1024

MALWARE_SIGNATURES = [
    b'\x4d\x5a',
    b'\x7f\x45\x4c\x46',
    b'<%eval',
    b'<%execute',
    b'<script>',
    b'powershell -enc',
    b'/bin/sh',
    b'cmd.exe /c',
    b'\x00\x00\x00\x00\x00\x00\x00\x00MSCF',
    b'TVqQAAMAAAA',
]

MIME_TYPE_MAP = {
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
}


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list = field(default_factory=list)
    file_size: int = 0
    file_extension: str = ""
    mime_type: str = ""


@dataclass
class ScanResult:
    is_clean: bool
    threats_found: list = field(default_factory=list)
    scan_timestamp: datetime = field(default_factory=datetime.utcnow)
    file_hash: str = ""


@dataclass
class DocumentRecord:
    document_id: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str
    uploaded_at: datetime
    entity_type: str
    entity_id: str
    url: str = ""


@dataclass
class FileResponse:
    document_id: str
    file_name: str
    content: bytes
    mime_type: str
    file_size: int


class FileUploadService:

    def __init__(self, storage_backend=None):
        if storage_backend is None:
            from apps.contracts.storage import get_storage_backend
            self._storage = get_storage_backend()
        else:
            self._storage = storage_backend
        self._documents = {}

    def upload_contract(self, file: BinaryIO, contract_id: str) -> DocumentRecord:
        return self._upload_file(file, contract_id, "contract")

    def upload_invoice(self, file: BinaryIO, invoice_id: str) -> DocumentRecord:
        return self._upload_file(file, invoice_id, "invoice")

    def get_document(self, document_id: str) -> FileResponse:
        record = self._documents.get(document_id)
        if record is None:
            raise FileNotFoundError(f"Document not found: {document_id}")

        try:
            content = self._storage.download(record.file_path)
        except Exception as e:
            raise FileServiceError(f"Failed to retrieve document content: {e}")

        return FileResponse(
            document_id=record.document_id,
            file_name=record.file_name,
            content=content,
            mime_type=record.mime_type,
            file_size=record.file_size
        )

    def delete_document(self, document_id: str) -> bool:
        record = self._documents.get(document_id)
        if record is None:
            raise FileNotFoundError(f"Document not found: {document_id}")

        try:
            result = self._storage.delete(record.file_path)
            if result:
                del self._documents[document_id]
            return result
        except Exception as e:
            raise FileDeleteError(f"Failed to delete document: {e}")

    def validate_file(self, file: BinaryIO) -> ValidationResult:
        errors = []
        file_name = getattr(file, 'name', '')
        file_size = self._get_file_size(file)

        extension = Path(file_name).suffix.lower() if file_name else ''

        if not extension:
            errors.append("File has no extension")
        elif extension not in ALLOWED_EXTENSIONS:
            errors.append(f"File type '{extension}' not allowed. Allowed: {sorted(ALLOWED_EXTENSIONS)}")

        if file_size > MAX_FILE_SIZE:
            errors.append(f"File size {file_size} bytes exceeds maximum {MAX_FILE_SIZE} bytes (25MB)")

        if file_size == 0:
            errors.append("File is empty")

        mime_type = MIME_TYPE_MAP.get(extension, 'application/octet-stream')

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            file_size=file_size,
            file_extension=extension,
            mime_type=mime_type
        )

    def scan_file(self, file: BinaryIO) -> ScanResult:
        threats = []
        file_hash = ""

        try:
            current_pos = file.tell() if hasattr(file, 'tell') else 0
            content = file.read(8192)

            if hasattr(file, 'seek'):
                file.seek(current_pos)

            hasher = hashlib.sha256()
            if hasattr(file, 'seek'):
                file.seek(0)
                while True:
                    chunk = file.read(65536)
                    if not chunk:
                        break
                    hasher.update(chunk)
                file.seek(current_pos)
            else:
                hasher.update(content)

            file_hash = hasher.hexdigest()

            for signature in MALWARE_SIGNATURES:
                if signature in content:
                    threats.append(f"Suspicious signature detected: {signature[:10]}")

            file_name = getattr(file, 'name', '').lower()
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.msi']
            for ext in dangerous_extensions:
                if file_name.endswith(ext):
                    threats.append(f"Dangerous file extension: {ext}")

        except Exception as e:
            raise FileScanError(f"File scan failed: {e}")

        return ScanResult(
            is_clean=len(threats) == 0,
            threats_found=threats,
            scan_timestamp=datetime.utcnow(),
            file_hash=file_hash
        )

    def _upload_file(self, file: BinaryIO, entity_id: str, entity_type: str) -> DocumentRecord:
        validation = self.validate_file(file)
        if not validation.is_valid:
            raise FileValidationError(f"File validation failed: {'; '.join(validation.errors)}")

        scan_result = self.scan_file(file)
        if not scan_result.is_clean:
            raise FileScanError(f"File security scan failed: {'; '.join(scan_result.threats_found)}")

        document_id = str(uuid.uuid4())
        file_name = getattr(file, 'name', f'{document_id}{validation.file_extension}')
        safe_name = self._sanitize_filename(file_name)
        storage_path = f"{entity_type}s/{entity_id}/{document_id}/{safe_name}"

        if hasattr(file, 'seek'):
            file.seek(0)

        try:
            url = self._storage.upload(file, storage_path)
        except Exception as e:
            raise FileServiceError(f"Failed to upload file: {e}")

        record = DocumentRecord(
            document_id=document_id,
            file_name=safe_name,
            file_path=storage_path,
            file_size=validation.file_size,
            mime_type=validation.mime_type,
            file_hash=scan_result.file_hash,
            uploaded_at=datetime.utcnow(),
            entity_type=entity_type,
            entity_id=entity_id,
            url=url
        )

        self._documents[document_id] = record
        return record

    def _get_file_size(self, file: BinaryIO) -> int:
        if hasattr(file, 'size'):
            return file.size

        if hasattr(file, 'seek') and hasattr(file, 'tell'):
            current_pos = file.tell()
            file.seek(0, 2)
            size = file.tell()
            file.seek(current_pos)
            return size

        return 0

    def _sanitize_filename(self, filename: str) -> str:
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
        name = Path(filename).name
        sanitized = ''.join(c if c in safe_chars else '_' for c in name)
        if len(sanitized) > 255:
            ext = Path(sanitized).suffix
            sanitized = sanitized[:255 - len(ext)] + ext
        return sanitized
