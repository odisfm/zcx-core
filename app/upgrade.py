import datetime
import glob
import importlib
import logging
import os
import shutil
import sys
import traceback
import zipfile

HELP_URL = "https://www.zcxcore.com/help"

# Protected file extensions that should never be deleted
PROTECTED_EXTENSIONS = [
    "wav",
    "aiff",
    "mp3",
    "ogg",
    "flac",
    "als",
    "asd",
    "ablbundle",
    "abl",
    "adg",
    "agr",
    "adv",
    "alc",
    "alp",
    "ams",
    "amxd",
    "ask",
]

PURPLE = "\033[35m"
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "update_log.txt")
        ),
    ],
)
logger = logging.getLogger("zcx_updater")


def setup_environment():
    """Setup the environment and add vendor packages to path"""
    try:
        globals()["yaml"] = importlib.import_module("yaml")
        globals()["requests"] = importlib.import_module("requests")
        globals()["semver"] = importlib.import_module("semver")

    except ImportError as e:
        logger.error(f"Failed to import required packages: {e}")
        logger.info(
            f"Please ensure the 'vendor' directory contains the required packages"
        )
        sys.exit(1)


def load_config(script_dir):
    """Load configuration from zcx.yaml"""
    try:
        config_path = os.path.join(script_dir, "zcx.yaml")
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return None, None

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        hardware = config.get("hardware")
        version = config.get("version")

        if not hardware or not version:
            logger.warning(f"Missing hardware or version in configuration")
            if not hardware:
                hardware = input(
                    f"Hardware not found in `zcx.yaml`. Enter hardware name: "
                )

        return hardware, version
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None, None


def is_prerelease(version):
    """Check if a version is a prerelease version (alpha, beta, rc)"""
    return any(x in version for x in ["-alpha", "-beta", "-rc"])


def check_for_updates(version, hardware, include_prereleases=False):
    """Check for updates from the repository"""
    try:
        repo_owner = "odisfm"
        repo_name = "zcx-core"
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"

        logger.info(f"Checking for updates...")
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            logger.error(
                f"Error checking for updates: {response.status_code} - {response.text}"
            )
            return None, None, None, None, None

        releases = response.json()
        if not releases:
            logger.info("No releases found")
            return None, None, None, None, None

        # Filter releases based on prerelease preference
        eligible_releases = []
        for release in releases:
            release_is_prerelease = release["prerelease"]

            if not include_prereleases and release_is_prerelease:
                logger.info(f"Skipping prerelease version: {release['tag_name']}")
                continue

            eligible_releases.append(release)

        if not eligible_releases:
            logger.info("No eligible releases found based on your preferences")
            return None, None, None, None, None

        latest_release = eligible_releases[0]
        latest_version = latest_release["tag_name"].lstrip("v")

        logger.info(
            f"Latest eligible release: v{latest_version}, Current version: v{version}"
        )

        precedence_result = compare_versions(latest_version, version)

        if precedence_result == 0:
            latest_is_upgrade = False
        elif precedence_result == 1:
            latest_is_upgrade = True
        elif precedence_result == -1:
            raise RuntimeError(
                f"You seem to be running a super secret preview version ;)."
            )

        # Find the asset for this hardware
        asset_url = None
        asset_name = None
        html_url = latest_release["html_url"]

        for asset in latest_release.get("assets", []):
            asset_name = asset["name"]
            parse_name = asset_name.lstrip("_zcx_").rstrip(".zip")
            if parse_name == hardware:
                asset_url = asset["browser_download_url"]
                break

        if not asset_url:
            logger.error(f"No release found for hardware: {hardware}")
            return None, None, None, None, None

        return latest_version, asset_url, asset_name, html_url, latest_is_upgrade

    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return None, None, None, None, None


def compare_versions(version1, version2):
    """
    Compare two semantic version strings for precedence.
    """
    return semver.compare(version1, version2)


