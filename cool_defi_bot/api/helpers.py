"""
Functions helping execution of the main functions.
Miha Lotric, Dec 2019
"""
import requests
from math import floor, log10
from cool_defi_bot.api.custom_exceptions import *


def to_metric_prefix(num, sig=4):
    """Turn thousands in their equivalent metric(SI) prefixes and return the result.
    Args:
        num [float]: Number to which prefix will be added.
    Returns:
        str: Requested number with SI prefixes.
    """
    prefixes = ['', 'K', 'M', 'B']
    power = floor(log10(num)) if num != 0 else 0
    # Currently numbers between 1(included) and trillion(excluded) are accepted
    if (power >= 12) or (power < 0):
        x = 'e' if power < -3 else 'f'
        return f"{round_sig(num, sig=sig):.{sig-1}{x}}"
    thousands = floor(power/3)
    num_front = num * 10 ** (-3 * thousands)
    prefix = prefixes[thousands]
    # Two digits if number's power is in thousands (1.2k instead of 1k)
    num_front = round(num_front, 1) if (power % 3 == 0) else round(num_front)
    num_front = int(num_front) if int(num_front) == num_front else num_front

    return str(num_front) + prefix


def to_emoji(num):
    """Return an emoji corresponding to the percentage of annualized returns
    Args:
        num [float]: Number for which emoji is requested.
    Return:
        str: Emoji.
    """
    if num > 15:
        return '🤑'
    elif num > 5:
        return '🤩'
    elif num > 0:
        return '🙂'
    elif num < -25:
        return '😱'
    elif num < -10:
        return '😨'
    elif num <= 0:
        return '🙃'


def could_float(value):
    """Return if string is a number."""
    try:
        float(value)
        return 1
    except ValueError:
        return 0


def round_sig(x, sig=4):
    """Return value rounded to specified significant figure"""
    rounded = round(x, sig - floor(log10(abs(x))) - 1)
    rounded = int(rounded) if float(rounded).is_integer() else rounded  # 1.0 --> 1
    return rounded


def api_call(url, params=None):
    """Make an API call and return response."""
    try:
        return requests.get(url, params).json()
    except:
        raise APIError('<b>API Unavailable</b>\nPlease try again later')

