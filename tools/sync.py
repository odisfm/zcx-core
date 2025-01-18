#!/usr/bin/env python3

# AI slop

import logging
import shutil
import time
import traceback
from pathlib import Path
from typing import List

from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileMovedEvent
from watchdog.observers import Observer

# Import configuration
from sync_config import SyncPath, SYNC_PATHS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


class DirectorySyncer:
    def __init__(
        self, sync_paths: List[SyncPath], max_retries: int = 3, retry_delay: float = 1.0
    ):
        self.sync_paths = sync_paths
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.ignore_patterns = {
            ".git",
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            ".gitignore",
        }

    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored based on patterns"""
        path_str = str(path)
        return any(
            ignored in path_str
            or (path.is_file() and path.match(ignored))
            or (path.is_dir() and any(ignored in part for part in path.parts))
            for ignored in self.ignore_patterns
        )

    def safe_makedirs(self, path: Path):
        """Create directories with robust error handling"""
        for attempt in range(self.max_retries):
            try:
                path.mkdir(parents=True, exist_ok=True)
                return
            except (PermissionError, OSError) as e:
                logging.warning(f"Error creating directory {path}: {e}")
                time.sleep(self.retry_delay)

        logging.error(
            f"Failed to create directory {path} after {self.max_retries} attempts"
        )

    def safe_copy(self, src_path: Path, dest_path: Path):
        """Copy file with robust error handling"""
        for attempt in range(self.max_retries):
            try:
                # Ensure destination directory exists
                self.safe_makedirs(dest_path.parent)

                # Remove existing file if needed
                if dest_path.exists():
                    dest_path.unlink()

                # Copy with metadata
                shutil.copy2(src_path, dest_path)
                logging.info(f"Copied {src_path} to {dest_path}")
                return
            except (PermissionError, OSError) as e:
                logging.warning(f"Error copying {src_path} to {dest_path}: {e}")
                time.sleep(self.retry_delay)

        logging.error(
            f"Failed to copy {src_path} to {dest_path} after {self.max_retries} attempts"
        )

    def find_destinations_for_file(self, file_path: Path) -> List[tuple[Path, Path]]:
        """Find all destinations and relative paths for a given source file"""
        file_path = Path(file_path)
        results = []

        for sync_path in self.sync_paths:
            try:
                # Check if the file is under this source path
                if (
                    sync_path.source in file_path.parents
                    or sync_path.source == file_path
                ):
                    relative_path = file_path.relative_to(sync_path.source)
                    for dest in sync_path.destinations:
                        dest_path = dest / relative_path
                        results.append((dest_path, relative_path))
            except ValueError:
                continue
        return results

    def clear_destinations(self):
        # noinspection SpellCheckingInspection
        """Clear all destination directories while preserving specified subdirs"""
        processed_destinations = set()

        for sync_path in self.sync_paths:
            for dest in sync_path.destinations:
                if dest not in processed_destinations:
                    if dest.exists():
                        try:
                            for item in dest.iterdir():
                                if item.is_file():
                                    item.unlink()
                                elif (
                                    item.is_dir() and item.name not in sync_path.subdirs
                                ):
                                    shutil.rmtree(item)
                        except (PermissionError, OSError) as e:
                            logging.error(f"Error clearing destination {dest}: {e}")
                            continue

                    # Ensure specified subdirectories exist
                    for subdir in sync_path.subdirs:
                        self.safe_makedirs(dest / subdir)

                    processed_destinations.add(dest)

    def handle_rename(self, src_path: Path, dest_path: Path):
        """Handle file rename/move operations with robust error handling"""
        src_path, dest_path = Path(src_path), Path(dest_path)
        if self.should_ignore(src_path) or self.should_ignore(dest_path):
            return

        # Find all destinations for both source and destination paths
        old_destinations = self.find_destinations_for_file(src_path)
        new_destinations = self.find_destinations_for_file(dest_path)

        logging.info(f"Handling rename from {src_path} to {dest_path}")

        # Perform the rename in all relevant destinations
        for (old_dest_path, _), (new_dest_path, _) in zip(
            old_destinations, new_destinations
        ):
            try:
                if old_dest_path.exists():
                    logging.info(f"Renaming {old_dest_path} to {new_dest_path}")

                    # Ensure destination directory exists
                    self.safe_makedirs(new_dest_path.parent)

                    # Handle rename or copy
                    if not new_dest_path.exists():
                        old_dest_path.rename(new_dest_path)
                    else:
                        # If destination exists, copy the content and remove old file
                        shutil.copy2(dest_path, new_dest_path)
                        old_dest_path.unlink()

            except (FileNotFoundError, PermissionError, OSError) as e:
                logging.error(f"Error renaming {old_dest_path} to {new_dest_path}: {e}")

    def sync_files(self):
        """Sync all files according to configuration with robust error handling"""
        self.clear_destinations()

        for sync_path in self.sync_paths:
            if not Path(sync_path.source).exists():
                logging.warning(f"Source path does not exist: {sync_path.source}")
                continue

            logging.info(f"Syncing from {sync_path.source}")

            # Handle single file syncs
            if not sync_path.recursive:
                try:
                    source_file = Path(sync_path.source)
                    if source_file.is_file() and not self.should_ignore(source_file):
                        for dest in sync_path.destinations:
                            self.safe_copy(source_file, Path(dest))
                except Exception as e:
                    logging.error(f"Error syncing {source_file}: {e}")
                    logging.error(traceback.format_exc())
                continue

            # Handle recursive directory syncs
            for source_file in Path(sync_path.source).rglob("*"):
                try:
                    if source_file.is_file() and not self.should_ignore(source_file):
                        relative_path = source_file.relative_to(sync_path.source)

                        # Check if file should be excluded by pattern
                        if (
                            sync_path.exclude_patterns
                            and str(source_file) in sync_path.exclude_patterns
                        ):
                            continue

                        for dest in sync_path.destinations:
                            dest_file = Path(dest) / relative_path
                            self.safe_copy(source_file, dest_file)
                except Exception as e:
                    logging.error(f"Error syncing {source_file}: {e}")
                    logging.error(traceback.format_exc())


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, syncer: DirectorySyncer):
        self.syncer = syncer
        self.last_sync = 0
        self.sync_cooldown = 1.0
        self._sync_scheduled = False

    def schedule_sync(self):
        """Schedule a sync if one isn't already scheduled"""
        if not self._sync_scheduled:
            self._sync_scheduled = True
            self._do_sync()

    def _do_sync(self):
        """Perform the actual sync with error handling"""
        try:
            current_time = time.time()
            if current_time - self.last_sync >= self.sync_cooldown:
                logging.info("Syncing changes...")
                self.syncer.sync_files()
                self.last_sync = current_time
                self._sync_scheduled = False
        except Exception as e:
            logging.error(f"Sync failed: {e}")
            logging.error(traceback.format_exc())

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            logging.info(f"File created: {event.src_path}")
            self.schedule_sync()

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            logging.info(f"File modified: {event.src_path}")
            self.schedule_sync()

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            logging.info(f"File deleted: {event.src_path}")
            self.schedule_sync()

    # noinspection PyTypeChecker
    def on_moved(self, event: FileMovedEvent):
        if not event.is_directory:
            logging.info(
                f"File moved/renamed from {event.src_path} to {event.dest_path}"
            )
            self.syncer.handle_rename(event.src_path, event.dest_path)


def main():
    # Use the SYNC_PATHS from the imported configuration
    syncer = DirectorySyncer(SYNC_PATHS)

    logging.info("Performing initial sync...")
    syncer.sync_files()

    observer = Observer()
    handler = ChangeHandler(syncer)

    # Watch all source directories
    watched_paths = set()
    for sync_path in SYNC_PATHS:
        source_path = str(sync_path.source)
        if source_path not in watched_paths and sync_path.source.exists():
            logging.info(f"Watching directory: {source_path}")
            observer.schedule(handler, source_path, recursive=True)
            watched_paths.add(source_path)

    observer.start()
    logging.info("Watching for changes... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
            # Handle any pending syncs
            if handler._sync_scheduled:
                handler._do_sync()
    except KeyboardInterrupt:
        logging.info("\nStopping file watcher...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        logging.error(traceback.format_exc())
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
