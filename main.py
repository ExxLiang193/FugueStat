import argparse
from time import time
from decimal import getcontext, FloatOperation


def enable_safe_float_handling():
    c = getcontext()
    c.traps[FloatOperation] = True


def parse_args():
    parser = argparse.ArgumentParser(description="Generates statistics for fugue")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    enable_safe_float_handling()
    t0 = time()
    print("Solutions generated in: {} sec".format(round(time() - t0, 5)))
