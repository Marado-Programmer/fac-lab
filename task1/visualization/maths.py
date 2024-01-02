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


def sig(x):
    if math.isinf(x):
        return 0

    return 1 / (1 + math.exp(-x))


def inv_sig(x):
    return math.log(x, math.e) - math.log(1 - x, math.e)


def largest_divisor(x: int) -> int:
    if x % 2 == 0:
        return x // 2

    for i in range(3, int(math.sqrt(x)) + 2, 2):
        if x % i == 0:
            return x // i

    return 1


def find_squarest_rectangle(n) -> (int, int):
    x = largest_divisor(n)
    return x, n // x


def sum_i_equals_0_n_i(n: int) -> int:
    return (n * (n + 1)) // 2
