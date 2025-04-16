#!/usr/bin/env python3

import argparse
import logging
import shutil
import time
from pathlib import Path
from typing import Optional, Set
import sys

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


class BuildManager:
    def __init__(
            self,
            hardware_config: Optional[str] = None,
            control_surface_name: Optional[str] = None,
            custom_config_path: Optional[Path] = None,
    ):
        # Import config here so CLI args can override
        from sync_config import (
            HARDWARE_CONFIG,
            CONTROL_SURFACE_NAME,
            PROJECT_ROOT,
            SRC_ROOT,
            REMOTE_SCRIPTS_PATH,
        )

        self.hardware_config = hardware_config or HARDWARE_CONFIG
        self.control_surface_name = control_surface_name or CONTROL_SURFACE_NAME
        self.custom_config_path = custom_config_path

        # Define paths
        self.project_root = PROJECT_ROOT
        self.src_root = SRC_ROOT

        # Validate REMOTE_SCRIPTS_PATH before using it
        self._validate_remote_scripts_path(REMOTE_SCRIPTS_PATH)
        self.dest_root = REMOTE_SCRIPTS_PATH / self.control_surface_name

        if not self.dest_root.exists():
            raise RuntimeError(f"Destination directory does not exist: {self.dest_root}")

        self.hardware_root = self.project_root / "hardware" / self.hardware_config

        self.ignore_patterns = {  # i dont know man
            ".git",
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            ".gitignore",
            "log.txt"
        }
        self.retry_attempts = 3
        self.retry_delay = 1.0

        # Store detected symlinks to avoid checking on every run
        self.detected_symlinks: Set[Path] = set()
        self.symlinks_checked = False

    def _validate_remote_scripts_path(self, path: Path) -> None:
        """
        Validate that the REMOTE_SCRIPTS_PATH is safe to use.
        Checks for the existence of ClyphX_Pro component file to confirm
        this is a valid Ableton Remote Scripts directory.
        Raises ValueError if validation fails.
        """
        if not path.exists():
            raise RuntimeError(f"Remote Scripts path does not exist: {path}")

        # Safety check: Look for ClyphX_Pro component file
        clyphx_component_path = path / "ClyphX_Pro" / "clyphx_pro" / "ClyphX_ProComponent.pyc"

        if not clyphx_component_path.exists():
            red_warning = "\033[91m"
            reset_color = "\033[0m"
            print(
                f"{red_warning}WARNING: This does not appear to be a valid Ableton Remote Scripts directory!{reset_color}")
            print(f"{path}")
            print(f"{red_warning}Continuing may result in DATA LOSS or incorrect synchronization.{reset_color}")

            confirmation = input(
                f"Are you sure you want to proceed? This could result in data loss. (y/N): "
            ).lower()

            if confirmation != 'y':
                raise ValueError(f"Operation aborted for safety. Please verify REMOTE_SCRIPTS_PATH in sync_config.py")

    def should_ignore(self, path: Path) -> bool:
        """Check if a file or directory should be ignored."""
        path_str = str(path)
        return any(
            ignored in path_str or path.match(ignored)
            for ignored in self.ignore_patterns
        )

    def check_for_symlinks(self, dest: Path) -> bool:
        """
        Check if a destination path is a symlink.
        Returns True if it's a symlink, False otherwise.
        """
        if dest.is_symlink():
            yellow_warning = "\033[93m"
            reset_color = "\033[0m"
            logging.warning(f"{yellow_warning}SKIPPING: Destination is a symlink: {dest}{reset_color}")
            self.detected_symlinks.add(dest)
            return True
        return False

    def safe_copy(self, src: Path, dest: Path) -> None:
        """Copy a file with retries on failure."""
        # Skip if destination parent is in detected symlinks
        for symlink in self.detected_symlinks:
            if symlink in dest.parents or symlink == dest.parent:
                return

        for attempt in range(self.retry_attempts):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    # Only copy if the source file is newer or different size
                    src_stat = src.stat()
                    dest_stat = dest.stat()

                    if (src_stat.st_mtime > dest_stat.st_mtime or
                            src_stat.st_size != dest_stat.st_size):
                        shutil.copy2(src, dest)
                else:
                    shutil.copy2(src, dest)
                return
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    logging.error(f"Failed to copy {src} to {dest}: {e}")
                else:
                    time.sleep(self.retry_delay)

    def get_destination_files(self, dest_dir: Path) -> set:
        """Get a set of all files in the destination directory."""
        if not dest_dir.exists():
            return set()
        return {f.relative_to(dest_dir) for f in dest_dir.rglob('*') if f.is_file() and not self.should_ignore(f)}

    def get_source_files(self, src_dir: Path) -> dict:
        """Get a dict of all files in the source directory with modification times."""
        if not src_dir.exists():
            return {}
        return {
            f.relative_to(src_dir): f.stat().st_mtime
            for f in src_dir.rglob('*')
            if f.is_file() and not self.should_ignore(f)
        }

    def scan_for_symlinks(self, base_dir: Path) -> None:
        """
        Recursively scan a directory for symlinks.
        Only performed on first run.
        """
        if not base_dir.exists() or base_dir in self.detected_symlinks:
            return

        if base_dir.is_symlink():
            logging.warning(f"\033[93mDetected symlink directory: {base_dir}\033[0m")
            self.detected_symlinks.add(base_dir)
            return

        # Scan subdirectories
        for path in base_dir.iterdir():
            if path.is_dir():
                self.scan_for_symlinks(path)

    def sync_directory(self, src: Path, dest: Path) -> None:
        """Sync a directory from source to destination."""
        if not src.exists():
            raise RuntimeError(f"Source directory does not exist: {src}")

        # Check for symlinks on first run only
        if not self.symlinks_checked:
            self.scan_for_symlinks(dest)

        # Skip syncing if destination is a symlink
        if dest in self.detected_symlinks or dest.is_symlink():
            return

        # Create destination if it doesn't exist
        dest.mkdir(parents=True, exist_ok=True)

        # Get source and destination files
        src_files = self.get_source_files(src)
        dest_files = self.get_destination_files(dest)

        # Copy new and updated files
        for rel_path, mtime in src_files.items():
            src_file = src / rel_path
            dest_file = dest / rel_path

            # Skip if destination file is in a symlink directory
            skip = False
            for symlink in self.detected_symlinks:
                if symlink in dest_file.parents:
                    skip = True
                    break

            if skip:
                continue

            if not dest_file.exists() or dest_file.stat().st_mtime < mtime:
                self.safe_copy(src_file, dest_file)

        # Remove files in destination that don't exist in source
        for rel_path in dest_files:
            dest_file = dest / rel_path

            # Skip if file is in a symlink directory
            skip = False
            for symlink in self.detected_symlinks:
                if symlink in dest_file.parents:
                    skip = True
                    break

            if skip:
                continue

            if rel_path not in src_files:
                try:
                    dest_file.unlink()
                    logging.info(f"Removed orphaned file: {dest_file}")
                except Exception as e:
                    logging.error(f"Failed to remove {dest_file}: {e}")

        # Clean up empty directories
        self._cleanup_empty_dirs(dest)

    def _cleanup_empty_dirs(self, path: Path) -> None:
        """Remove empty directories recursively."""
        if not path.exists() or not path.is_dir() or path in self.detected_symlinks or path.is_symlink():
            return

        for child in path.iterdir():
            if child.is_dir() and child not in self.detected_symlinks and not child.is_symlink():
                self._cleanup_empty_dirs(child)

        # Check if directory is empty now
        if not any(path.iterdir()):
            try:
                path.rmdir()
                logging.info(f"Removed empty directory: {path}")
            except Exception as e:
                logging.error(f"Failed to remove empty directory {path}: {e}")

    def build(self) -> None:
        """Build the plugin by syncing all directories."""
        try:
            # Check for symlinks on first run only
            if not self.symlinks_checked:
                logging.info("Scanning for symlinks in destination directories...")
                self.scan_for_symlinks(self.dest_root)
                self.symlinks_checked = True
                if self.detected_symlinks:
                    symlink_list = "\n  - ".join([str(s) for s in self.detected_symlinks])
                    logging.warning(
                        f"\033[93mThe following symlinks were detected and will be skipped:\n  - {symlink_list}\033[0m")

            # Sync app directory
            self.sync_directory(self.src_root, self.dest_root)

            # Sync hardware config
            hardware_dest = self.dest_root / "hardware"
            self.sync_directory(self.hardware_root, hardware_dest)

            # Sync config from either custom_config_path or hardware-specific demo_config
            config_path = (
                self.custom_config_path
                if self.custom_config_path
                else self.hardware_root / "demo_config"
            )
            if config_path.exists():
                config_dest = self.dest_root / "_config"
                self.sync_directory(config_path, config_dest)

            logging.info("Build completed successfully")

        except Exception as e:
            logging.error(f"Build failed: {e}")
            raise


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, builder: BuildManager):
        self.builder = builder
        self.last_build = 0
        self.build_cooldown = 1.0  # Cooldown period in seconds
        self._build_pending = False

    def handle_change(self, event: FileSystemEvent) -> None:
        """Handle file system changes with a cooldown period."""
        if event.is_directory or self.builder.should_ignore(Path(event.src_path)):
            return

        current_time = time.time()
        if current_time - self.last_build >= self.build_cooldown:
            try:
                self.builder.build()
                self.last_build = current_time
                self._build_pending = False
            except Exception as e:
                logging.error(f"Build failed: {e}")
        else:
            self._build_pending = True

    def on_created(self, event: FileSystemEvent):
        self.handle_change(event)

    def on_modified(self, event: FileSystemEvent):
        self.handle_change(event)

    def on_deleted(self, event: FileSystemEvent):
        self.handle_change(event)

    def on_moved(self, event: FileSystemEvent):
        self.handle_change(event)


