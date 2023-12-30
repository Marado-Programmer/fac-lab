import math
from pathlib import Path
from sys import stderr
from time import time
from typing import BinaryIO

import matplotlib.pyplot as plt
from pandas import DataFrame, Series
from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

MIN_ROWS = 10


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


def write_csv(file_stream: BinaryIO, ser: Serial, n_rows: int) -> (list[str], dict[str, list[float]]):
    first = True

    h = []
    d = {}
    while n_rows >= 0:  # first line will be the header so does not count as a row
        line = str(ser.readline())
        split = line.strip().split(separator)

        if first:
            h = split
            for column in h:
                d[column] = []
            file_stream.write(bytes(line.strip(), "utf-8"))
            first = False
        else:
            for index, v in enumerate(split):
                d[h[index]].append(float(v))

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

    for port in comports():
        with create_serial(port) as serial:
            if not serial.is_open:
                serial.open()

            directory = "data"
            file_name = f"data_sensor_raw_{serial.name}_{time()}.csv"

            separator = ","
            delimiter = "\r\n"

            with open(f"{directory}/{file_name}", 'ab') as stream:
                header, data = write_csv(stream, serial, get_n_rows())

            data_frame = DataFrame(data)
            data_frame.to_csv(f"{directory}/pandas_{file_name}", index=False)

            draw_plots(header, data_frame)
