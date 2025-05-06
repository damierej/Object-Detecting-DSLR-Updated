#define SENSOR_PIN 3  // Push button connected to pin 3
#define LED_PIN 2     // LED pin
#define BUZZER_PIN 12 // Pin for the buzzer (optional)

int sensorState = LOW;  // Tracks the sensor's state (HIGH or LOW)

void setup() {
  Serial.begin(9600);  // Start Serial communication at 9600 baud
  pinMode(SENSOR_PIN, INPUT_PULLUP);  // Push button with internal pull-up resistor
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Test the LED on startup
  Serial.println("Testing LED...");
  digitalWrite(LED_PIN, HIGH);  // Turn on LED
  delay(2000);  // Keep it on for 2 seconds
  digitalWrite(LED_PIN, LOW);   // Turn off LED
  Serial.println("LED test complete.");

  Serial.println("Security System Starting...");
  Serial.println("Starting motion detection...");
}

void loop() {
  int reading = digitalRead(SENSOR_PIN);  // LOW when button is pressed

  if (reading == LOW && sensorState == LOW) {  // Button pressed
    Serial.println("MOTION");
    sensorState = HIGH;
  }
  else if (reading == HIGH && sensorState == HIGH) {  // Button released
    Serial.println("STOP");
    sensorState = LOW;
  }

  // Check for commands from Python (e.g., to trigger LED/buzzer)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "DETECTED") {
      Serial.println("Detection received, activating LED...");
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(BUZZER_PIN, HIGH);
      delay(3000);  // LED on for 3 seconds
      digitalWrite(LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, LOW);
    }
  }

  delay(100);
}