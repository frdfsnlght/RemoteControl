/*
    Firmware for Remote Control project using SparkFun nRF52832 Breakout
    https://www.sparkfun.com/products/13990
    
    Hardware:
    --------------
    SparkFun nRF52832 Breakout
    ADXL345 Digital Accelerometer (eBay generic)
    MAX17048 LiPo Fuel Gauge (custom PCB with LiPo charger)
    Neopixels
    
    Required libraries:
    -------------------
    Adafruit ADXL345 by Adafruit
    Adafruit Unified Sensor by Adafruit
    BLEPeripheral by Sandeep Mistry
    Keypad by Mark Stanley, Alexander Brevig
    
    TODO: add fuel gauge library
    * Adafruit Neopixel by Adafruit
    * Arduio Low Power by Arduino
    
    WARNING: You must make some modifications to the default SparkFun nRF52832 Breakout library before
    this code will work:
    
    The default I2C pins must be changed. They are hard-coded in the board's varient.h file located at:
        <user dir>\AppData\Local\Arduino15\packages\SparkFun\hardware\nRF5\0.2.3\variants\SparkFun_nRF52832_Breakout\varient.h
    Change the definitions for PIN_WIRE_SDA and PIN_WIRE_SCL.
    See https://learn.sparkfun.com/tutorials/nrf52832-breakout-board-hookup-guide/discuss

    Make sure to restart Arduino IDE after these changes before compiling.
*/

#include <SPI.h>                    // BLEPeripheral depends on this
#include <Wire.h>                   // For I2C
#include <BLEPeripheral.h>          // BLE stuff
#include <Adafruit_Sensor.h>        // Accelerometer
#include <Adafruit_ADXL345_U.h>     // Accelerometer
#include <Keypad.h>                 // All the buttons!
#include <Adafruit_NeoPixel.h>      // LEDs


//////////////
// Hardware //
//////////////
const int LED_PIN = 7;          // builtin LED, used only for testing
const int BTN_PIN = 6;          // builtin button, used only for testing
const int I2C_SCL_PIN = 2;
const int I2C_SDA_PIN = 3;
const int ACC_INT2_PIN = 4;
const int ACC_INT1_PIN = 5;
const int ACC_CS_PIN = 8;
const int BAT_QSTRT_PIN = 9;
const int BAT_ALRT_PIN = 10;
const int BAT_STAT_PIN = 11;
byte KEYPAD_ROW_PINS[] = {16, 17, 18, 19};
byte KEYPAD_COL_PINS[] = {20, 22, 23};
const int LEDS_PIN = 15;


///////////////
// Neopixels //
///////////////
typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} color_t;
const color_t LEDS_OFF[5] = {};
//const color_t LEDS_OFF[] = {{0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}};
const unsigned long LEDS_BLINK_INTERVAL = 500;
const int LEDS_DATA_LENGTH = sizeof(LEDS_OFF);
const int LEDS_NUMPIXELS = 5;
Adafruit_NeoPixel leds = Adafruit_NeoPixel(LEDS_NUMPIXELS, LEDS_PIN, NEO_GRB + NEO_KHZ800);
color_t ledsValue[5] = {};
bool ledsBlink;
bool ledsBlinkOn;
unsigned long ledsLastBlink;

///////////////
// Bluetooth //
///////////////
const char* localName = "RemoteControl";
BLEPeripheral blePeriph;
BLEService bleServ("1234");
BLEUnsignedCharCharacteristic ledChar("1234-LED", BLERead | BLEWrite);
BLECharCharacteristic buttonDownChar("1234-BTN-DOWN", BLERead | BLENotify);
BLECharCharacteristic buttonUpChar("1234-BTN-UP", BLERead | BLENotify);
BLEFixedLengthCharacteristic ledsChar("1234-BTN-UP", BLERead | BLEWrite, LEDS_DATA_LENGTH);

