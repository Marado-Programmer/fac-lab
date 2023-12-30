from sys import stderr
from pathlib import Path
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

            file_name = f"data/data_sensor_raw_{serial.name}.csv"

            with open(file_name, 'ab') as stream:
                while n_rows > 0:
                    stream.write(serial.readline())
                    stream.write(b'\n')  # removed from serial.Serial.readline()
                    n_rows -= 1
