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
import random
from pathlib import Path
from sys import stderr
from time import time, sleep
from typing import BinaryIO

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame, Series
from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

MIN_ROWS = 200


def inv_sig(x):
    return math.log(x, math.e) - math.log(1 - x, math.e)


def create_serial(port_info: ListPortInfo) -> Serial:
    return Serial(port=port_info.device,
                  baudrate=115200,
                  timeout=1)


def get_n_rows() -> int:
    n = int(input('How many rows of data you want to receive:\t'))

    if n < MIN_ROWS:
        print(f"number of rows can't be less than {MIN_ROWS}, n_rows={n}\nnumber of rows it's now {MIN_ROWS}\n",
              file=stderr)

    return max(MIN_ROWS, n)


def create_csv(ser: Serial) -> (list[str], DataFrame):
    directory = "data"
    file_name = f"data_sensor_raw_{ser.name}_{int(time())}.csv"

    with open(f"{directory}/{file_name}", 'ab') as stream:
        h, d = write_csv(stream, ser, get_n_rows())

    df = DataFrame(d)
    df.to_csv(f"{directory}/pandas_{file_name}", index=False)

    return h, df


def write_csv(file_stream: BinaryIO, _ser: Serial, n_rows: int) -> (list[str], dict[str, list[float]]):
    separator = ","
    delimiter = "\r\n"

    first = True

    h = []
    d = {}
    while n_rows >= 0:  # first line will be the header so does not count as a row
        # line = str(ser.readline())
        # split = line.strip().split(separator)

        if first:
            line = "timestamp,temperature,pressure"
            split = line.strip().split(separator)

            h = split
            for column in h:
                d[column] = []
            file_stream.write(bytes(line.strip(), "utf-8"))
            first = False
        else:
            line = f"{time()},{random.uniform(-8, 8)},{inv_sig(random.uniform(0, 1))}"
            split = line.strip().split(separator)

            sleep(1 / 144)

            for index, v in enumerate(split):
                d[h[index]].append(float(v) if '.' in v else int(v))

            file_stream.write(bytes(f"{delimiter}{line.strip()}", "utf-8"))

        n_rows -= 1

    return h, d


def draw_plots(columns: list[str], data_dict: dict[str, list[float]] | DataFrame) -> None:
    x_column = columns[0]
    for c in columns[1:]:
        plt.title(f"Graph {x_column}-{c}")
        plt.xlabel(x_column)
        plt.ylabel(c)

        plt.plot(data_dict[x_column], data_dict[c])

        plt.show()


def draw_subplots(columns: list[str], data_dict: dict[str, list[float]] | DataFrame, title: str) -> None:
    x = int(math.floor(math.sqrt(len(columns) - 1)))
    y = (len(columns) - 1) // x
    fig, plots = plt.subplots(y, x, sharey=True, sharex=True)

    fig.suptitle(title)

    x_column = columns[0]

    def conf_axe(axe: Axes, name: str) -> None:
        axe.set_title(f"Graph {x_column}-{name}")
        axe.set_xlabel(x_column)
        axe.set_ylabel(name)

        axe.plot(data_dict[x_column], data_dict[name])

    if y > 1:
        for i in range(y):
            if x > 1:
                for j in range(x):
                    c = columns[i * y + j + 1]
                    conf_axe(plots[i, j], c)
            else:
                c = columns[i + 1]
                conf_axe(plots[i], c)
    else:
        if x > 1:
            for j in range(x):
                c = columns[j + 1]
                conf_axe(plots[j], c)
        else:
            c = columns[1]
            conf_axe(plots[0], c)

    plt.tight_layout()
    plt.show()


def draw_hist(columns: list[str], data_dict: dict[str, list[float]] | DataFrame, bins: int) -> None:
    for c in columns[1:]:
        plt.title(f"Histogram {c}")
        plt.xlabel(c)
        plt.ylabel("Amount")

        plt.hist(data_dict[c], bins=bins)

        plt.show()


def draw_subhists(columns: list[str], data_dict: dict[str, list[float]] | DataFrame, title: str, bins: int) -> None:
    x = int(math.floor(math.sqrt(len(columns) - 1)))
    y = (len(columns) - 1) // x
    fig, plots = plt.subplots(y, x, sharey=True, sharex=True)

    fig.suptitle(title)

    def conf_axe(axe: Axes, name: str) -> None:
        plt.title(f"Histogram {c}")
        axe.set_title(f"Histogram {c}")
        axe.set_xlabel(name)
        axe.set_ylabel("Amount")

        axe.hist(data_dict[name], bins=bins)

    if y > 1:
        for i in range(y):
            if x > 1:
                for j in range(x):
                    c = columns[i * y + j + 1]
                    conf_axe(plots[i, j], c)
            else:
                c = columns[i + 1]
                conf_axe(plots[i], c)
    else:
        if x > 1:
            for j in range(x):
                c = columns[j + 1]
                conf_axe(plots[j], c)
        else:
            c = columns[1]
            conf_axe(plots[0], c)

    plt.tight_layout()
    plt.show()


def draw(h: list[str], d: DataFrame, s: Serial) -> None:
    draw_plots(h, d)
    draw_subplots(h, d, s.name)
    draw_hist(h, d, 20)
    draw_subhists(h, d, s.name, 20)

    plt.xlabel(h[1])
    plt.ylabel(h[2])
    plt.title(f"Scatter {h[1]}-{h[2]}")
    plt.scatter(d[h[1]], d[h[2]], s=.2)

    plt.show()


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


if __name__ == '__main__':
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("report").mkdir(parents=True, exist_ok=True)

    for port in comports():
        with create_serial(port) as serial:
            if not serial.is_open:
                serial.open()

            header, data_frame = create_csv(serial)

            draw(header, data_frame, serial)

            serial.close()
