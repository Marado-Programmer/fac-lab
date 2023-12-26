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

float getTemp();  // returns the temprature of the Arduino's sensor

unsigned long last = micros();
constexpr unsigned int UPS = 24;       // Updates Per Second
constexpr double UPMUS = (1e6 / UPS);  // Microseconds it takes to do an update
double delta = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  Serial.print("t, sensor_value");
}

void loop() {
  unsigned long cur = micros();
  delta += (cur - last) / UPMUS;
  last = cur;
  if (delta >= 1) {
    Serial.print("\r\n");
    Serial.print(cur / 1e6);
    Serial.print(",");
    Serial.print(getTemp());
    delta -= 1;
  }
}

float getTemp() {
  return 0;
}