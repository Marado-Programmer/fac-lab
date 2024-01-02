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

from pandas import DataFrame
from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from maths import inv_sig, sig
from plots import draw_plots, draw_subplots, draw_hist, draw_subhists, draw_scatter, draw_subscatters
from report import create_report, write_report

MIN_ROWS = 200


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


def draw(d: DataFrame, s: Serial) -> None:
    draw_plots(d[["timestamp", "sin", "cos"]])
    draw_subplots(d)
    draw_hist(d, 20)
    draw_subhists(d, 20)
    draw_scatter(d)
    draw_subscatters(d, s.name)


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