def create_backup(script_dir):
    """Create a backup of the current installation"""
    try:
        parent_dir = os.path.dirname(script_dir)
        backup_root_dir = os.path.join(parent_dir, "__zcx_backups__")

        # Create the backup root directory if it doesn't exist
        if not os.path.exists(backup_root_dir):
            os.makedirs(backup_root_dir)
            logger.info(f"Created backup root directory: {backup_root_dir}")

        # Generate timestamp for backup folder name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        parent_dir_name = os.path.basename(script_dir)
        backup_dir_name = f"{parent_dir_name}_backup_{timestamp}"
        backup_dir = os.path.join(backup_root_dir, backup_dir_name)

        # Create the timestamped backup directory
        os.makedirs(backup_dir)
        logger.info(f"Created backup directory: {backup_dir}")

        # Copy all contents from script_dir to backup_dir
        for item in os.listdir(script_dir):
            item_path = os.path.join(script_dir, item)
            dst_path = os.path.join(backup_dir, item)

            try:
                if os.path.isdir(item_path) and not os.path.islink(item_path):
                    shutil.copytree(item_path, dst_path)
                else:
                    # For symlinks or regular files, copy as is
                    if os.path.islink(item_path):
                        linkto = os.readlink(item_path)
                        os.symlink(linkto, dst_path)
                    else:
                        shutil.copy2(item_path, dst_path)
            except Exception as e:
                logger.error(f"Failed to backup {item}: {e}")
                raise

        # Verify backup
        if not os.path.exists(backup_dir) or len(os.listdir(backup_dir)) < len(
            os.listdir(script_dir)
        ):
            raise Exception("Backup verification failed")

        logger.info(f"{GREEN}Backup completed to: {backup_dir}{RESET}")
        return backup_dir

    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return None


def preserve_user_data(script_dir):
    """Preserve important user data during update"""
    try:
        temp_dir = os.path.join(script_dir, "__upgrade_temp__")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        os.makedirs(temp_dir)
        logger.info(f"Created temporary directory: {temp_dir}")

        # Items to preserve
        preserved_items = []

        # Preserve global preferences
        global_prefs = os.path.join(script_dir, "_global_preferences.yaml")
        if os.path.exists(global_prefs):
            shutil.copy2(
                global_prefs, os.path.join(temp_dir, "_global_preferences.yaml")
            )
            preserved_items.append("_global_preferences.yaml")

        # Preserve config directories
        config_dirs = glob.glob(os.path.join(script_dir, "_config*"))
        for config_dir in config_dirs:
            if os.path.isdir(config_dir):
                dir_name = os.path.basename(config_dir)
                shutil.copytree(config_dir, os.path.join(temp_dir, dir_name))
                preserved_items.append(dir_name)

        # Preserve plugins directory
        plugins_dir = os.path.join(script_dir, "plugins")
        if os.path.exists(plugins_dir) and os.path.isdir(plugins_dir):
            shutil.copytree(plugins_dir, os.path.join(temp_dir, "plugins"))
            preserved_items.append("plugins")

        if preserved_items:
            logger.info(f"Preserved user data: {', '.join(preserved_items)}")
        else:
            logger.warning("No user data found to preserve")

        return temp_dir, preserved_items

    except Exception as e:
        logger.error(f"Error preserving user data: {e}")
        return None, []


def clean_installation_directory(script_dir, temp_dir):
    """Clean the installation directory keeping only the preserve directory and this script"""
    try:
        this_script = os.path.basename(__file__)
        items_deleted = []

        for item in os.listdir(script_dir):
            item_path = os.path.join(script_dir, item)

            # Skip temp directory and this script and log file
            if item_path == temp_dir or item == this_script or item == "update_log.txt":
                continue

            # Check for protected extensions before deleting
            extension = os.path.splitext(item)[1].lstrip(".")
            if extension in PROTECTED_EXTENSIONS:
                logger.warning(f"Skipping protected file: {item}")
                continue

            try:
                # If the item is a symlink, skip deletion so it can be restored later
                if os.path.islink(item_path):
                    logger.info(f"Preserving symlink: {item_path}")
                    continue

                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                items_deleted.append(item)
            except Exception as e:
                logger.error(f"Error deleting {item}: {e}")
                raise

        logger.info(
            f"Cleaned installation directory, removed {len(items_deleted)} items"
        )
        return True

    except Exception as e:
        logger.error(f"Error cleaning installation directory: {e}")
        return False


