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
from datetime import datetime
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


def sig(x):
    if math.isinf(x):
        return 0

    return 1 / (1 + math.exp(-x))


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


def create_csv(ser: Serial) -> DataFrame:
    directory = "data"
    file_name = f"data_sensor_raw_{ser.name}_{int(time())}.csv"

    with open(f"{directory}/{file_name}", 'xb') as stream:
        d = write_csv(stream, ser, get_n_rows())

    df = DataFrame(d)
    df.to_csv(f"{directory}/pandas_{file_name}", index=False)

    return df


def write_csv(file_stream: BinaryIO, _ser: Serial, n_rows: int = 200) -> dict[str, list[float]]:
    separator = ","
    delimiter = "\r\n"

    first = True

    h = []
    d = {}
    while n_rows >= 0:  # first line will be the header so does not count as a row
        # line = str(ser.readline())
        # split = line.strip().split(separator)

        if first:
            line = "timestamp,temperature,pressure,sin,cos,sig(tg)"
            split = line.strip().split(separator)

            h = split
            for column in h:
                d[column] = []
            file_stream.write(bytes(line.strip(), "utf-8"))
            first = False
        else:
            line = (f"{time()},"
                    f"{random.uniform(-5, 5)},"
                    f"{inv_sig(random.uniform(0, 1))},"
                    f"{math.sin(n_rows * math.pi / 12) + random.uniform(-0.5, 0.5)},"
                    f"{math.cos(n_rows * math.pi / 12) + random.uniform(-0.5, 0.5)},"
                    f"{sig(math.tan(n_rows * math.pi / 3) + random.uniform(-2, 2))}")
            split = line.strip().split(separator)

            sleep(1 / 144)

            for index, v in enumerate(split):
                d[h[index]].append(float(v) if '.' in v else int(v))

            file_stream.write(bytes(f"{delimiter}{line.strip()}", "utf-8"))

        n_rows -= 1

    return d


def draw_plots(data_dict: dict[str, list[float]] | DataFrame) -> None:
    columns = data_dict.columns

    x_column = columns[0]
    for c in columns[1:]:
        plt.title(f"Graph {x_column}-{c}")
        plt.xlabel(x_column)
        plt.ylabel(c)

        plt.plot(data_dict[x_column], data_dict[c])

        plt.show()


def draw_subplots(data_dict: dict[str, list[float]] | DataFrame, title: str) -> None:
    columns = data_dict.columns

    x = int(math.floor(math.sqrt(len(columns) - 1)))
    y = math.ceil((len(columns) - 1) / x)
    fig, plots = plt.subplots(y, x, sharey=True, sharex=True)

    fig.suptitle(title)

    x_column = columns[0]

    def conf_axe(axe: Axes, name: str) -> None:
        axe.set_title(f"Graph {x_column}-{name}")
        axe.set_xlabel(x_column)
        axe.set_ylabel(name)

        axe.plot(data_dict[x_column], data_dict[name])

    counter = 0
    if y > 1:
        for i in range(y):
            if x > 1:
                for j in range(x):
                    if counter >= len(columns) - 1:
                        continue

                    c = columns[i * x + j + 1]
                    conf_axe(plots[i, j], c)

                    counter += 1
            else:
                c = columns[i + 1]
                conf_axe(plots[i], c)
    else:
        if x > 1:
            for j in range(x):
                if counter >= len(columns) - 1:
                    continue

                c = columns[j + 1]
                conf_axe(plots[j], c)

                counter += 1
        else:
            c = columns[1]
            conf_axe(plots[0], c)

    plt.tight_layout()
    plt.show()


def draw_hist(data_dict: dict[str, list[float]] | DataFrame, bins: int) -> None:
    columns = data_dict.columns

    for c in columns[1:]:
        plt.title(f"Histogram {c}")
        plt.xlabel(c)
        plt.ylabel("Amount")

        plt.hist(data_dict[c], bins=bins)

        plt.show()


