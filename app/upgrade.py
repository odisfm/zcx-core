import os
import sys
import shutil
import glob
import datetime
import traceback
import zipfile
import logging
import hashlib

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
    "amxd",
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(script_dir, "vendor"))

    try:
        import yaml
        import requests

        return script_dir, yaml, requests
    except ImportError as e:
        logger.error(f"Failed to import required packages: {e}")
        logger.info(
            f"Please ensure the 'vendor' directory contains the required packages"
        )
        sys.exit(1)


def load_config(script_dir, yaml_module):
    """Load configuration from zcx.yaml"""
    try:
        config_path = os.path.join(script_dir, "zcx.yaml")
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return None, None

        with open(config_path, "r") as f:
            config = yaml_module.safe_load(f)

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


def check_for_updates(version, hardware, requests_module):
    """Check for updates from the repository"""
    try:
        repo_owner = "odisfm"
        repo_name = "zcx-core"
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"

        logger.info(f"Checking for updates...")
        response = requests_module.get(url, timeout=30)

        if response.status_code != 200:
            logger.error(
                f"Error checking for updates: {response.status_code} - {response.text}"
            )
            return None, None, None

        releases = response.json()
        if not releases:
            logger.info("No releases found")
            return None, None, None

        latest_release = releases[0]
        latest_version = latest_release["tag_name"].lstrip("v")

        logger.info(f"Latest release: v{latest_version}, Current version: v{version}")

        if not compare_semver(latest_version, version, consider_prerelease=True):
            logger.info(f"You already have the latest version (v{version})")
            return None, None, None

        logger.info(f"Update available: v{latest_version}")

        # Find the asset for this hardware
        asset_url = None
        asset_name = None

        for asset in latest_release.get("assets", []):
            asset_name = asset["name"]
            parse_name = asset_name.lstrip("_zcx_").rstrip(".zip")
            if parse_name == hardware:
                asset_url = asset["browser_download_url"]
                break

        if not asset_url:
            logger.error(f"No release found for hardware: {hardware}")
            return None, None, None

        return latest_version, asset_url, asset_name

    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return None, None, None


def compare_semver(version1, version2, consider_prerelease=False):
    """
    Compare two semantic version strings for precedence.
    Returns True if version1 > version2, False otherwise.
    """

    def parse_version(version_str):
        prerelease = None
        if "-" in version_str:
            version_str, prerelease = version_str.split("-", 1)

        version_nums = [int(x) for x in version_str.split(".")]
        prerelease_precedence = {None: 3, "rc": 2, "beta": 1, "alpha": 0}

        return version_nums, prerelease, prerelease_precedence.get(prerelease, -1)

    v1_nums, v1_prerelease, v1_pre_value = parse_version(version1)
    v2_nums, v2_prerelease, v2_pre_value = parse_version(version2)

    # Compare version numbers
    for i in range(max(len(v1_nums), len(v2_nums))):
        v1_num = v1_nums[i] if i < len(v1_nums) else 0
        v2_num = v2_nums[i] if i < len(v2_nums) else 0

        if v1_num > v2_num:
            return True
        elif v1_num < v2_num:
            return False

    # Fix: Only compare prerelease values if version numbers are equal
    if consider_prerelease:
        return v1_pre_value > v2_pre_value
    else:
        # If not considering prerelease, stable is better
        return v1_prerelease is None and v2_prerelease is not None


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
                if os.path.isdir(item_path):
                    shutil.copytree(item_path, dst_path)
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

        logger.info(f"Backup completed to: {backup_dir}")
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

            # Skip temp directory and this script
            if item_path == temp_dir or item == this_script or item == "update_log.txt":
                continue

            # Check for protected extensions before deleting
            extension = os.path.splitext(item)[1].lstrip(".")
            if extension in PROTECTED_EXTENSIONS:
                logger.warning(f"Skipping protected file: {item}")
                continue

            try:
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

            # Check for protected extensions
            extension = os.path.splitext(item)[1].lstrip(".")
            if extension in PROTECTED_EXTENSIONS:
                logger.warning(f"Skipping protected file type: {item}")
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


def main():
    """Main function orchestrating the update process"""
    try:
        logger.info("\n\nWelcome to the ZCX Updater!")

        # Check if running in dev environment
        cwd = os.getcwd()
        parent_directory_name = os.path.basename(cwd)
        if parent_directory_name == "app":
            logger.error("Running in dev environment! Aborting!")
            return 1

        # Setup environment and load dependencies
        script_dir, yaml, requests = setup_environment()

        # Load configuration
        hardware, current_version = load_config(script_dir, yaml)
        if not hardware or not current_version:
            logger.error("Failed to load configuration")
            return 1

        logger.info(
            f"Current configuration - Hardware: {hardware}, Version: {current_version}"
        )

        # Check for updates
        latest_version, asset_url, asset_name = check_for_updates(
            current_version, hardware, requests
        )
        if not latest_version or not asset_url:
            logger.info("No update available or update check failed")
            return 0

        # Confirm update with user
        logger.info(f"Update available: v{current_version} -> v{latest_version}")
        logger.info(f"Update package: {asset_name}")
        user_confirm = input(
            "\nDo you want to update? This will backup your current installation. (y/n): "
        )
        if user_confirm.lower() != "y":
            logger.info("Update cancelled by user")
            return 0

        # Create backup
        backup_dir = create_backup(script_dir)
        if not backup_dir:
            logger.error("Backup failed, aborting update")
            return 1

        # Preserve user data
        temp_dir, preserved_items = preserve_user_data(script_dir)
        if not temp_dir:
            logger.error("Failed to preserve user data, aborting update")
            return 1

        # Clean installation directory
        if not clean_installation_directory(script_dir, temp_dir):
            logger.error("Failed to clean installation directory, aborting update")
            return 1

        # Download and extract update package
        download_dir = download_and_verify_asset(
            asset_url, asset_name, script_dir, requests
        )
        if not download_dir:
            logger.error("Failed to download update package, aborting update")
            return 1

        # Extract update package
        if not extract_asset(download_dir, asset_name):
            logger.error("Failed to extract update package, aborting update")
            return 1

        # Find core directory
        core_dir = find_core_directory(download_dir)
        if not core_dir:
            logger.error("Failed to find core directory, aborting update")
            return 1

        # Prepare core directory
        if not prepare_core_directory(core_dir):
            logger.error("Failed to prepare core directory, aborting update")
            return 1

        # Install update
        if not install_update(core_dir, script_dir):
            logger.error("Failed to install update files, aborting update")
            return 1

        # Restore user data
        if not restore_user_data(temp_dir, script_dir):
            logger.warning("Issues restoring user data, update may be incomplete")

        # Clean up temporary directories
        cleanup_temp_dirs(script_dir)

        logger.info(
            f"\nUpdate successfully completed! Version: v{current_version} -> v{latest_version}"
        )
        logger.info(f"Backup location: {backup_dir}")

        return 0

    except KeyboardInterrupt:
        logger.info("\nUpdate cancelled by user")
        return 0
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Unexpected error during update: {e}")
        logger.error(f'\nzcx auto upgrade failed. \n\nVisit https://www.zcxcore.com/lessons/upgrade')
        return 1


if __name__ == "__main__":
    sys.exit(main())