////////////
// Keypad //
////////////
const uint8_t KEYPAD_ROWS = sizeof(KEYPAD_ROW_PINS);
const uint8_t KEYPAD_COLS = sizeof(KEYPAD_COL_PINS);
char KEYPAD_MAP[KEYPAD_ROWS][KEYPAD_COLS] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};
Keypad keypad = Keypad(makeKeymap(KEYPAD_MAP), KEYPAD_ROW_PINS, KEYPAD_COL_PINS, KEYPAD_ROWS, KEYPAD_COLS);
bool keypadIdle;

///////////////////
// Accelerometer //
///////////////////
bool accelSetup = false;
const unsigned long ACCEL_READ_INTERVAL = 500;
const float ACCEL_THRESHOLD = 1;
typedef struct {
    float x;
    float y;
    float z;
} accel_data_t;
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();
sensors_event_t accelEvent;  
accel_data_t accelLastValue;
unsigned long accelLastRead;
bool accelIdle;

///////////////////////////
// Charger/battery level //
///////////////////////////

// TODO: charger and battery stuff


//////////
// Idle //
//////////
const unsigned long IDLE_THRESHOLD = 10000;
bool isIdle;
unsigned long idleStart;



void setup() {
    Serial.begin(9600);

    setupBLETest();
    
    setupKeypad();
    setupAccel();
    setupLEDs();
    
    Serial.println("Ready");
}

void loop() {
    loopBLETest();
    
    loopKeypad();
    loopAccel();
    loopLEDs();
    
    checkIdle();
}


//======================================================
// Testing
//

void setupBLETest() {
    pinMode(LED_PIN, OUTPUT);
    pinMode(BTN_PIN, INPUT_PULLUP);
    digitalWrite(LED_PIN, HIGH);
    
    blePeriph.setDeviceName(localName);
    blePeriph.setLocalName(localName);
    blePeriph.setAdvertisedServiceUuid(bleServ.uuid());

    // Add service
    blePeriph.addAttribute(bleServ);

    // Add characteristics
    blePeriph.addAttribute(ledChar);
    blePeriph.addAttribute(buttonDownChar);
    blePeriph.addAttribute(buttonUpChar);
    blePeriph.addAttribute(ledsChar);

    blePeriph.setEventHandler(BLEConnected, bleConnectedHandler);
    blePeriph.setEventHandler(BLEDisconnected, bleDisconnectedHandler);
    
    // Now that device, service, characteristics are set up,
    // initialize BLE:
    blePeriph.begin();

    // Initialize characteristic values
    ledChar.setValue(0);
    buttonDownChar.setValue(0);
    buttonUpChar.setValue(0);
    ledsChar.setValue((char*)LEDS_OFF);
    
    Serial.println("BLE setup");
    
}

void loopBLETest() {
    blePeriph.poll();

    char buttonValue = digitalRead(BTN_PIN);
    static char lastButtonValue = HIGH;
    
    if (buttonValue != lastButtonValue) {
        lastButtonValue = buttonValue;
        
        Serial.print("Button: ");
        Serial.print(buttonValue);
        Serial.println();
        
        if (buttonValue == LOW) {
            buttonDownChar.setValue('A');
            buttonUpChar.setValue(0);
        } else {
            buttonUpChar.setValue('A');
            buttonDownChar.setValue(0);
        }
    }
    
    if (ledChar.written()) {
        int ledState = ledChar.value();
        Serial.print("LED: ");
        Serial.print(ledState);
        Serial.println();
        digitalWrite(LED_PIN, ledState ? LOW : HIGH);
    }
    
    if (ledsChar.written()) {
        const unsigned char* ledsState = ledsChar.value();
        memcpy(ledsValue, ledsState, sizeof(ledsState));
        setLEDs();
        Serial.print("LEDs: ");
        for (int i = 0; i < LEDS_DATA_LENGTH; i++) {
            if (i > 0)
                Serial.print(", ");
            Serial.print((int)ledsState[i]);
        }
        Serial.println();
    }
    
}

