"""
Script to create a complete, self-contained portable ZIP archive of meia_kg_poc
for easy deployment to another Windows machine.

Includes:
- All source code (src/)
- Pre-built Tri-Graph SQLite registry (storage/meia_tri_graph_registry.db)
- Pre-computed 1024-dim vector embeddings (storage/vdb_*.json)
- Rendered 180 DPI visual schematics & bounding box manifests (parsed/figures/)
- Golden competency question catalog & benchmarks (eval/)
- Automated Windows setup script (setup_windows.ps1) & requirements.txt
- Complete documentation & manifests (config/, docs/)

Excludes:
- .git repository history
- Virtual environments (.venv, env)
- Python bytecode (__pycache__, *.pyc)
- Pytest and scratch caches (.pytest_cache)
- Any existing archive zip files
"""

import sys
import zipfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode"
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".zip"
}


def package_portable_zip(output_path: Path) -> Path:
    print("=" * 70)
    print("  Creating MEIA Knowledge Graph POC Portable Archive")
    print(f"  Source: {REPO_ROOT}")
    print(f"  Destination: {output_path}")
    print("=" * 70)

    start_time = time.time()
    file_count = 0
    uncompressed_bytes = 0

    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in sorted(REPO_ROOT.rglob("*")):
            if not file_path.is_file():
                continue

            # Check if any parent part is in EXCLUDE_DIRS
            rel_parts = file_path.relative_to(REPO_ROOT).parts
            if any(part in EXCLUDE_DIRS for part in rel_parts):
                continue

            # Check extension
            if file_path.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            # Add to ZIP under meia_kg_poc/ root directory
            arcname = Path("meia_kg_poc").joinpath(*rel_parts)
            zf.write(file_path, arcname=str(arcname))
            file_count += 1
            uncompressed_bytes += file_path.stat().st_size

    elapsed = time.time() - start_time
    zip_bytes = output_path.stat().st_size

    print("\n[SUCCESS] Archive created successfully!")
    print(f"  Files Packed:        {file_count:,}")
    print(f"  Uncompressed Size:   {uncompressed_bytes / (1024 * 1024):.2f} MB")
    print(f"  Compressed Size:     {zip_bytes / (1024 * 1024):.2f} MB")
    print(f"  Elapsed Time:        {elapsed:.2f} seconds")
    print(f"  Archive Location:    {output_path.resolve()}")
    print("\nTo set up on another Windows machine:")
    print("  1. Extract this zip file.")
    print("  2. Open PowerShell in the extracted 'meia_kg_poc' directory.")
    print("  3. Run: powershell -ExecutionPolicy Bypass -File setup_windows.ps1")
    print("  4. Start the app: python -m src.web\n")

    return output_path


if __name__ == "__main__":
    default_dest = REPO_ROOT.parent / "meia_kg_poc_portable.zip"
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else default_dest
    package_portable_zip(dest)