def download_and_verify_asset(asset_url, asset_name, script_dir, requests_module):
    """Download and verify an asset"""
    try:
        temp_dir = os.path.join(script_dir, "__temp_new__")

        # Remove directory if it already exists
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        os.makedirs(temp_dir)
        logger.info(f"Created download directory: {temp_dir}")

        # Download the asset
        asset_path = os.path.join(temp_dir, asset_name)
        logger.info(f"Downloading {asset_name}...")

        with requests_module.get(asset_url, stream=True, timeout=60) as response:
            if response.status_code != 200:
                logger.error(
                    f"Download failed with status code: {response.status_code}"
                )
                return None

            with open(asset_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Verify download exists and has size > 0
        if not os.path.exists(asset_path) or os.path.getsize(asset_path) == 0:
            logger.error("Downloaded file is empty or missing")
            return None

        logger.info(
            f"Downloaded {os.path.getsize(asset_path) / (1024*1024):.2f} MB to {asset_path}"
        )

        return temp_dir

    except Exception as e:
        logger.error(f"Error downloading asset: {e}")
        return None


def extract_asset(temp_dir, asset_name):
    """Extract a downloaded asset"""
    try:
        asset_path = os.path.join(temp_dir, asset_name)

        if not asset_name.endswith(".zip"):
            logger.info(f"Asset is not a zip file, skipping extraction")
            return True

        logger.info(f"Extracting {asset_name}...")

        with zipfile.ZipFile(asset_path, "r") as zip_ref:
            # Check for any malicious paths before extracting
            for zip_info in zip_ref.infolist():
                if ".." in zip_info.filename or zip_info.filename.startswith("/"):
                    logger.error(
                        f"Potentially malicious path in zip: {zip_info.filename}"
                    )
                    return False

            zip_ref.extractall(temp_dir)

        logger.info(f"Extraction completed")

        # Remove the zip file after extraction
        os.remove(asset_path)
        logger.info(f"Removed zip file")

        return True

    except Exception as e:
        logger.error(f"Error extracting asset: {e}")
        return False


def find_core_directory(temp_dir):
    """Find the core directory in the extracted files"""
    try:
        core_dir = None

        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and item.startswith("_zcx_"):
                core_dir = item_path
                logger.info(f"Found core directory: {item}")
                break

        if core_dir is None:
            logger.error("Could not find core directory starting with '_zcx_'")
            return None

        return core_dir

    except Exception as e:
        logger.error(f"Error finding core directory: {e}")
        return None


def prepare_core_directory(core_dir):
    """Prepare core directory by removing configuration files"""
    try:
        # Items that should not be copied from the update package
        items_to_delete = ["_config", "_global_preferences.yaml", "plugins"]

        for item in items_to_delete:
            item_path = os.path.join(core_dir, item)

            # Check for protected extensions
            extension = os.path.splitext(item)[1].lstrip(".")
            if extension in PROTECTED_EXTENSIONS:
                logger.error(f"Encountered protected item! {item}")
                return False

            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                logger.info(f"Removed {item} from core directory")

        return True

    except Exception as e:
        logger.error(f"Error preparing core directory: {e}")
        return False


def install_update(core_dir, script_dir):
    """Install update files from core directory to script directory"""
    try:
        items_installed = []

        for item in os.listdir(core_dir):
            src_path = os.path.join(core_dir, item)
            dst_path = os.path.join(script_dir, item)

            # If destination exists and is an existing symlink, keep it (do not override)
            if os.path.exists(dst_path) and os.path.islink(dst_path):
                logger.info(f"Maintaining existing symlink: {dst_path}")
                continue

            # If the source is a symlink, recreate the symlink without copying the target
            if os.path.islink(src_path):
                # Remove any non-symlink file at destination so we can create the symlink
                if os.path.exists(dst_path) and not os.path.islink(dst_path):
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)
                link_target = os.readlink(src_path)
                os.symlink(link_target, dst_path)
                logger.info(f"Installed symlink {item} -> {link_target}")
                items_installed.append(item)
                continue

            try:
                if os.path.isdir(src_path):
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
                items_installed.append(item)
            except Exception as e:
                logger.error(f"Error installing {item}: {e}")
                raise

        logger.info(f"Installed {len(items_installed)} items from update package")
        return True

    except Exception as e:
        logger.error(f"Error installing update: {e}")
        return False


