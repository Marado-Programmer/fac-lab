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
from datetime import datetime
from time import time

from pandas import DataFrame
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo

from statistics import mean, median


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
