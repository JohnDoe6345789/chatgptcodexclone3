#!/usr/bin/env python3
"""
Cleanup script to remove generated files and directories.
Run: python cleanup.py
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any


def setup_logging(log_path: Path) -> None:
    """Configure logging for cleanup operations."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(
        fmt='[%(levelname)s] %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load the manifest file containing generated files."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def remove_files(files: List[str], base_dir: Path, logger: logging.Logger) -> Tuple[int, int]:
    """Remove files listed in manifest."""
    removed = 0
    failed = 0
    
    for relative_path in files:
        file_path = base_dir / relative_path
        
        if not file_path.exists():
            logger.debug(f"File not found (skipped): {relative_path}")
            continue
        
        try:
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"Removed file: {relative_path}")
                removed += 1
        except (OSError, PermissionError) as exc:
            logger.error(f"Failed to remove {relative_path}: {exc}")
            failed += 1
    
    return removed, failed


def remove_directories(directories: List[str], base_dir: Path, logger: logging.Logger) -> Tuple[int, int]:
    """Remove directories listed in manifest."""
    removed = 0
    failed = 0
    
    for relative_path in directories:
        dir_path = base_dir / relative_path
        
        if not dir_path.exists():
            logger.debug(f"Directory not found (skipped): {relative_path}")
            continue
        
        try:
            if dir_path.is_dir():
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory: {relative_path}")
                removed += 1
        except (OSError, PermissionError) as exc:
            logger.error(f"Failed to remove {relative_path}: {exc}")
            failed += 1
    
    return removed, failed


def remove_logs(base_dir: Path, logger: logging.Logger, log_files: Optional[List[str]] = None) -> Tuple[int, int]:
    """Remove generated log files."""
    removed = 0
    failed = 0
    
    if log_files is None:
        log_files = ["generator.log", "codex.log", "cleanup.log"]
    
    for log_file in log_files:
        log_path = base_dir / log_file
        
        if log_path.exists():
            try:
                log_path.unlink()
                logger.info(f"Removed log: {log_file}")
                removed += 1
            except Exception as exc:
                logger.error(f"Failed to remove {log_file}: {exc}")
                failed += 1
    
    return removed, failed


def remove_pycache(base_dir: Path, logger: logging.Logger) -> Tuple[int, int]:
    """Remove all __pycache__ directories recursively."""
    removed = 0
    failed = 0
    
    for pycache_dir in base_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            try:
                shutil.rmtree(pycache_dir)
                rel_path = pycache_dir.relative_to(base_dir)
                logger.info(f"Removed directory: {rel_path}")
                removed += 1
            except (OSError, PermissionError) as exc:
                logger.error(f"Failed to remove {pycache_dir}: {exc}")
                failed += 1
    
    return removed, failed


def main() -> int:
    """Main cleanup function."""
    base_dir = Path(__file__).resolve().parent
    manifest_path = base_dir / "manifest.json"
    
    setup_logging(base_dir / "cleanup.log")
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("Cleanup Started")
    logger.info(f"Base directory: {base_dir}")
    logger.info("=" * 80)
    
    try:
        manifest = load_manifest(manifest_path)
    except FileNotFoundError as exc:
        logger.error(str(exc))
        logger.error("Cannot proceed without manifest.json")
        return 1
    
    total_removed = 0
    total_failed = 0
    
    if "files" in manifest:
        logger.info("\nRemoving generated files...")
        removed, failed = remove_files(manifest["files"], base_dir, logger)
        total_removed += removed
        total_failed += failed
    
    if "directories" in manifest:
        logger.info("\nRemoving generated directories...")
        removed, failed = remove_directories(manifest["directories"], base_dir, logger)
        total_removed += removed
        total_failed += failed
    
    logger.info("\nRemoving __pycache__ directories...")
    removed, failed = remove_pycache(base_dir, logger)
    total_removed += removed
    total_failed += failed
    
    logger.info("\nRemoving log files...")
    removed, failed = remove_logs(base_dir, logger, manifest.get("logs"))
    total_removed += removed
    total_failed += failed
    
    logger.info("=" * 80)
    logger.info("CLEANUP COMPLETE")
    logger.info(f"  Removed: {total_removed}")
    logger.info(f"  Failed: {total_failed}")
    logger.info("=" * 80)
    
    if total_failed > 0:
        logger.error(f"{total_failed} items failed to remove")
        return 1
    
    logger.info("Cleanup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
