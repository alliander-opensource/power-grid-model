# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import math
import re
from typing import Optional, Tuple, TypeVar

import numpy as np

from ..enum import WindingType

CONNECTION_PATTERN = re.compile(r"(Y|YN|D|Z|ZN)(y|yn|d|z|zn)([0-9]|1[0-2])")

# TODO: Implement Z winding
WINDING_TYPES = {
    "Y": WindingType.wye,
    "YN": WindingType.wye_n,
    "D": WindingType.delta,
    "Z": WindingType.wye,
    "ZN": WindingType.wye_n,
}

T = TypeVar("T")


def relative_no_load_current(i0: float, p0: float, sn: float, un: float) -> float:
    return i0 / (sn / un / math.sqrt(3)) if i0 > p0 / sn else p0 / sn


def multiply(*args: float):
    return math.prod(args)


def value_or_default(value: Optional[T], default: T) -> T:
    return value if value is not None and not np.isnan(value) else default


def value_or_zero(value: Optional[T]) -> T:
    return value_or_default(value=value, default=0)


def complex_inverse_real_part(real: float, imag: float) -> float:
    return (1.0 / (real + 1j * imag)).real


def complex_inverse_imaginary_part(real: float, imag: float) -> float:
    return (1.0 / (real + 1j * imag)).imag


# TODO: Check Z logic
def get_winding_from(conn_str: str, neutral_grounding: bool = True) -> WindingType:
    wfr, wto, clock_str = _split_connection_string(conn_str)
    winding = WINDING_TYPES[wfr]
    if winding == WindingType.wye_n and not neutral_grounding:
        winding = WindingType.wye
    if wfr[0] == "Z" and wto != "d" and int(clock_str) % 2:
        winding = WindingType.delta
    return winding


# TODO: Check Z logic
def get_winding_to(conn_str: str, neutral_grounding: bool = True) -> WindingType:
    wfr, wto, clock_str = _split_connection_string(conn_str)
    winding = WINDING_TYPES[wto.upper()]
    if winding == WindingType.wye_n and not neutral_grounding:
        winding = WindingType.wye
    if wfr != "D" and wto[0] == "z" and int(clock_str) % 2:
        winding = WindingType.delta
    return winding


def get_clock(conn_str: str) -> int:
    _, _, clock_str = _split_connection_string(conn_str)
    clock = int(clock_str)
    return clock


def _split_connection_string(conn_str: str) -> Tuple[str, str, str]:
    match = CONNECTION_PATTERN.fullmatch(conn_str)
    if not match:
        raise ValueError(f"Invalid transformer connection string: '{conn_str}'")
    return match.groups()