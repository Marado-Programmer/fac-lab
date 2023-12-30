# Acquisition

The initial objective was to retrieve data from [Arduino](https://www.arduino.cc/) sensors and transmit it to the computer through serial communication in [CSV](https://www.ietf.org/rfc/rfc4180.txt) format, specifying the timestamp of each sensor reading in seconds.

It is important to note that the required format is not strictly CSV, but rather a simple '*t, valor_sensor*' pair for each reading, where '*t*' represents the timestamp and '*valor_sensor*' represents the value obtained from the sensor.
The delimiter used in this case is not a single comma, but rather a comma followed by a space.
CSV (as well as [TSV](https://www.iana.org/assignments/media-types/text/tab-separated-values)) is a well-standardized way of formatting data, making it appropriate for this application.

The CSV file format does not require a header, which means it may be absent.
Although a header is not required, it may be useful in cases where multiple values from different sensors are present.

So I made this simple Sketch:
``` cpp
#include <Arduino.h>

float getTemp();  // returns the temperature of the Arduino's sensor

unsigned long last = micros();
constexpr unsigned int UPS = 24;       // Updates Per Second
constexpr double UPMUS = (1e6 / UPS);  // Microseconds it takes to do an update
double delta = 0;

void setup() {
	Serial.begin(115200);
	while (!Serial) {}

	Serial.print("t,sensor_value");
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
```

Let's walk through the more important parts of it!

## Specifying the CSV header in [`void setup()`](https://www.arduino.cc/reference/en/language/structure/sketch/setup/)

It only needs to be sent once, so it only makes sense to appear in `void setup()`.

## Throttling the reads on [`void loop()`](https://www.arduino.cc/reference/en/language/structure/sketch/loop/)

Now in the loop, we will send each row of the CSV with the data we want to show.

Because I think it makes sense to have some time between each read, I implemented a very common way of throttling procedures.
I know it because of game development, they implement this "game loop" to control when to update the game logic and when to update what the user sees in the game, basically the FPS.

Here I implemented it like this:
``` cpp
unsigned long last = micros();
constexpr unsigned int UPS = 24;
constexpr double UPMUS = (1e6 / UPS);
double delta = 0;
```

The variable `last` will be used to know when was the last time we tried to update. Here we are using the [`unsigned long micros()`](https://www.arduino.cc/reference/en/language/functions/time/micros/), but we could've used the [`unsigned long millis()`](https://www.arduino.cc/reference/en/language/functions/time/millis/) instead.
The choice here was made because microseconds give us more precision than milliseconds for the calculations we do.
Does it matter? That's for you to decide.
Probably for most situations the difference it's insignificant for you.

Then we define the `UPS` which stands for **U**pdates **P**er **S**econds. It will define how many rows of data you want to send in one second.

We also define `UPMUS` that is, based on the `UPS`, how many microseconds it takes to do an update (because we are using `unsigned long micros()`).
This is calculated knowing that $1s = 10^6μs$, in $10^6μs$ we do `UPS` updates only if in 1μs we do $(1*10^6)/UPS$ updates

The `delta` variable controls how are we to do an update.
It will usually have a value not lower than 0% and close to 100%.
The value it's 100% which means we need to do an update and then we reset `delta`.

Now let's take a look at the `void loop()`:
``` cpp
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
```

`cur` is the current time.

Using `cur`, we add to `delta` how much more we got close to an update.

Remember the `last` variable? When we do `cur - last` we get time elapsed in microseconds since the last attempt to update.
Dividing that by the `UPMUS` we get a how many updates should be made in that elapsed time.
Normally it shouldn't be a big value since `void loop()` loops very fast but imagine it takes 1 microsecond to do an update. If the time elapsed was 2 microseconds that means we need to do 2 more updates.

We make `last = cur`.

Now if the `delta` is >=100% do an update and subtract 100% to `delta`. This can be transformed into a `while` loop which might make more sense and will work the same almost every time since it's hard for `delta` to reach 200%.

In this case, the update is to send the row with the data.

### Simpler alternative

The Arduino API offers [`void delay(unsigned long ms)`](https://www.arduino.cc/reference/en/language/functions/time/delay/) and [`void delayMicroseconds(unsigned int us)`](https://www.arduino.cc/reference/en/language/functions/time/delaymicroseconds/) witch "pauses the program for the amount of time".

Knowing this we could just do:
``` cpp
void loop() {
	unsigned long cur = micros();

	Serial.print("\r\n");
	Serial.print(cur / 1e6);
	Serial.print(",");
	Serial.print(getTemp());

	delayMicroseconds(UPMUS);
}
```

So much simpler. You also get to remove some unusable variables and make the code more readable.

Also, probably Arduino's implementation of these two functions is so much more performant.

# Using the sensors

First of all, each Arduino board model will have different sensors and different ways to read the values from them.

I have a [Nano RP2040 Connect](https://docs.arduino.cc/hardware/nano-rp2040-connect).

In my case, the way I found to read values from my sensor it's by using the [Arduino_LSM6DSOX Library](https://github.com/arduino-libraries/Arduino_LSM6DSOX).

``` cpp
#include <Arduino.h>
#include <Arduino_LSM6DSOX.h>

float getTemp();

constexpr unsigned int UPS = 24;
constexpr double UPMUS = (1e6 / UPS);

bool sensor_usable = false;

void setup() {
	Serial.begin(115200);
	while (!Serial) {}

	// Writing the header
#ifdef IMU
	sensor_usable = IMU.begin();
	if (!sensor_usable) {
		// Failed to initialize IMU!
		Serial.print("t");
	} else {
		Serial.print("t,sensor_value");
	}
#else
	Serial.print("t");
#endif
}

void loop() {
	// Writing a row
	Serial.print("\r\n");
	Serial.print(micros() / 1e6);
	if (sensor_usable) {
		Serial.print(",");
		Serial.print(getTemp());
	}
	
	delayMicroseconds(UPMUS);
}

float getTemp() {
#ifdef IMU
	if (IMU.temperatureAvailable()) {
		float temp = 0;
		IMU.readTemperatureFloat(temp);
		
		return temp;
	}
#endif
	
	return 0;
}
```

The library should provide the macro `IMU`. In case the macro isn't defined I use the preprocessor `#ifdef`. My idea it's to make the program work every time. If the macro `IMU` isn't defined or the sensor it's not usable, we won't send the sensor data and only the timestamps will be sent. The code's very ugly in my opinion right now, but if we have multiple sensors, one not working doesn't stop the program from working.
I can even write support for multiple sensors and if I ever need to get the data from a specific board/sensor I know this code will work if it has support for that board/sensor even if some of the sensors do not exist.

## Separation of concerns

We can separate the data acquisition and the sending of the data. That's what I did.

Here is [separator_separated_values.h](./data_acquisitor/separator_separated_values.h):
``` cpp
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
```

Because we are writing C++, I created a class that sends the data formatted the way you want (on a "separator" separated values style, like CSV for example).
See the [implementation](./data_acquisitor/separator_separated_values.cpp).

The main things you need to know here are:
- `void SeparatorSeparatedValues::add_column(const std::string& column)` lets you add a column to the header;
- `void SeparatorSeparatedValues::write_header()` sends the header;
- `void SeparatorSeparatedValues::write_row(const row_t& row)` sends a row with the data provided.

Now our entry file can look like this:
``` cpp
#include <Arduino.h>
#include <Arduino_LSM6DSOX.h>

#include "./separator_separated_values.h"

void add_columns(SeparatorSeparatedValues* generator);
row_t get_row();

constexpr unsigned int UPS = 24;
constexpr double UPMUS = (1e6 / UPS);

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
	
	row_t row = get_row();
	row["t"] = micros() / 1e6;
	generator->write_row(row);
	
	delayMicroseconds(UPMUS);
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
```

See how much clean it is?

The main reason in my opinion is the use of the [creational design pattern **builder**](https://refactoring.guru/design-patterns/builder) which makes us not worry about `else` statements because imagine how the `void add_columns(SeparatorSeparatedValues* generator)` would look like if we add support to one more sensor in the program. The amount of combinations of having/not having and working/not working sensors would grow exponents making the code full of `else` statements like:

``` cpp
if (A) {
	if (B) {
		// A, B
	} else {
		// A
	}
} else {
	if (B) {
		// B
	} else {
		//
	} 
}
```

That's only two sensors (A and B) by the way.

Giving a map struct as the row with the data to send also prevents this condition statement hell.

Also, you don't need to care about the order you give the data because it will be formatted depending on the header. If you care about the order of the columns then be careful about the header.

### TODO

- For now, we can only send `float` values as data values. I made it this way because I can't see the use of strings needing to be sent (unless it's some date, like a timestamp formatted with [RFC3339](https://www.rfc-editor.org/rfc/rfc3339), but you can always use [UNIX epoch](https://en.wikipedia.org/wiki/Unix_time)) and all the basic data types can be cast to a float using [`static_cast<float>()`](https://en.cppreference.com/w/cpp/language/static_cast). But in case we need other data types:
	- We can use templates, but then we can only accept values of a specific type
	- If we want to support multiple types, that's harder. We need to take into account that [`size_t Print::print()`](https://www.arduino.cc/reference/en/language/functions/communication/serial/print/) does not support every type as the first parameter. Maybe something with [`union`](https://en.cppreference.com/w/cpp/language/union) types using [polymorthism as showed by Low Level Learning](https://youtu.be/ZMzdrEYKyFQ?t=296&si=J8sLgql6lqij1-fd), `void*` pointers or [`std::any`](https://en.cppreference.com/w/cpp/utility/any).
 - If strings were supported as values, we would have problems because they would need to either escape the string or just throw an exception in case of an invalid string. Imagine the value string "there's a, here" and the problem it would cause when parsing the CSV.
