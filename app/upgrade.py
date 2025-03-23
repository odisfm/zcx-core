import os
import sys


current_directory = os.getcwd()
parent_directory_name = os.path.basename(current_directory)

sys.path.insert(0, os.path.join(current_directory, 'vendor'))

try:
    import yaml
    import requests

    DEV_MODE = False

    if parent_directory_name == 'app':
        DEV_MODE = True
        print(f'Running in dev environment. Not deleting or creating files.')


except Exception as e:
    print(f'Error: {e}')