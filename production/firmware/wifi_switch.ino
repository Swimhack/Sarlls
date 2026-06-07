/*
 * Sarlls IoT Smart Switch - Production Firmware
 * WiFi Remote On/Off Control
 *
 * Connects to WiFi and runs a web server on the ESP32.
 * Control the relay from any browser on the same network.
 *
 * Endpoints:
 *   http://<ip>/        - Status page with on/off buttons
 *   http://<ip>/on      - Turn relay ON
 *   http://<ip>/off     - Turn relay OFF
 *   http://<ip>/toggle  - Toggle relay state
 *   http://<ip>/status  - JSON status (for app integration)
 *
 * Pin Assignments:
 *   GPIO4 (IO4):  Relay driver (through BC817 transistor)
 *   GPIO5 (IO5):  Relay status LED (green)
 *   GPIO0 (IO0):  Boot button (manual toggle)
 *   EN:           Reset button
 *
 * First Boot:
 *   If no WiFi credentials are saved, the ESP32 creates an access point:
 *     SSID: Sarlls-Switch-XXXX
 *     Password: sarlls1234
 *   Connect to it and go to http://192.168.4.1 to configure WiFi.
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <ESPmDNS.h>

// --- Pin Definitions ---
#define RELAY_PIN       4
#define RELAY_LED_PIN   5
#define BOOT_PIN        0

// --- Globals ---
WebServer server(80);
Preferences prefs;
bool relayState = false;
bool apMode = false;
String deviceName = "sarlls-switch";
unsigned long lastButtonPress = 0;

// --- Relay Control ---
void setRelay(bool state) {
  relayState = state;
  digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  digitalWrite(RELAY_LED_PIN, state ? HIGH : LOW);
  Serial.printf("[RELAY] %s\n", state ? "ON" : "OFF");
}

// --- HTML Page ---
String buildPage() {
  String stateText = relayState ? "ON" : "OFF";
  String stateColor = relayState ? "#4CAF50" : "#f44336";
  String ip = apMode ? "192.168.4.1" : WiFi.localIP().toString();

  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  html += "<title>Sarlls IoT Switch</title>";
  html += "<style>";
  html += "body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;";
  html += "display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}";
  html += ".card{background:#16213e;border-radius:16px;padding:40px;text-align:center;";
  html += "box-shadow:0 8px 32px rgba(0,0,0,0.3);max-width:360px;width:90%}";
  html += "h1{margin:0 0 8px;font-size:24px;color:#e2e2e2}";
  html += ".status{font-size:48px;font-weight:700;margin:24px 0;color:" + stateColor + "}";
  html += ".btn{display:inline-block;padding:16px 48px;margin:8px;border:none;";
  html += "border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;";
  html += "text-decoration:none;color:#fff;transition:transform 0.1s}";
  html += ".btn:active{transform:scale(0.95)}";
  html += ".btn-on{background:#4CAF50}.btn-off{background:#f44336}";
  html += ".info{margin-top:24px;font-size:13px;color:#888}";
  html += "</style></head><body>";
  html += "<div class='card'>";
  html += "<h1>Sarlls IoT Switch</h1>";
  html += "<div class='status'>" + stateText + "</div>";
  html += "<div>";
  html += "<a class='btn btn-on' href='/on'>ON</a>";
  html += "<a class='btn btn-off' href='/off'>OFF</a>";
  html += "</div>";
  html += "<div class='info'>IP: " + ip + "<br>";
  html += "http://" + deviceName + ".local</div>";
  html += "</div></body></html>";
  return html;
}

// --- WiFi Config Page (AP Mode) ---
String buildConfigPage() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  html += "<title>Sarlls Switch Setup</title>";
  html += "<style>";
  html += "body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;";
  html += "display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}";
  html += ".card{background:#16213e;border-radius:16px;padding:40px;text-align:center;";
  html += "box-shadow:0 8px 32px rgba(0,0,0,0.3);max-width:400px;width:90%}";
  html += "h1{margin:0 0 24px;font-size:22px}";
  html += "input{width:100%;padding:12px;margin:8px 0;border:1px solid #333;";
  html += "border-radius:8px;background:#0f3460;color:#eee;font-size:16px;box-sizing:border-box}";
  html += "button{width:100%;padding:14px;margin-top:16px;border:none;border-radius:8px;";
  html += "background:#4CAF50;color:#fff;font-size:18px;font-weight:600;cursor:pointer}";
  html += "</style></head><body>";
  html += "<div class='card'>";
  html += "<h1>WiFi Setup</h1>";
  html += "<form action='/save' method='POST'>";
  html += "<input name='ssid' placeholder='WiFi Network Name' required>";
  html += "<input name='pass' type='password' placeholder='WiFi Password'>";
  html += "<button type='submit'>Connect</button>";
  html += "</form></div></body></html>";
  return html;
}

// --- Route Handlers ---
void handleRoot() {
  if (apMode) {
    server.send(200, "text/html", buildConfigPage());
  } else {
    server.send(200, "text/html", buildPage());
  }
}

void handleOn() {
  setRelay(true);
  server.sendHeader("Location", "/");
  server.send(303);
}

void handleOff() {
  setRelay(false);
  server.sendHeader("Location", "/");
  server.send(303);
}

void handleToggle() {
  setRelay(!relayState);
  server.sendHeader("Location", "/");
  server.send(303);
}

void handleStatus() {
  String json = "{\"relay\":";
  json += relayState ? "true" : "false";
  json += ",\"uptime\":";
  json += String(millis() / 1000);
  json += ",\"ip\":\"";
  json += WiFi.localIP().toString();
  json += "\",\"rssi\":";
  json += String(WiFi.RSSI());
  json += ",\"heap\":";
  json += String(ESP.getFreeHeap());
  json += "}";
  server.send(200, "application/json", json);
}

void handleSaveConfig() {
  String ssid = server.arg("ssid");
  String pass = server.arg("pass");

  if (ssid.length() == 0) {
    server.send(400, "text/plain", "SSID required");
    return;
  }

  prefs.begin("wifi", false);
  prefs.putString("ssid", ssid);
  prefs.putString("pass", pass);
  prefs.end();

  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  html += "<style>body{font-family:sans-serif;background:#1a1a2e;color:#eee;";
  html += "display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}";
  html += ".card{background:#16213e;border-radius:16px;padding:40px;text-align:center}</style>";
  html += "</head><body><div class='card'>";
  html += "<h2>Connecting to " + ssid + "...</h2>";
  html += "<p>The switch will restart. Find it on your network at:<br>";
  html += "<strong>http://" + deviceName + ".local</strong></p>";
  html += "</div></body></html>";
  server.send(200, "text/html", html);

  delay(2000);
  ESP.restart();
}

void handleReset() {
  prefs.begin("wifi", false);
  prefs.clear();
  prefs.end();
  server.send(200, "text/plain", "WiFi credentials cleared. Restarting...");
  delay(1000);
  ESP.restart();
}

// --- WiFi Connection ---
bool connectWiFi() {
  prefs.begin("wifi", true);
  String ssid = prefs.getString("ssid", "");
  String pass = prefs.getString("pass", "");
  prefs.end();

  if (ssid.length() == 0) {
    return false;
  }

  Serial.printf("[WIFI] Connecting to: %s\n", ssid.c_str());
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid.c_str(), pass.c_str());

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WIFI] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
    return true;
  }

  Serial.println("[WIFI] Connection failed");
  return false;
}

void startAccessPoint() {
  apMode = true;
  uint32_t chipId = ESP.getEfuseMac() & 0xFFFF;
  String apName = "Sarlls-Switch-" + String(chipId, HEX);
  apName.toUpperCase();

  WiFi.mode(WIFI_AP);
  WiFi.softAP(apName.c_str(), "sarlls1234");

  Serial.printf("[AP] Started: %s\n", apName.c_str());
  Serial.printf("[AP] Password: sarlls1234\n");
  Serial.printf("[AP] Config at: http://192.168.4.1\n");
}

// --- Setup ---
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println("================================");
  Serial.println("Sarlls IoT Smart Switch v1.5");
  Serial.println("================================");

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(RELAY_LED_PIN, OUTPUT);
  pinMode(BOOT_PIN, INPUT_PULLUP);

  setRelay(false);

  if (!connectWiFi()) {
    startAccessPoint();
  }

  if (!apMode) {
    if (MDNS.begin(deviceName.c_str())) {
      Serial.printf("[MDNS] http://%s.local\n", deviceName.c_str());
    }
  }

  server.on("/", handleRoot);
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.on("/toggle", handleToggle);
  server.on("/status", handleStatus);
  server.on("/save", HTTP_POST, handleSaveConfig);
  server.on("/reset-wifi", handleReset);
  server.begin();

  Serial.println("[SERVER] Ready");
}

// --- Loop ---
void loop() {
  server.handleClient();

  // Boot button = manual toggle with debounce
  if (digitalRead(BOOT_PIN) == LOW && millis() - lastButtonPress > 300) {
    lastButtonPress = millis();
    setRelay(!relayState);
    while (digitalRead(BOOT_PIN) == LOW) {
      delay(10);
    }
  }

  // Reconnect WiFi if disconnected (station mode only)
  if (!apMode && WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] Reconnecting...");
    WiFi.reconnect();
    delay(5000);
  }
}
