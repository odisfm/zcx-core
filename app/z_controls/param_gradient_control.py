from .param_control import ParamControl, ColorRecommendation
from ..colors import parse_color_definition, RgbColor, PARAM_GRADIENT
from ..errors import ConfigurationError, CriticalConfigurationError, NumberedDeviceMissingError
from ..util import to_percentage


class ParamGradientControl(ParamControl):

    def __init__(self, *args, **kwargs):
        ParamControl.__init__(self, *args, **kwargs)
        self.__continuous_gradient = []
        self.__quantized_gradient = []
        self.__color_cache = {}

    @property
    def continuous_gradient(self):
        return self.__continuous_gradient

    @property
    def quantized_gradient(self):
        return self.__quantized_gradient

    def setup(self):
        super().setup()
        cont_gradient_def = self._raw_config.get("gradient", None)
        if cont_gradient_def is not None:
            cont_gradient_colors = []
            if not isinstance(cont_gradient_def, list):
                self.error(f"Option `gradient` must be a list. Using default.")
            try:
                for color_def in cont_gradient_def:
                    cont_gradient_colors.append(parse_color_definition(color_def, self))
            except Exception as e:
                self.error(f"Error while parsing `gradient`: {e.__class__.__name__}: {e}")
                self.error(f"Using default gradient.")

            self.__continuous_gradient = cont_gradient_colors

        if not self.__continuous_gradient:
            self.__continuous_gradient = PARAM_GRADIENT

    def _do_update_feedback(self):
        color_rec = self.recommend_color()
        if color_rec.disabled:
            self.replace_color(self._color_dict["disabled"])
        elif color_rec.percent is not None:
            param_value = self._mapped_parameter.value
            gradient_len = len(self.__continuous_gradient)
            quantized_idx = self.quantize_to_index(color_rec.percent, gradient_len)
            reversed_idx = (gradient_len - 1) - quantized_idx
            self.replace_color(self.__continuous_gradient[reversed_idx])
        elif color_rec.recommended is not None:
            if color_rec.recommended in self.__color_cache:
                self.replace_color(self.__color_cache[color_rec.recommended])
            else:
                color = parse_color_definition(color_rec.recommended, self)
                self.__color_cache[color_rec.recommended] = color
                self.replace_color(self.__color_cache[color_rec.recommended])
        elif color_rec.binary is not None:
            if color_rec.binary:
                self.replace_color(self._color_dict["on"])
            else:
                self.replace_color(self._color_dict["off"])

        else:
            raise RuntimeError(f"Failed to set color")

    def quantize_to_index(self, value: float, length: int) -> int:
        """Map a float [0.0, 100.0] to an array index [0, length-1]."""
        return min(int(value / 100.0 * length), length - 1)


    def set_feedback(self, status: bool):
        ...
