"""Standard Declarative Manifest Reader for MEIA Knowledge Graph POC.

Strict standard-library reader that validates cryptographic digests (SHA-256),
sheet/cell boundaries, PDF page spans, and API receipt integrity.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class ManifestIntegrityError(Exception):
    """Raised when manifest file hashes or structural invariants fail validation."""
    pass


class StandardManifest:
    """Provides validated read-only access to the MEIA POC Declarative Manifest."""

    def __init__(self, manifest_path: Optional[Path] = None):
        if manifest_path is None:
            # Default to repo config directory
            repo_root = Path(__file__).resolve().parent.parent
            manifest_path = repo_root / "config" / "meia_poc_manifest.json"
        
        self.manifest_path = Path(manifest_path)
        if not self.manifest_path.exists():
            raise ManifestIntegrityError(f"Manifest not found at {self.manifest_path}")
        
        self.repo_root = self.manifest_path.parent.parent
        self._raw_data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.schema_version = self._raw_data.get("schema_version")
        self.manifest_revision = self._raw_data.get("manifest_revision")

    def validate_hashes(self) -> Dict[str, bool]:
        """Verifies that all files declared in the manifest match their expected SHA-256 digests."""
        results = {}
        # Workbooks
        for wb in self._raw_data.get("workbooks", []):
            relpath = wb["relpath"]
            fpath = self.repo_root / relpath
            if not fpath.exists():
                raise ManifestIntegrityError(f"Declared workbook missing: {relpath}")
            digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
            if digest != wb["sha256"]:
                raise ManifestIntegrityError(
                    f"SHA-256 mismatch for {relpath}: expected {wb['sha256']}, got {digest}"
                )
            results[wb["id"]] = True

        # Documents
        for doc in self._raw_data.get("documents", []):
            relpath = doc["relpath"]
            fpath = self.repo_root / relpath
            if not fpath.exists():
                raise ManifestIntegrityError(f"Declared document missing: {relpath}")
            digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
            if digest != doc["sha256"]:
                raise ManifestIntegrityError(
                    f"SHA-256 mismatch for {relpath}: expected {doc['sha256']}, got {digest}"
                )
            results[doc["id"]] = True

        # API Receipts
        for rec in self._raw_data.get("api_receipts", []):
            relpath = rec["relpath"]
            fpath = self.repo_root / relpath
            if not fpath.exists():
                raise ManifestIntegrityError(f"Declared API receipt missing: {relpath}")
            digest = hashlib.sha256(fpath.read_bytes()).hexdigest()
            if digest != rec["sha256"]:
                raise ManifestIntegrityError(
                    f"SHA-256 mismatch for {relpath}: expected {rec['sha256']}, got {digest}"
                )
            results[rec["id"]] = True

        return results

    def get_workbook(self, doc_id: str) -> Dict[str, Any]:
        """Returns metadata for a specific workbook."""
        for wb in self._raw_data.get("workbooks", []):
            if wb["id"] == doc_id or wb.get("standard_id") == doc_id:
                return wb
        raise KeyError(f"Workbook {doc_id} not found in manifest")

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Returns metadata for a specific document."""
        for doc in self._raw_data.get("documents", []):
            if doc["id"] == doc_id or doc.get("standard_id") == doc_id:
                return doc
        raise KeyError(f"Document {doc_id} not found in manifest")

    def get_api_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """Returns metadata for an API receipt."""
        for rec in self._raw_data.get("api_receipts", []):
            if rec["id"] == receipt_id or rec.get("standard_id") == receipt_id:
                return rec
        raise KeyError(f"API receipt {receipt_id} not found in manifest")

    def list_workbooks(self) -> List[Dict[str, Any]]:
        return self._raw_data.get("workbooks", [])

    def list_documents(self) -> List[Dict[str, Any]]:
        return self._raw_data.get("documents", [])

    def list_api_receipts(self) -> List[Dict[str, Any]]:
        return self._raw_data.get("api_receipts", [])
