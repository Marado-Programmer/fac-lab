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
#include <Arduino.h>
#include <Arduino_LSM6DSOX.h>

#include "./data_acquisitor.h"
#include "./separator_separated_values.h"

unsigned long last = micros();
constexpr unsigned int UPS = 24;       // Updates Per Second
constexpr double UPMUS = (1e6 / UPS);  // Microseconds it takes to do an update
double delta = 0;

SeparatorSeparatedValues* generator = nullptr;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  generator = new CSV(&Serial);

  add_columns(generator);

  generator->write_header();
}

void loop() {
  if (generator == nullptr) {
    return;
  }

  unsigned long cur = micros();
  delta += (cur - last) / UPMUS;
  last = cur;
  if (delta >= 1) {
    row_t row = get_row();
    row["t"] = cur / 1e6;
    generator->write_row(row);
    delta -= 1;
  }
}

void add_columns(SeparatorSeparatedValues* generator) {
  generator->add_column("t");

#ifdef IMU
  if (IMU.begin()) {
    generator->add_column("sensor_value");
  }
#endif
}

row_t get_row() {
  row_t row;

#ifdef IMU
  if (IMU.begin() && IMU.temperatureAvailable()) {
    float temp = 0;
    IMU.readTemperatureFloat(temp);
    row["sensor_value"] = temp;
  }
#endif

  return row;
}
