
#define BTN_PIN 2
#define LED_PIN 13

#define LONG_PRESS 3000   // giu > 3s de doi che do
#define DEBOUNCE   30     // chong doi phim
#define CLICK_GAP  1500   // het gio cho dem so lan nhan

bool configMode = false;  // false = VAN HANH, true = CAU HINH
long currentBaud = 9600;

// theo doi nut nhan
bool btnStable = HIGH, btnLast = HIGH;
unsigned long tDebounce = 0, tPress = 0;
bool longDone = false;

// dem so lan nhan trong che do cau hinh
int clicks = 0;
unsigned long tClick = 0;

// nhay LED n lan
void blink(int n, int on, int off) {
  for (int i = 0; i < n; i++) {
    digitalWrite(LED_PIN, HIGH); delay(on);
    digitalWrite(LED_PIN, LOW);  delay(off);
  }
}

// doi baud rate ngay luc chay
void setBaud(long baud) {
  currentBaud = baud;
  Serial.print("Da chon baud: "); Serial.println(baud);
  Serial.flush();
  Serial.end();
  Serial.begin(currentBaud);
  delay(50);
  Serial.print("UART chay o "); Serial.print(currentBaud); Serial.println(" bps");
}

void setup() {
  pinMode(BTN_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(currentBaud);
  Serial.println("=== Che do VAN HANH ===");
  Serial.print("Baud hien tai: "); Serial.println(currentBaud);
}

void loop() {
  bool r = digitalRead(BTN_PIN);

  // chong doi phim
  if (r != btnLast) { tDebounce = millis(); btnLast = r; }

  if (millis() - tDebounce > DEBOUNCE && r != btnStable) {
    btnStable = r;

    if (btnStable == LOW) {          // vua nhan xuong
      tPress = millis();
      longDone = false;
    } else {                        // vua nha ra
      // neu chua tinh la giu-lau va thoi gian < 3s -> la 1 lan nhan ngan
      if (!longDone && millis() - tPress < LONG_PRESS && configMode) {
        clicks++;
        tClick = millis();
        blink(1, 120, 80);
        Serial.print("So lan nhan: "); Serial.println(clicks);
      }
    }
  }

  // giu du 3s -> doi che do
  if (btnStable == LOW && !longDone && millis() - tPress >= LONG_PRESS) {
    longDone = true;
    configMode = !configMode;

    if (configMode) {
      clicks = 0;
      Serial.println(">> Vao CAU HINH (1 nhan = 9600, 2 nhan = 115200)");
      blink(6, 80, 80);             // nhay nhanh bao vao cau hinh
    } else {
      Serial.println(">> Ve VAN HANH");
      Serial.print("Baud dang dung: "); Serial.println(currentBaud);
      blink(2, 300, 200);           // nhay cham bao ve van hanh
    }
  }

  // het gio cho -> chot lua chon baud
  if (configMode && clicks > 0 && millis() - tClick > CLICK_GAP) {
    if (clicks == 1)      setBaud(9600);
    else if (clicks == 2) setBaud(115200);
    else { Serial.println("So lan nhan khong hop le"); blink(4, 60, 60); }
    clicks = 0;
  }
}
