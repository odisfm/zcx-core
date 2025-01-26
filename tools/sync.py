#!/usr/bin/env python3

import argparse
import logging
import shutil
import time
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


class SyncManager:
    def __init__(
        self,
        hardware_config: Optional[str] = None,
        control_surface_name: Optional[str] = None,
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

        # Define paths
        self.dest_root = REMOTE_SCRIPTS_PATH / self.control_surface_name
        self.project_root = PROJECT_ROOT
        self.src_root = SRC_ROOT
        self.hardware_root = self.project_root / "hardware" / self.hardware_config

        self.ignore_patterns = {
            ".git",
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            ".gitignore",
        }
        self.retry_attempts = 3
        self.retry_delay = 1.0

    def should_ignore(self, path: Path) -> bool:
        path_str = str(path)
        return any(
            ignored in path_str or path.match(ignored)
            for ignored in self.ignore_patterns
        )

    def safe_copy(self, src: Path, dest: Path) -> None:
        for attempt in range(self.retry_attempts):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    dest.unlink()
                shutil.copy2(src, dest)
                return
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    logging.error(f"Failed to copy {src} to {dest}: {e}")
                else:
                    time.sleep(self.retry_delay)

    def sync_directory(self, src: Path, dest: Path) -> None:
        if not src.exists():
            logging.warning(f"Source directory does not exist: {src}")
            return

        # Clear destination
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)

        # Copy files
        for src_file in src.rglob("*"):
            if src_file.is_file() and not self.should_ignore(src_file):
                rel_path = src_file.relative_to(src)
                dest_file = dest / rel_path
                self.safe_copy(src_file, dest_file)

    def sync_all(self) -> None:
        """Sync all directories according to configuration"""
        try:
            # Sync app directory
            self.sync_directory(self.src_root, self.dest_root)

            # Sync hardware config
            self.sync_directory(self.hardware_root, self.dest_root / "hardware")

            # Sync config from hardware-specific demo_config
            demo_config_path = self.hardware_root / "demo_config"
            if demo_config_path.exists():
                self.sync_directory(demo_config_path, self.dest_root / "_config")

            # Sync preferences
            preferences_path = self.project_root / "preferences"
            if preferences_path.exists():
                self.sync_directory(preferences_path, self.dest_root / "_preferences")

            logging.info("Sync completed successfully")

        except Exception as e:
            logging.error(f"Sync failed: {e}")
            raise


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, syncer: SyncManager):
        self.syncer = syncer
        self.last_sync = 0
        self.sync_cooldown = 1.0
        self._sync_pending = False

    def handle_change(self, event: FileSystemEvent) -> None:
        if event.is_directory or self.syncer.should_ignore(Path(event.src_path)):
            return

        current_time = time.time()
        if current_time - self.last_sync >= self.sync_cooldown:
            try:
                self.syncer.sync_all()
                self.last_sync = current_time
                self._sync_pending = False
            except Exception as e:
                logging.error(f"Sync failed: {e}")
        else:
            self._sync_pending = True

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
        description="Sync Ableton Live Remote Script files"
    )
    parser.add_argument(
        "hardware_config", nargs="?", help="Hardware configuration name"
    )
    parser.add_argument("control_surface_name", nargs="?", help="Control surface name")
    args = parser.parse_args()

    syncer = SyncManager(args.hardware_config, args.control_surface_name)

    # Initial sync
    logging.info("Performing initial sync...")
    syncer.sync_all()

    # Set up file watching
    observer = Observer()
    handler = ChangeHandler(syncer)

    # Watch project directories
    dirs_to_watch = [
        syncer.src_root,
        syncer.hardware_root,
        syncer.hardware_root / "demo_config",
        syncer.project_root / "preferences",
    ]

    for dir_path in dirs_to_watch:
        if dir_path.exists():
            observer.schedule(handler, str(dir_path), recursive=True)
            logging.info(f"Watching directory: {dir_path}")

    observer.start()
    logging.info("Watching for changes... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
            if handler._sync_pending:
                handler.handle_change(FileSystemEvent(str(syncer.src_root)))
    except KeyboardInterrupt:
        logging.info("Stopping file watcher...")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
