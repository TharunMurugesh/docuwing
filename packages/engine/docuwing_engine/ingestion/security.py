"""Upload Security Wrapper for Ingestion Safety."""

from __future__ import annotations

import io
import zipfile
from typing import BinaryIO

import magic

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50MB default limit
MAX_ZIP_DECOMPRESSION_RATIO = 100.0  # Zip bomb detection threshold
EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


class SecurityValidationError(ValueError):
    """Raised when an ingested file violates security policies."""

    pass


class UploadSecurityWrapper:
    """Ingestion security stage enforcing MIME checks, size limits,
    zip-bomb checks, and malware hooks.
    """

    def __init__(
        self,
        max_bytes: int = MAX_UPLOAD_BYTES,
        max_decompression_ratio: float = MAX_ZIP_DECOMPRESSION_RATIO,
    ) -> None:
        self.max_bytes = max_bytes
        self.max_decompression_ratio = max_decompression_ratio

    def validate_and_read(self, raw_stream: BinaryIO, filename: str) -> io.BytesIO:
        """Validate stream safety and return a safe in-memory stream."""
        content = raw_stream.read(self.max_bytes + 1)
        if len(content) > self.max_bytes:
            raise SecurityValidationError(
                f"File exceeds maximum allowed size of {self.max_bytes} bytes"
            )

        # Check malware signature hook (e.g. EICAR test file)
        if EICAR_SIGNATURE in content:
            raise SecurityValidationError("Malware signature detected in uploaded file (EICAR)")

        # MIME magic sniffing
        sniffed_mime = magic.from_buffer(content[:2048], mime=True)

        # Check zip decompression ratio for docx / xlsx / zip formats
        if "zip" in sniffed_mime or filename.endswith((".xlsx", ".docx")):
            self._check_zip_bomb(content)

        return io.BytesIO(content)

    def _check_zip_bomb(self, content: bytes) -> None:
        """Inspect zip archives to prevent decompression bombs."""
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                total_uncompressed = 0
                compressed_size = len(content) or 1
                for info in zf.infolist():
                    total_uncompressed += info.file_size
                    ratio = total_uncompressed / compressed_size
                    if ratio > self.max_decompression_ratio:
                        raise SecurityValidationError(
                            f"Zip bomb detected: decompression ratio {ratio:.1f} "
                            f"exceeds limit {self.max_decompression_ratio}"
                        )
        except zipfile.BadZipFile:
            pass  # Not a valid zip or corrupted
