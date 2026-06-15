// ============================================================
//  SIMULATION.ino  —  upload identical binary to both boards
//
//  rfc2217ServerPort in wokwi.toml exposes UART0 (Serial).
//  So Serial IS the inter-board link.
//  Debug prints are removed to avoid polluting the link.
// ============================================================

// ── Button pins (INPUT_PULLUP, pressed = LOW) ──────────────
const int button1 = 25;
const int button2 = 26;
const int button3 = 27;

// ── LED pins (driven by REMOTE board's button state) ───────
const int led1 = 16;
const int led2 = 17;
const int led3 = 4;

// ── Indicator LED (always ON while running) ────────────────
const int indicator = 14;

// ── Protocol: 2-byte frame  [ 0xAA | state ] ──────────────
//    state bits:  bit0 = btn1,  bit1 = btn2,  bit2 = btn3

uint8_t lastSent = 0xFF;   // forces a send on first loop

void setup() {
  // UART0 = the RFC2217 link (exposed by wokwi.toml)
  Serial.begin(115200);
  delay(500);

  pinMode(button1, INPUT_PULLUP);
  pinMode(button2, INPUT_PULLUP);
  pinMode(button3, INPUT_PULLUP);

  pinMode(led1,      OUTPUT);
  pinMode(led2,      OUTPUT);
  pinMode(led3,      OUTPUT);
  pinMode(indicator, OUTPUT);

  digitalWrite(indicator, HIGH);
}

void loop() {
  // ── 1. Read local buttons ──────────────────────────────
  uint8_t state = 0;
  if (digitalRead(button1) == LOW) state |= 0b001;
  if (digitalRead(button2) == LOW) state |= 0b010;
  if (digitalRead(button3) == LOW) state |= 0b100;

  // ── 2. Transmit only when state changes ───────────────
  if (state != lastSent) {
    Serial.write(0xAA);
    Serial.write(state);
    lastSent = state;
  }

  // ── 3. Receive remote state → drive LEDs ──────────────
  while (Serial.available() >= 2) {
    if (Serial.peek() == 0xAA) {
      Serial.read();                      // consume start byte
      uint8_t remoteState = Serial.read();
      digitalWrite(led1, (remoteState & 0b001) ? HIGH : LOW);
      digitalWrite(led2, (remoteState & 0b010) ? HIGH : LOW);
      digitalWrite(led3, (remoteState & 0b100) ? HIGH : LOW);
    } else {
      Serial.read();                      // discard garbage, resync
    }
  }

  delay(20);
}
