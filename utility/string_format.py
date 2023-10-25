from typing import List


def format_array(array: List[int], r_padding: int = 4) -> str:
    def format_value(value):
        return str(value if value is None else round(value, 2))

    return "".join(["{value:>{width}} ".format(value=format_value(value), width=r_padding) for value in array])
