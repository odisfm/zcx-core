from .consts import SEND_LETTERS

class DynamicString(str):
    def __new__(cls, *args, **kwargs):
        obj = str.__new__(cls, "")
        obj._value_func = lambda: ""
        return obj

    def __str__(self):
        return self._value_func()

    def __repr__(self):
        return repr(self._value_func())

    def __format__(self, format_spec):
        return format(self._value_func(), format_spec)

    def __len__(self):
        return len(self._value_func())


def to_percentage(min_val: float, max_val: float, actual: float) -> float:
    if min_val == max_val:
        raise ValueError("min_val and max_val cannot be equal")

    percentage = ((actual - min_val) / (max_val - min_val)) * 100
    percentage = max(0.0, min(100.0, percentage))

    return round(percentage, 1)

def is_chain_map_positional(chain_map: list[str]) -> bool:
    for node in chain_map:
        if node in ["first", "last", "sel"]:
            return True
        else:
            if node.isdigit():
                return True

    return False

sends_count = len(SEND_LETTERS)
def number_to_send_letter(number: int) -> str:
    return SEND_LETTERS[number % sends_count]