def restore_user_data(temp_dir, script_dir):
    """Restore preserved user data"""
    try:
        if not os.path.exists(temp_dir):
            logger.error("Temporary directory not found for restoration")
            return False

        items_restored = []

        for item in os.listdir(temp_dir):
            src_path = os.path.join(temp_dir, item)
            dst_path = os.path.join(script_dir, item)

            try:
                if os.path.isdir(src_path):
                    # Merge directories if they exist
                    if os.path.exists(dst_path):
                        # For each item in the source directory
                        for sub_item in os.listdir(src_path):
                            sub_src = os.path.join(src_path, sub_item)
                            sub_dst = os.path.join(dst_path, sub_item)

                            if os.path.isdir(sub_src):
                                if os.path.exists(sub_dst):
                                    shutil.rmtree(sub_dst)
                                shutil.copytree(sub_src, sub_dst)
                            else:
                                shutil.copy2(sub_src, sub_dst)
                    else:
                        shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

                items_restored.append(item)
            except Exception as e:
                logger.error(f"Error restoring {item}: {e}")
                continue

        logger.info(f"Restored {len(items_restored)} user data items")
        return True

    except Exception as e:
        logger.error(f"Error restoring user data: {e}")
        return False


def cleanup_temp_dirs(script_dir):
    """Clean up temporary directories"""
    try:
        temp_dirs = ["__temp_new__", "__upgrade_temp__"]
        for dir_name in temp_dirs:
            dir_path = os.path.join(script_dir, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.info(f"Deleted temporary directory: {dir_name}")

        return True

    except Exception as e:
        logger.error(f"Error cleaning up temporary directories: {e}")
        return False


def record_symlinks(root_dir):
    """
    Recursively record all symlinks under the root_dir.
    Returns a dictionary mapping relative paths to their symlink targets.
    """
    symlinks = {}
    for current_root, dirs, files in os.walk(root_dir, topdown=True, followlinks=False):
        for name in dirs + files:
            full_path = os.path.join(current_root, name)
            if os.path.islink(full_path):
                rel_path = os.path.relpath(full_path, root_dir)
                try:
                    target = os.readlink(full_path)
                    symlinks[rel_path] = target
                    logger.info(f"Recorded symlink: {rel_path} -> {target}")
                except Exception as e:
                    logger.error(f"Failed to read symlink {full_path}: {e}")
    return symlinks


def restore_symlinks(root_dir, symlink_map):
    """
    Restore symlinks from the recorded mapping.
    For each recorded symlink, if a file or folder exists at that path and is not a symlink,
    it is removed and the symlink is re-created.
    """
    for rel_path, target in symlink_map.items():
        full_path = os.path.join(root_dir, rel_path)
        # Remove conflicting file/directory if it exists and is not a symlink
        if os.path.exists(full_path) and not os.path.islink(full_path):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                logger.info(f"Removed conflicting item at {full_path}")
            except Exception as e:
                logger.error(f"Failed to remove {full_path}: {e}")
                continue
        # (Re)create the symlink if it does not exist
        if not os.path.exists(full_path):
            try:
                os.symlink(target, full_path)
                logger.info(f"Restored symlink: {full_path} -> {target}")
            except Exception as e:
                logger.error(f"Failed to restore symlink {full_path}: {e}")


def main():
    """Main function orchestrating the update process"""
    try:
        logger.info("\n\nWelcome to the ZCX Updater!")

        backup_dir = None

        # Check if running in dev environment
        cwd = os.getcwd()
        parent_directory_name = os.path.basename(cwd)
        if parent_directory_name == "app":
            raise RuntimeError("Running in dev environment! Aborting!")

        # Setup environment and load dependencies
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(script_dir, "vendor"))
        setup_environment()

        # Load configuration
        hardware, current_version = load_config(script_dir)
        if not hardware or not current_version:
            raise RuntimeError("Failed to load configuration")

        logger.info(
            f"Current configuration - Hardware: {hardware}, Version: {current_version}"
        )

        existing_symlinks = record_symlinks(script_dir)

        if os.name == "nt" and existing_symlinks:
            logger.error(f"\n{RED}Detected {len(existing_symlinks)} symlinks.{RESET}")
            logger.error(
                f"{RED}This script will not work on Windows where symlinks are present.{RESET}"
            )

            print("\nSymlinks detected in your installation:")
            for rel_path, target in existing_symlinks.items():
                print(f" - {rel_path} -> {target}")

            print(
                f"{PURPLE}To proceed with the automated upgrade, delete all symlinks and recreate them after script completion.{RESET}"
            )
            print(f"{PURPLE}Visit {HELP_URL} for assistance.{RESET}")

            sys.exit(1)

        # Ask user about prerelease preference
        include_prereleases = (
            input("\nCheck for preview versions? (y/N): ").lower() == "y"
        )
        if include_prereleases:
            logger.info("Including preview versions in update check")

        # Check for updates with user's prerelease preference
        latest_version, asset_url, asset_name, html_url, latest_is_upgrade = (
            check_for_updates(current_version, hardware, include_prereleases)
        )

        latest_ver_obj = semver.Version.parse(latest_version)
        current_ver_obj = semver.Version.parse(current_version)
        dummy_current_version = (
            current_ver_obj.major == 0
            and current_ver_obj.minor == 0
            and current_ver_obj.patch == 0
        )

        if dummy_current_version:
            pass
        elif current_ver_obj.major == latest_ver_obj.major:
            pass
        elif current_ver_obj.major == 0 and latest_ver_obj.major == 1:
            pass
        else:
            raise RuntimeError(
                f"Too big a jump between versions: (v{current_version} -> v{latest_version})"
            )

        if not latest_version:
            raise RuntimeError(f"Update check failed.")

        elif not latest_is_upgrade:
            version_adj = "version" if not include_prereleases else "preview version"
            logger.info(
                f"{GREEN}You already have the latest {version_adj} ({current_version}).{RESET}\n"
            )

            logger.info(
                f"You may choose to repair this installation by replacing core files with the current release."
            )
            logger.info(f"Your configuration files will not be overwritten.")
            repair = input(f"Type 'repair' to continue: ")
            if repair != "repair":
                logger.info(f"{PURPLE}Get the latest news on Discord!{RESET}")
                logger.info(f"https://discord.zcxcore.com")
                sys.exit(0)
        else:
            # Confirm update with user
            logger.info(
                f"{GREEN}Update available: v{current_version} -> v{latest_version}{RESET}"
            )
            logger.info(f"Update package: {asset_name}")
            pre_v1 = latest_version[0] == "0"
            if pre_v1:
                print(
                    f"{PURPLE}zcx is in active development.{RESET}\n"
                    f"You {RED}must{RESET} check the release notes to see if your config is affected by any breaking changes.\n"
                    f"\n{html_url}{RESET}"
                )
            user_confirm = input(
                "\nDo you want to update? This will backup your current installation. (y/N): "
            )
            if user_confirm.lower() != "y":
                logger.info("Update cancelled by user")
                return 0

        # Create backup
        backup_dir = create_backup(script_dir)
        if not backup_dir:
            raise RuntimeError("Backup failed, aborting update")

        # Preserve user data
        temp_dir, preserved_items = preserve_user_data(script_dir)
        if not temp_dir:
            raise RuntimeError("Failed to preserve user data, aborting update")

        # Clean installation directory
        if not clean_installation_directory(script_dir, temp_dir):
            raise RuntimeError(
                "Failed to clean installation directory, aborting update"
            )

        # Download and extract update package
        download_dir = download_and_verify_asset(
            asset_url, asset_name, script_dir, requests
        )
        if not download_dir:
            raise RuntimeError("Failed to download update package, aborting update")

        # Extract update package
        if not extract_asset(download_dir, asset_name):
            raise RuntimeError("Failed to extract update package, aborting update")

        # Find core directory
        core_dir = find_core_directory(download_dir)
        if not core_dir:
            raise RuntimeError("Failed to find core directory, aborting update")

        # Prepare core directory
        if not prepare_core_directory(core_dir):
            raise RuntimeError("Failed to prepare core directory, aborting update")

        # Install update
        if not install_update(core_dir, script_dir):
            raise RuntimeError("Failed to install update files, aborting update")

        # Restore user data
        if not restore_user_data(temp_dir, script_dir):
            logger.warning("Issues restoring user data, update may be incomplete")

        restore_symlinks(script_dir, existing_symlinks)

        logger.info(
            f"\n{GREEN}Update successfully completed! Version: v{current_version} -> v{latest_version}{RESET}"
        )
        logger.info(f"Backup location: {backup_dir}")

        upgrade_ua = input(
            f"{PURPLE}Install/upgrade the Zcx user action? (Y/n): {RESET}"
        )
        if upgrade_ua.lower() != "n":
            user_actions_source = os.path.join(download_dir, "_user_actions", "Zcx.py")

            parent_dir = os.path.dirname(script_dir)
            parent_dir_name = os.path.basename(parent_dir)

            if parent_dir_name != "Remote Scripts":
                logger.error(f"Parent directory is not 'Remote Scripts': {parent_dir}")
                raise RuntimeError(
                    "Parent directory must be 'Remote Scripts' to install Zcx user action."
                )

            user_actions_target_dir = os.path.join(parent_dir, "_user_actions")

            if not os.path.exists(user_actions_source):
                logger.error(
                    f"Zcx user action file not found in update package: {user_actions_source}"
                )
                raise RuntimeError("Zcx user action file not found in update package")

            if not os.path.exists(user_actions_target_dir):
                logger.error(
                    f"_user_actions directory does not exist: {user_actions_target_dir}"
                )
                raise RuntimeError(
                    "_user_actions directory does not exist. Cannot install Zcx user action."
                )

            target_file = os.path.join(user_actions_target_dir, "Zcx.py")
            try:
                shutil.copy2(user_actions_source, target_file)
                logger.info(f"Successfully installed Zcx user action to: {target_file}")
            except Exception as e:
                logger.error(f"Failed to copy Zcx user action: {e}")
                raise RuntimeError("Failed to install Zcx user action")

        new_upgrade_path = os.path.join(core_dir, "upgrade.py")

        if os.path.exists(new_upgrade_path):
            current_path = os.path.abspath(__file__)
            temp_path = current_path + ".tmp"

            # Copy new version to temp file
            shutil.copy2(new_upgrade_path, temp_path)

            # On Windows, we need to delay the replacement
            if os.name == "nt":
                import atexit
                import tempfile

                # Create a batch script to do the replacement
                batch_script = f"""
                        @echo off
                        timeout /t 1 /nobreak >nul
                        move /Y "{temp_path}" "{current_path}"
                        del "%~f0"
                        """

                batch_path = os.path.join(tempfile.gettempdir(), "replace_upgrade.bat")
                with open(batch_path, "w") as f:
                    f.write(batch_script)

                # Schedule the batch script to run after we exit
                os.startfile(batch_path)
            else:
                # On Unix-like systems, we can do it directly
                os.replace(temp_path, current_path)

            # Clean up temporary directories
            cleanup_temp_dirs(script_dir)

        else:
            raise RuntimeError(f'Upgrade did not contain a new "upgrade.py".')

        return 0

    except KeyboardInterrupt:
        logger.error(f"Upgrade cancelled by user.")
        logger.error(f"For help, see: https://www.zcxcore.com/lessons/upgrade")

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Unexpected error during update: {e}")
        logger.error(
            f"\nzcx auto upgrade failed. \n\nVisit https://www.zcxcore.com/lessons/upgrade\nGet help in the Discord https://discord.zcxcore.com"
        )
        if "backup_dir" in locals() and backup_dir is not None:
            logger.info(f"Backup location: {backup_dir}")


if __name__ == "__main__":
    sys.exit(main())
