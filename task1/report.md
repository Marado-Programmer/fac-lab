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
This is calculated knowing that $1s = 10^6μs$, in 10^6μs we do `UPS` updates only if in 1μs we do $(1*10^6)/UPS$ updates

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

Now if the `delta` is >=100% do an update and subtract 100% to `delta`.

In this case, the update is to send the row with the data.

### Simpler alternative

The Arduino API offers [`void delay(unsigned long ms)`](https://www.arduino.cc/reference/en/language/functions/time/delay/) and [`void delayMicroseconds(unsigned int us)`](https://www.arduino.cc/reference/en/language/functions/time/delaymicroseconds/) witch "pauses the program for the amount of time".

Knowing this we could just do:
``` cpp
void loop() {
	Serial.print("\r\n");
	Serial.print(cur / 1e6);
	Serial.print(",");
	Serial.print(getTemp());

	delayMicroseconds(UPMUS);
}
```

So much simpler. You also get to remove some unusable variables and make the code more readable.

Also, probably Arduino's implementation of these two functions is so much more performant.