def draw_subhists(data_dict: dict[str, list[float]] | DataFrame, title: str, bins: int) -> None:
    columns = data_dict.columns

    x = int(math.floor(math.sqrt(len(columns) - 1)))
    y = math.ceil((len(columns) - 1) / x)
    fig, plots = plt.subplots(y, x, sharey=True, sharex=True)

    fig.suptitle(title)

    def conf_axe(axe: Axes, name: str) -> None:
        axe.set_title(f"Histogram {c}")
        axe.set_xlabel(name)
        axe.set_ylabel("Amount")

        axe.hist(data_dict[name], bins=bins)

    counter = 0
    if y > 1:
        for i in range(y):
            if x > 1:
                for j in range(x):
                    if counter >= len(columns) - 1:
                        continue

                    c = columns[i * x + j + 1]
                    conf_axe(plots[i, j], c)

                    counter += 1
            else:
                c = columns[i + 1]
                conf_axe(plots[i], c)
    else:
        if x > 1:
            for j in range(x):
                if counter >= len(columns) - 1:
                    continue

                c = columns[j + 1]
                conf_axe(plots[j], c)

                counter += 1
        else:
            c = columns[1]
            conf_axe(plots[0], c)

    plt.tight_layout()
    plt.show()

def draw_scatter(data_dict: dict[str, list[float]] | DataFrame) -> None:
    columns = data_dict.columns
    n = len(columns)

    for i in range(1, n):
        for j in range(i + 1, n):

            plt.title(f"Scatter {columns[i]}-{columns[j]}")
            plt.xlabel(columns[i])
            plt.ylabel(columns[j])

            plt.scatter(data_dict[columns[i]], data_dict[columns[j]], s=1 / 3)
            plt.show()


def draw_subscatters(data_dict: dict[str, list[float]] | DataFrame, title: str) -> None:
    columns = data_dict.columns
    n = len(columns) - 2
    n = int((n * (n + 1)) / 2)

    x = int(math.floor(math.sqrt(n)))
    y = math.ceil(n / x)
    fig, plots = plt.subplots(y, x, sharey=True, sharex=True)

    fig.suptitle(title)

    def conf_axe(axe: Axes, name_x: str, name_y: str) -> None:
        axe.set_title(f"Scatter {name_x}-{name_y}")
        axe.set_xlabel(name_x)
        axe.set_ylabel(name_y)

        axe.scatter(data_dict[name_x], data_dict[name_y], s=1 / 3)

    counter = 0
    for i in range(1, len(columns)):
        for j in range(i + 1, len(columns)):
            if counter >= n:
                continue

            conf_axe(plots[counter // x, counter % x] if x > 1 and y > 1 else plots[counter], columns[i], columns[j])

            counter += 1

    plt.tight_layout()
    plt.show()


def draw(d: DataFrame, s: Serial) -> None:
    draw_plots(d)
    draw_subplots(d, s.name)
    draw_hist(d, 20)
    draw_subhists(d, s.name, 20)
    draw_scatter(d)
    draw_subscatters(d, s.name)

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


def create_report(p: ListPortInfo, s: Serial, d: dict[str, list[float]] | DataFrame) -> str:
    report = (f"fac-lab  Copyright (C) 2023  João Augusto Costa Branco Marado Torres\n"
              f"This program comes with ABSOLUTELY NO WARRANTY.\n"
              f"This is free software, and you are welcome to redistribute it\n"
              f"under certain conditions; type `show c' for details.\n"
              f"\n"
              f"# Report\n"
              f"## Date\n"
              f"{datetime.today()}\n"
              f"## Arduino\n"
              f"{p.__str__()}\n"
              f"{s.__str__()}\n"
              f"## Statistics\n")

    first = True
    for col in d:
        if first:
            first = False
            continue
        else:
            report += (f"### {col}\n"
                       f"- average: {mean(d[col])}\n"
                       f"- median: {median(d[col])}\n"
                       f"- standard deviation: {d[col].std()}\n"
                       f"- max: {d[col].max()}\n"
                       f"- min: {d[col].min()}\n")

    return report


def write_report(r: str, s: Serial) -> None:
    directory = "report"
    file_name = f"report_{s.name}_{int(time())}.md"

    with open(f"{directory}/{file_name}", 'ab') as stream:
        stream.write(bytes(r, "utf-8"))


if __name__ == '__main__':
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("report").mkdir(parents=True, exist_ok=True)

    for port in comports():
        with create_serial(port) as serial:
            data_frame = create_csv(serial)

            draw(data_frame, serial)

            rep = create_report(port, serial, data_frame)
            print(rep)

            write_report(rep, serial)
