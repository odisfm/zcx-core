import os
import sys
import shutil
import glob
import datetime
import zipfile

HELP_URL = f'https://www.zcxcore.com/help'

# you can never be too careful
PROTECTED_EXTENSIONS = [
    'wav',
    'aiff',
    'mp3',
    'ogg',
    'flac',
    'als',
    'asd',
    'amxd',
    'ablbundle',
    'abl',
    'adg',
    'agr',
    'adv',
    'alc',
    'alp',
    'ams',
    'amxd',
    'ask'
]

cwd = os.getcwd()
parent_directory_name = os.path.basename(cwd)

script_dir = os.path.dirname(os.path.abspath(__file__))

# print(f'Script directory: {script_dir}')
# raise NotImplementedError()

sys.path.insert(0, os.path.join(script_dir, 'vendor'))

import yaml
import requests


def download_and_extract_asset(asset_url, asset_name):
    """Download and extract a zip asset to __temp_new__ folder"""
    # Create __temp_new__ folder in script_dir
    temp_dir = os.path.join(script_dir, "__temp_new__")

    # Remove directory if it already exists
    if os.path.exists(temp_dir):
        print(f"Removing existing {temp_dir} directory...")
        shutil.rmtree(temp_dir)

    # Create the directory
    os.makedirs(temp_dir)
    print(f"Created directory: {temp_dir}")

    # Download the asset
    print(f"Downloading {asset_name}...")
    asset_path = os.path.join(temp_dir, asset_name)

    response = requests.get(asset_url, stream=True)

    if response.status_code == 200:
        with open(asset_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded to {asset_path}")

        # Extract if it's a zip file
        if asset_name.endswith('.zip'):
            print(f"Extracting {asset_name}...")
            with zipfile.ZipFile(asset_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            print(f"Extracted to {temp_dir}")

            # Optionally remove the zip file after extraction
            os.remove(asset_path)
            print(f"Removed zip file {asset_path}")

        return True
    else:
        print(f"Error downloading asset: {response.status_code}")
        return False


def compare_semver(version1, version2, consider_prerelease=False):
    """
    Compare two semantic version strings for precedence.
    Returns True if version1 > version2, False otherwise.

    Args:
        version1 (str): First version string to compare
        version2 (str): Second version string to compare
        consider_prerelease (bool): If True, higher prerelease versions
                                       are considered better than lower ones

    Example:
        compare_semver("1.2.3", "1.2.2")  # Returns True
        compare_semver("1.2.3-beta", "1.2.3")  # Returns False
        compare_semver("1.2.3-beta", "1.2.3-alpha")  # Returns True
    """

    def parse_version(version_str):
        prerelease = None
        if '-' in version_str:
            version_str, prerelease = version_str.split('-', 1)

        version_nums = [int(x) for x in version_str.split('.')]

        prerelease_precedence = {None: 3, 'rc': 2, 'beta': 1, 'alpha': 0}

        return version_nums, prerelease, prerelease_precedence.get(prerelease, -1)

    v1_nums, v1_prerelease, v1_pre_value = parse_version(version1)
    v2_nums, v2_prerelease, v2_pre_value = parse_version(version2)

    for i in range(max(len(v1_nums), len(v2_nums))):
        v1_num = v1_nums[i] if i < len(v1_nums) else 0
        v2_num = v2_nums[i] if i < len(v2_nums) else 0

        if v1_num > v2_num:
            return True
        elif v1_num < v2_num:
            return False

    if consider_prerelease:
        return v1_pre_value > v2_pre_value
    else:
        return v1_pre_value > v2_pre_value


def main():
    print(f'\n\nWelcome to the zcx updater!\n')

    try:
        if parent_directory_name == 'app':
            print(f'Running in dev environment!!! Aborting!!!')
            sys.exit(1)

        def load_yaml(path):
            full_path = os.path.join(script_dir, path)
            with open(full_path, 'r') as f:
                obj = yaml.safe_load(f)
            return obj

        zcx_spec = load_yaml('zcx.yaml')
        this_hardware = zcx_spec['hardware']
        this_version = zcx_spec['version']

        print(f'zcx spec: {zcx_spec}')

        repo_owner = "odisfm"
        repo_name = "zcx-core"
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"

        response = requests.get(url)

        if response.status_code == 200:
            releases = response.json()

            release = releases[0]

            release_str = release['tag_name'].lstrip('v')

            # print(f'Latest release: v{release_str}')

            release_newer = compare_semver(release_str, this_version, consider_prerelease=True)

            if release_newer:
                print(f'Latest release (v{release_str}) newer than current version (v{this_version}).')
            else:
                print(f'Latest release is v{release_str}. You already have v{this_version}')
                print(f'No updates available.')
                print(f'Exiting...\n')
                sys.exit(0)

            assets = release.get('assets', [])

            if this_hardware is None:
                this_hardware = input(f'Could not identify hardware from `zcx.yaml`. Enter hardware name to get: ')

            asset_url = None
            asset_name = None

            for asset in assets:
                asset_name = asset['name']
                parse_name = asset_name.lstrip('_zcx_').rstrip('.zip')
                if parse_name == this_hardware:
                    asset_url = asset['browser_download_url']
                    break

            if asset_url is None:
                raise RuntimeError(f'No valid release found for hardware `{this_hardware}`.\nGo to {HELP_URL}')

        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            sys.exit(1)

        print(f'Found asset: {asset_url}')
        if input('Continue? (y/n): ') != 'y':
            sys.exit(0)

        # Create backup directory one level up from script_dir
        parent_dir = os.path.dirname(script_dir)
        backup_root_dir = os.path.join(parent_dir, "__zcx_backups__")

        # Create the backup root directory if it doesn't exist
        if not os.path.exists(backup_root_dir):
            os.makedirs(backup_root_dir)
            print(f"Created backup root directory: {backup_root_dir}")

        # Generate timestamp for backup folder name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        parent_dir_name = os.path.basename(script_dir)
        backup_dir_name = f"{parent_dir_name}_backup_{timestamp}"
        backup_dir = os.path.join(backup_root_dir, backup_dir_name)

        # Create the timestamped backup directory
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")

        # Copy all contents from script_dir to backup_dir
        for item in os.listdir(script_dir):
            item_path = os.path.join(script_dir, item)
            if os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(backup_dir, item))
                print(f"Backed up directory: {item}")
            else:
                shutil.copy2(item_path, os.path.join(backup_dir, item))
                print(f"Backed up file: {item}")

        print(f"Full backup completed to: {backup_dir}")

        # sys.exit(0)

        # Create temp folder for user data preservation
        temp_dir = os.path.join(script_dir, "__upgrade_temp__")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print(f"Created temporary directory: {temp_dir}")

        # Find and move _global_preferences.yaml
        global_prefs = os.path.join(script_dir, "_global_preferences.yaml")
        if os.path.exists(global_prefs):
            shutil.move(global_prefs, os.path.join(temp_dir, "_global_preferences.yaml"))
            print(f"Moved: _global_preferences.yaml to {temp_dir}")
        else:
            print("Warning: _global_preferences.yaml not found")

        # Find and move all _config* directories
        config_dirs = glob.glob(os.path.join(script_dir, "_config*"))
        for config_dir in config_dirs:
            if os.path.isdir(config_dir):
                dir_name = os.path.basename(config_dir)
                shutil.move(config_dir, os.path.join(temp_dir, dir_name))
                print(f"Moved directory: {dir_name} to {temp_dir}")

        # Find and preserve plugins directory
        plugins_dir = os.path.join(script_dir, "plugins")
        if os.path.exists(plugins_dir) and os.path.isdir(plugins_dir):
            shutil.move(plugins_dir, os.path.join(temp_dir, "plugins"))
            print(f"Moved directory: plugins to {temp_dir}")
        else:
            print("Warning: plugins directory not found")

        # Get list of all items in cwd before deletion
        items_to_delete = []
        for item in os.listdir(script_dir):
            item_path = os.path.join(script_dir, item)
            # Skip the temp directory we just created
            if item_path != temp_dir:
                items_to_delete.append(item_path)

        # Delete everything except the temp directory and this script
        for item_path in items_to_delete:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"Deleted directory: {os.path.basename(item_path)}")
                else:
                    os.remove(item_path)
                    print(f"Deleted file: {os.path.basename(item_path)}")
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

        download_and_extract_asset(asset_url, asset_name)

        # Identify the 'core' folder in __temp_new__
        temp_new_dir = os.path.join(script_dir, "__temp_new__")
        core_dir = None

        for item in os.listdir(temp_new_dir):
            item_path = os.path.join(temp_new_dir, item)
            if os.path.isdir(item_path) and item.startswith('_zcx_'):
                core_dir = item_path
                print(f"Found core directory: {item}")
                break

        if core_dir is None:
            raise RuntimeError("Could not find core directory starting with '_zcx_' in the extracted files")

        # Delete specified files/folders from core_dir
        items_to_delete = ['_config', '_global_preferences.yaml', 'plugins']
        for item in items_to_delete:
            file_extension = os.path.splitext(item)[1]
            if file_extension in PROTECTED_EXTENSIONS:
                raise RuntimeError(f'Encountered protected item! {item}')

            item_path = os.path.join(core_dir, item)
            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"Deleted directory from core: {item}")
                else:
                    os.remove(item_path)
                    print(f"Deleted file from core: {item}")

        # Move contents of core to script_dir
        for item in os.listdir(core_dir):
            src_path = os.path.join(core_dir, item)
            dst_path = os.path.join(script_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
                print(f"Moved directory to script_dir: {item}")
            else:
                shutil.copy2(src_path, dst_path)
                print(f"Moved file to script_dir: {item}")

        # Move preserved files/directories back from temp_dir
        for item in os.listdir(temp_dir):

            src_path = os.path.join(temp_dir, item)
            dst_path = os.path.join(script_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
                print(f"Restored directory: {item}")
            else:
                shutil.copy2(src_path, dst_path)
                print(f"Restored file: {item}")

        # Delete temp directories
        temp_dirs = ['__temp_new__', '__upgrade_temp__']
        for dir_name in temp_dirs:
            dir_path = os.path.join(script_dir, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"Deleted temporary directory: {dir_name}")

        print("\nUpdate complete!")

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f'Error: {e}')

main()
