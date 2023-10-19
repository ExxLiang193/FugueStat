from typing import List


def format_array(array: List[int], r_padding: int = 4) -> str:
    return "".join(["{value:>{width}} ".format(value=str(value), width=r_padding) for value in array])
