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
#ifndef SEPARATOR_SEPARATED_VALUES_H
#define SEPARATOR_SEPARATED_VALUES_H

#include <Print.h>
#include <string>
#include <map>
#include <vector>

using std::string;

typedef std::map<string, float> row_t;

class SeparatorSeparatedValues {
public:
  SeparatorSeparatedValues(arduino::Print* stream,  const string& separator,const string& delimiter);

  void add_column(const string& column);
  void write_header();
  void write_row(const row_t& row);

private:
  arduino::Print* stream;
  string separator;
  string delimiter;
  std::vector<string> columns;
  bool headerWritten;
};

class CSV : public SeparatorSeparatedValues {
public:
  CSV(arduino::Print* stream);
};

class TSV : public SeparatorSeparatedValues {
public:
  TSV(arduino::Print* stream);
};

#endif