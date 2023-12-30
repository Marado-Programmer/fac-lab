from pathlib import Path
from sys import stderr
from time import time

from pandas import DataFrame
from serial import Serial
from serial.tools.list_ports import comports

MIN_ROWS = 10


def create_serial(port_info):
    return Serial(port=port_info.device,
                  baudrate=115200,
                  timeout=1)


def get_n_rows():
    n = int(input('How many rows of data you want to receive:\t'))

    if n < MIN_ROWS:
        print(f"number of rows can't be less than {MIN_ROWS}, n_rows={n}\nnumber of rows it's now {MIN_ROWS}\n",
              file=stderr)

    return max(MIN_ROWS, n)


if __name__ == '__main__':
    Path("data").mkdir(parents=True, exist_ok=True)

    for port in comports():
        with create_serial(port) as serial:
            if not serial.is_open:
                serial.open()

            n_rows = get_n_rows()

            directory = "data"
            file_name = f"data_sensor_raw_{serial.name}_{time()}.csv"

            separator = ","
            delimiter = "\r\n"

            with open(f"{directory}/{file_name}", 'ab') as stream:
                i = 1
                first = True
                header = []
                data = {}
                while n_rows >= 0:  # first line will be the header so does not count as a row
                    line = str(serial.readline())
                    split = line.strip().split(separator)

                    if first:
                        header = split
                        for column in header:
                            data[column] = []
                        stream.write(bytes(line.strip(), "utf-8"))
                        first = False
                    else:
                        for index, v in enumerate(split):
                            data[header[index]].append(v)

                        stream.write(bytes(f"{delimiter}{line.strip()}", "utf-8"))

                    i += 1
                    n_rows -= 1

                data_frame = DataFrame(data)
                data_frame.to_csv(f"{directory}/pandas_{file_name}", index=False)
