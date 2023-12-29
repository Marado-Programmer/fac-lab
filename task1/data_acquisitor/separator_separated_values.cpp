/*
    Reads values from the Arduino's sensors and sends it to the computer via
    serial communications using a "separator separated values" format.
    Copyright (C) 2023  João Augusto Costa Branco Marado Torres

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/
#include <Print.h>
#include <string>
#include <vector>

#include "./separator_separated_values.h"

SeparatorSeparatedValues::SeparatorSeparatedValues(arduino::Print* stream, const std::string& separator, const std::string& delimiter)
  : stream(stream), separator(separator), delimiter(delimiter), headerWritten(false) {
}


void SeparatorSeparatedValues::add_column(const std::string& column) {
  this->columns.push_back(column);
}

void SeparatorSeparatedValues::write_header() {
  if (this->headerWritten) {
    return;
  }

  bool first = true;
  for (auto column : this->columns) {
    if (!first) {
      this->stream->print(this->separator.c_str());
    } else {
      first = false;
    }
    this->stream->print(column.c_str());
  }

  this->headerWritten = true;
}

void SeparatorSeparatedValues::write_row(const row_t& row) {
  if (!this->headerWritten) {
    return;
  }

  this->stream->print(this->delimiter.c_str());

  bool first = true;
  for (auto column : this->columns) {
    if (!first) {
      this->stream->print(this->separator.c_str());
    } else {
      first = false;
    }
    if (row.find(column) != row.end()) {
      this->stream->print(row.at(column));
    }
  }
}

CSV::CSV(arduino::Print* stream)
  : SeparatorSeparatedValues{ stream, ",", "\r\n" } {
}

TSV::TSV(arduino::Print* stream)
  : SeparatorSeparatedValues{ stream, "\t", "\n" } {
}