void bleConnectedHandler(BLECentral& central) {
    Serial.println("BLE Connected");
    Serial.print("Address: ");
    Serial.println(central.address());
}

void bleDisconnectedHandler(BLECentral& central) {
    Serial.println("BLE Disconnected");
}

void setupKeypad() {
    keypad.addEventListener(keypadEvent);
    Serial.println("Keypad setup");
}

void loopKeypad() {
    keypadIdle = !keypad.getKey();
}

void keypadEvent(KeypadEvent key) {
    switch (keypad.getState()) {
        case PRESSED:
            Serial.print("Key down: ");
            Serial.println(key);
            buttonDownChar.setValue(key);
            buttonUpChar.setValue(0);
            break;
        case RELEASED:
            Serial.print("Key up: ");
            Serial.println(key);
            buttonUpChar.setValue(key);
            buttonDownChar.setValue(0);
            break;
    }
}

void setupAccel() {
    if (!accel.begin()) {
        Serial.println("ADXL345 not detected!");
        return;
    }
    accel.setRange(ADXL345_RANGE_2_G);
    accel.setDataRate(ADXL345_DATARATE_25_HZ);
    
    // TODO: setup interrupt/threshold
    
    accelSetup = true;
    Serial.println("ADXL345 setup");
}

void loopAccel() {
    if (! accelSetup) return;
    if ((millis() - accelLastRead) < ACCEL_READ_INTERVAL) return;
    
    accel.getEvent(&accelEvent);
    accelLastRead = millis();

    accel_data_t diff;
    diff.x = abs(accelEvent.acceleration.x - accelLastValue.x);
    diff.y = abs(accelEvent.acceleration.y - accelLastValue.y);
    diff.z = abs(accelEvent.acceleration.z - accelLastValue.z);
    accelLastValue.x = accelEvent.acceleration.x;
    accelLastValue.y = accelEvent.acceleration.y;
    accelLastValue.z = accelEvent.acceleration.z;
    
    float totalDiff = diff.x + diff.y + diff.z;
    
    Serial.print("Acceleration: ");
    Serial.println(totalDiff);
    
    accelIdle = totalDiff < ACCEL_THRESHOLD;
}

void setupLEDs() {
    leds.begin();
    setLEDs(LEDS_OFF);
    Serial.println("LEDs setup");
}

void loopLEDs() {
    if (ledsBlink) {
        if ((millis() - ledsLastBlink) >= LEDS_BLINK_INTERVAL) {
            ledsLastBlink = millis();
            ledsBlinkOn = !ledsBlinkOn;
            if (ledsBlinkOn)
                setLEDs(ledsValue);
            else
                setLEDs(LEDS_OFF);
        }
    } else if (! ledsBlinkOn)
        setLEDs(ledsValue);
}

void startBlinkingLEDs() {
    if (ledsBlink) return;
    ledsBlink = true;
    ledsBlinkOn = true;
    ledsLastBlink = millis() - LEDS_BLINK_INTERVAL;
    loopLEDs();
}

void stopBlinkingLEDs() {
    ledsBlink = false;
}

void setLEDs() {
    if (ledsBlink) return;
    setLEDs(ledsValue);
}
    
void setLEDs(const color_t values[]) {
    for(int i = 0; i < LEDS_NUMPIXELS; i++)
        leds.setPixelColor(i, values[i].red, values[i].green, values[i].blue);
    leds.show();
}

    
void checkIdle() {
    // TODO: don't idle if charging
    
    if (keypadIdle && accelIdle) {
        if (!isIdle) {
            isIdle = true;
            idleStart = millis();
        } else if ((millis() - idleStart) > IDLE_THRESHOLD) {
            Serial.println("Going to sleep");
            idleStart = 0;
            
            // TODO: enable accelerometer interrupt, turn off LEDs, go to sleep
            
        }
    } else {
        if (isIdle) {
            isIdle = false;
            if (idleStart == 0) {
                Serial.println("Waking up");
            
                // TODO: disable accelerometer interrupt, turn on LEDs
            }
        }
    }
}

