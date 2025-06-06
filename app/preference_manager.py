import copy
import os

from .consts import DEFAULT_CONFIG_DIR
from .vendor.yaml import safe_load


class PreferenceManager:

    def __init__(self, logger):
        self._logger = logger.getChild("PreferenceManager")
        self._logger.debug(f"PreferenceManager initialized")
        self.this_dir = os.path.dirname(__file__)
        # self._logger.error(f'this_dir: {self.this_dir}')
        try:
            self.__default_prefs = self.load_yaml("default_preferences.yaml")
            self.__user_prefs = self.load_yaml(f"_global_preferences.yaml")
        except Exception as e:
            self._logger.error(
                f"Failed to load preferences.yaml:", {e}
            )  # todo: handle separately
            raise e

        specs = self.load_yaml("hardware/specs.yaml")
        hardware_prefs = specs.get("preferences", {})

        hw_default = self.deep_merge(self.__default_prefs, hardware_prefs)

        user_hw = self.deep_merge(hw_default, self.__user_prefs)

        self.__flattened_prefs = user_hw

        self.__first_cs = list(control_surfaces)[0]

        self.__config_dir = self.evaluate_config_dir()

        try:
            config_override_prefs = self.load_yaml(
                f"{self.__config_dir}/preferences.yaml"
            )
            self.__flattened_prefs = self.deep_merge(
                self.__flattened_prefs, config_override_prefs
            )
        except FileNotFoundError:
            pass

        self.log(f"Configuration dir: {self.__config_dir}", level="debug")

    def log(self, *msg, level="info"):
        method = getattr(self._logger, level)
        for m in msg:
            method(m)

    @property
    def user_prefs(self):
        return copy.deepcopy(self.__flattened_prefs)

    @property
    def config_dir(self):
        return self.__config_dir

    def load_yaml(self, path):
        if not path.endswith(".yaml"):
            raise ValueError("path must end with .yaml")

        full_path = os.path.join(self.this_dir, path)

        with open(full_path, "r") as f:
            obj = safe_load(f)

        return obj

    def deep_merge(self, dict1, dict2):
        """
        Recursively merge two dictionaries.
        If both dicts have the same key and the values are dictionaries, merge those dictionaries.
        If there's a conflict with non-dictionary values, use the value from dict2.
        Keys in dict1 that are not in dict2 are preserved.

        Args:
            dict1: First dictionary (base dictionary)
            dict2: Second dictionary, takes precedence in conflicts

        Returns:
            A new dictionary with merged values
        """
        if dict1 is None:
            dict1 = {}
        if dict2 is None:
            dict2 = {}

        result = dict1.copy()

        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def find_song(self):
        """
        Hacky way to get a reference to the Application.Song object before the ZcxCore object is created.
        This lets us see the name of the set and load a particular config accordingly.

        :return:
        """

        cs_list = list(control_surfaces)

        if len(cs_list) == 0:
            raise RuntimeError(
                "No control surfaces found above this one.\n"
                "ClyphX Pro MUST be enabled in a control surface script above this one."
            )

        def find_song_in_script(script):
            try:
                song_method = getattr(script, "song", None)
                if song_method is None:
                    return None
                try:
                    song = song_method()
                    return song
                except Exception as e:
                    return None
            except:
                return None

        for cs in cs_list:
            song = find_song_in_script(cs)
            if song is not None:
                return song

        return None

    def evaluate_config_dir(self):
        song = self.find_song()

        self.log(f"the song is called `{song.name}`")

        config_pattern_list = self.user_prefs.get("configs", [])

        if config_pattern_list is None:
            config_pattern_list = []

        for config_pattern in config_pattern_list:
            pattern_str = config_pattern.get("pattern", "")
            config_name = config_pattern.get("config", "")

            # Skip if pattern or config is missing
            if not pattern_str or not config_name:
                self.log(f"Skipping invalid config pattern: {config_pattern}")
                continue

            # Check if the pattern matches the song name using regex
            import re

            if re.search(pattern_str, song.name):
                self.log(
                    f'Found matching config "{config_name}" for song "{song.name}"'
                )
                config_dir = f"{DEFAULT_CONFIG_DIR}_{config_name}"

                # Check if the directory exists
                full_path = os.path.join(self.this_dir, config_dir)
                if os.path.isdir(full_path):
                    return config_dir
                else:
                    self.log(
                        f"Config directory {full_path} does not exist, attempting to load general config (`/{DEFAULT_CONFIG_DIR}`)",
                        level="error",
                    )

        # If no match is found or matched directory doesn't exist, check default config directory
        default_full_path = os.path.join(self.this_dir, DEFAULT_CONFIG_DIR)

        if os.path.isdir(default_full_path):
            self.log(f"Using default config directory: {DEFAULT_CONFIG_DIR}")
            return DEFAULT_CONFIG_DIR
        else:
            error_msg = f"Default config directory {default_full_path} does not exist"
            self.log(error_msg, level="error")
            raise RuntimeError(error_msg)

    def get_plugin_config(self, plugin_name):
        plugin_configs = self.user_prefs.get("plugins", {})
        return copy.copy(plugin_configs.get(plugin_name))
