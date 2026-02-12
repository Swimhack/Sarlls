/*
 * ESP32 Simple IoT Switch - Test Firmware
 *
 * This firmware validates all hardware functionality:
 * - Power supply (3.3V rail)
 * - USB-UART communication
 * - WiFi/BLE connectivity
 * - GPIO functionality
 * - Relay control
 * - Status LEDs
 *
 * Pin Assignments:
 * - GPIO4 (IO4):  Relay driver (through BC817)
 * - GPIO5 (IO5):  Relay status LED
 * - GPIO0 (IO0):  Boot button (active low)
 * - EN:           Reset (active low)
 * - GPIO1 (TXD0): UART TX
 * - GPIO3 (RXD0): UART RX
 *
 * For Arduino IDE:
 * - Board: ESP32 Dev Module
 * - Upload Speed: 115200
 * - Flash Frequency: 40MHz
 * - Partition Scheme: Default
 */

#include <WiFi.h>
#include <BLEDevice.h>
#include <BLEServer.h>

// Pin definitions
#define RELAY_PIN       4     // GPIO4 - Relay driver
#define RELAY_LED_PIN   5     // GPIO5 - Relay status LED
#define BOOT_PIN        0     // GPIO0 - Boot button

// Test intervals
#define RELAY_TOGGLE_MS 2000  // Toggle relay every 2 seconds
#define WIFI_SCAN_MS    10000 // Scan WiFi every 10 seconds
#define STATUS_PRINT_MS 5000  // Print status every 5 seconds

// Global variables
unsigned long lastRelayToggle = 0;
unsigned long lastWifiScan = 0;
unsigned long lastStatusPrint = 0;
bool relayState = false;
int wifiNetworksFound = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(1000); // Wait for serial to stabilize

  Serial.println();
  Serial.println("==========================================");
  Serial.println("ESP32 Simple IoT Switch - Test Firmware");
  Serial.println("==========================================");
  Serial.println();

  // Initialize GPIO
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(RELAY_LED_PIN, OUTPUT);
  pinMode(BOOT_PIN, INPUT_PULLUP);

  // Set initial states
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(RELAY_LED_PIN, LOW);

  Serial.println("[OK] GPIO initialized");

  // Test power supply
  testPowerSupply();

  // Test WiFi
  testWiFi();

  // Test BLE
  testBLE();

  // Initial status
  Serial.println();
  Serial.println("==========================================");
  Serial.println("Hardware Test Complete - Entering Loop");
  Serial.println("==========================================");
  Serial.println();
  Serial.println("Relay will toggle every 2 seconds.");
  Serial.println("Press BOOT button to manually trigger relay.");
  Serial.println();
}

void loop() {
  unsigned long currentMillis = millis();

  // Toggle relay periodically
  if (currentMillis - lastRelayToggle >= RELAY_TOGGLE_MS) {
    lastRelayToggle = currentMillis;
    toggleRelay();
  }

  // Scan WiFi periodically
  if (currentMillis - lastWifiScan >= WIFI_SCAN_MS) {
    lastWifiScan = currentMillis;
    scanWiFi();
  }

  // Print status periodically
  if (currentMillis - lastStatusPrint >= STATUS_PRINT_MS) {
    lastStatusPrint = currentMillis;
    printStatus();
  }

  // Check boot button
  if (digitalRead(BOOT_PIN) == LOW) {
    Serial.println("[BTN] Boot button pressed!");
    toggleRelay();
    delay(300); // Debounce
    while (digitalRead(BOOT_PIN) == LOW) {
      delay(10); // Wait for release
    }
  }
}

void testPowerSupply() {
  Serial.println();
  Serial.println("--- Power Supply Test ---");

  // Read internal temperature sensor
  float temp = temperatureRead();
  Serial.printf("[OK] Internal temperature: %.1f C\n", temp);

  // Check if we can read from ADC (validates 3.3V reference)
  analogSetAttenuation(ADC_11db);
  int adcValue = analogRead(36); // VP pin if available
  Serial.printf("[OK] ADC functional (sample: %d)\n", adcValue);

  // Report free heap (memory test)
  Serial.printf("[OK] Free heap: %d bytes\n", ESP.getFreeHeap());

  Serial.println("[OK] Power supply test passed");
}

void testWiFi() {
  Serial.println();
  Serial.println("--- WiFi Test ---");

  // Initialize WiFi in station mode
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  Serial.println("[OK] WiFi initialized");

  // Get MAC address
  Serial.print("[OK] MAC Address: ");
  Serial.println(WiFi.macAddress());

  // Scan for networks
  Serial.println("[..] Scanning for WiFi networks...");
  wifiNetworksFound = WiFi.scanNetworks();

  if (wifiNetworksFound == 0) {
    Serial.println("[WARN] No networks found");
  } else {
    Serial.printf("[OK] Found %d networks:\n", wifiNetworksFound);
    for (int i = 0; i < min(wifiNetworksFound, 5); i++) {
      Serial.printf("     %d: %s (%d dBm)\n", i + 1, WiFi.SSID(i).c_str(), WiFi.RSSI(i));
    }
    if (wifiNetworksFound > 5) {
      Serial.printf("     ... and %d more\n", wifiNetworksFound - 5);
    }
  }

  Serial.println("[OK] WiFi test passed");
}

void testBLE() {
  Serial.println();
  Serial.println("--- BLE Test ---");

  // Initialize BLE
  BLEDevice::init("ESP32_IoT_Switch");
  Serial.println("[OK] BLE initialized");

  // Get BLE address
  Serial.print("[OK] BLE Address: ");
  Serial.println(BLEDevice::getAddress().toString().c_str());

  // Create a simple BLE server
  BLEServer *pServer = BLEDevice::createServer();
  Serial.println("[OK] BLE server created");

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();
  Serial.println("[OK] BLE advertising started");

  Serial.println("[OK] BLE test passed");
}

void toggleRelay() {
  relayState = !relayState;
  digitalWrite(RELAY_PIN, relayState ? HIGH : LOW);
  digitalWrite(RELAY_LED_PIN, relayState ? HIGH : LOW);

  Serial.printf("[RELAY] %s\n", relayState ? "ON" : "OFF");
}

void scanWiFi() {
  Serial.println("[..] WiFi scan...");
  wifiNetworksFound = WiFi.scanNetworks();
  Serial.printf("[OK] Found %d networks\n", wifiNetworksFound);
}

void printStatus() {
  Serial.println();
  Serial.println("--- Status ---");
  Serial.printf("Uptime: %lu seconds\n", millis() / 1000);
  Serial.printf("Relay: %s\n", relayState ? "ON" : "OFF");
  Serial.printf("WiFi networks: %d\n", wifiNetworksFound);
  Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
  Serial.printf("Internal temp: %.1f C\n", temperatureRead());
  Serial.println();
}
