#  Reads values from the Arduino's sensors and sends it to the computer via
#  serial communications using a "separator separated values" format.
#  Copyright (C) 2023  João Augusto Costa Branco Marado Torres
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import math

from pandas import Series


def mean(vals: list[float] | Series) -> float:
    acc = 0
    for i in vals:
        acc += i

    return acc / len(vals)


def median(vals: list[float] | Series) -> float:
    size = len(vals)
    odd = bool(size & 1)
    mid = int(math.floor(size / 2))

    if isinstance(vals, Series):
        sorted_vals = vals.sort_values()
        sorted_vals.reset_index(drop=True, inplace=True)
        return sorted_vals.get(mid) if odd else mean([sorted_vals.get(mid - 1), sorted_vals.get(mid)])
    elif isinstance(vals, list):
        vals.sort()
        return vals[mid] if odd else mean([vals[mid - 1], vals[mid]])
