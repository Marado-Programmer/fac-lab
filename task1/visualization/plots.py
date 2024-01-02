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
from typing import Callable

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import DataFrame

from maths import find_squarest_rectangle, sum_i_equals_0_n_i

Data = dict[str, list[float]] | DataFrame
ConfigureFig = Callable[[Figure], None]


def draw_plots(data_dict: Data, together: bool = True) -> None:
    columns = data_dict.columns if isinstance(data_dict, DataFrame) else [*data_dict]

    x_column = columns[0]
    for c in columns[1:]:
        plt.title(f"Graph {x_column}-{c}")
        plt.xlabel(x_column)
        plt.ylabel(c)

        plt.plot(data_dict[x_column], data_dict[c])

        if not together:
            plt.show()

    if together:
        plt.show()


def draw_subplots(data_dict: Data, config: ConfigureFig | None = None, groups: list[list[str]] | None = None) -> None:
    columns = data_dict.columns if isinstance(data_dict, DataFrame) else [*data_dict]

    if groups is None:
        groups = [[c] for c in columns[1:]]

    x, y = find_squarest_rectangle(len(groups))

    fig, plots = plt.subplots(y, x, sharex=True, squeeze=False)

    if config is not None:
        config(fig)

    x_column = columns[0]

    def conf_axe(axe: Axes, names: list[str]) -> None:
        y_column = "; ".join(names)
        axe.set_title(f"Graph {x_column}-[{y_column}]")
        axe.set_xlabel(x_column)
        axe.set_ylabel(y_column)

        for name in names:
            print(name)
            axe.plot(data_dict[x_column], data_dict[name], )

    for i in range(y):
        for j in range(x):
            conf_axe(plots[i, j], groups[i * x + j])

    plt.tight_layout()
    plt.show()


def draw_hist(data_dict: dict[str, list[float]] | DataFrame, bins: int) -> None:
    columns = data_dict.columns if isinstance(data_dict, DataFrame) else [*data_dict]

    for c in columns[1:]:
        plt.title(f"Histogram {c}")
        plt.xlabel(c)
        plt.ylabel("Amount")

        plt.hist(data_dict[c], bins=bins)

        plt.show()


def draw_subhists(data_dict: Data, bins: int, config: ConfigureFig | None = None) -> None:
    columns = data_dict.columns if isinstance(data_dict, DataFrame) else [*data_dict]

    x, y = find_squarest_rectangle(len(columns) - 1)

    fig, plots = plt.subplots(y, x, squeeze=False)

    if config is not None:
        config(fig)

    def conf_axe(axe: Axes, name: str) -> None:
        axe.set_title(f"Histogram {name}")
        axe.set_xlabel(name)
        axe.set_ylabel("Amount")

        axe.hist(data_dict[name], bins=bins)

    for i in range(y):
        for j in range(x):
            conf_axe(plots[i, j], columns[i * x + j + 1])

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


def draw_subscatters(data_dict: Data, config: ConfigureFig | None = None) -> None:
    columns = data_dict.columns

    x, y = find_squarest_rectangle(sum_i_equals_0_n_i(len(columns) - 2))

    fig, plots = plt.subplots(y, x, squeeze=False)

    if config is not None:
        config(fig)

    def conf_axe(axe: Axes, name_x: str, name_y: str) -> None:
        axe.set_title(f"Scatter {name_x}-{name_y}")
        axe.set_xlabel(name_x)
        axe.set_ylabel(name_y)

        axe.scatter(data_dict[name_x], data_dict[name_y], s=1 / 3)

    counter = 0
    for i in range(1, len(columns)):
        for j in range(i + 1, len(columns)):
            conf_axe(plots[counter // x, counter % x], columns[i], columns[j])
            counter += 1

    plt.tight_layout()
    plt.show()