def main():
    parser = argparse.ArgumentParser(
        description="Build and watch Ableton Live Remote Script files"
    )
    parser.add_argument(
        "hardware_config", nargs="?", help="Hardware configuration name"
    )
    parser.add_argument("control_surface_name", nargs="?", help="Control surface name")
    parser.add_argument(
        "--custom-config",
        type=Path,
        help="Path to a custom config folder to override demo_config/",
    )
    args = parser.parse_args()

    try:
        builder = BuildManager(
            args.hardware_config,
            args.control_surface_name,
            args.custom_config,
        )

    except Exception as e:
        logging.critical(e)
        sys.exit(1)

    # Perform the initial build
    logging.info("Performing initial build...")
    builder.build()

    # Set up file watching
    observer = Observer()
    handler = ChangeHandler(builder)

    # Watch project directories
    dirs_to_watch = [
        builder.src_root,
        builder.hardware_root,
        builder.hardware_root / "demo_config",
        # builder.project_root / "preferences",
    ]

    # Dynamically add custom config path to watched directories if provided
    if args.custom_config:
        dirs_to_watch.append(args.custom_config)

    for dir_path in dirs_to_watch:
        if dir_path.exists():
            observer.schedule(handler, str(dir_path), recursive=True)
            logging.info(f"Watching directory: {dir_path}")
        else:
            raise RuntimeError(f"Directory {dir_path} does not exist")

    observer.start()
    logging.info("Watching for changes... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
            if handler._build_pending:
                handler.handle_change(FileSystemEvent(str(builder.src_root)))
    except KeyboardInterrupt:
        logging.info("Stopping file watcher...")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()