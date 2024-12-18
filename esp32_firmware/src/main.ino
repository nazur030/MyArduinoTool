// ESP32 LED Blink Example
void setup() {
    pinMode(2, OUTPUT);  // Set GPIO 2 as an output pin
}

void loop() {
    digitalWrite(2, HIGH);  // Turn LED ON
    delay(100);            // Wait 1 second
    digitalWrite(2, LOW);   // Turn LED OFF
    delay(100);            // Wait 1 second
}
