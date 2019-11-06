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
    Adafruit Neopixel by Adafruit
    MAX1704X by Daniel Porrey
    
    Required library but must be manually installed from zip:
    ---------------------------------------------------------
    https://github.com/mristau/Arduino_nRF5x_lowPower
    
    WARNING: You must make some modifications to the default SparkFun nRF52832 Breakout library before
    this code will work:
    
    The default I2C pins must be changed. They are hard-coded in the board's variant.h file located at:
        <user dir>\AppData\Local\Arduino15\packages\SparkFun\hardware\nRF5\0.2.3\variants\SparkFun_nRF52832_Breakout\variant.h
    Change the definitions for PIN_WIRE_SDA and PIN_WIRE_SCL to match I2C_SCL_PIN and I2C_SDA_PIN, defined below.
    See https://learn.sparkfun.com/tutorials/nrf52832-breakout-board-hookup-guide/discuss

    Make sure to restart Arduino IDE after these changes before compiling.
*/

#include <BLEPeripheral.h>          // BLE stuff
#include <Adafruit_Sensor.h>        // Accelerometer
#include <Adafruit_ADXL345_U.h>     // Accelerometer
#include <Adafruit_NeoPixel.h>      // LEDs
#include <Keypad.h>                 // All the buttons!
#include <MAX17043.h>               // Battery fuel gauge
#include <Arduino_nRF5x_lowPower.h> // Low power!

#define DEBUG

//////////////
// Hardware //
//////////////
const int LED_PIN = 7;          // builtin LED, used only for testing
const int BTN_PIN = 6;          // builtin button, used only for testing
const int RESET_PIN = 21;       // reset, bring low to reset device

const int I2C_SCL_PIN = 8;      // make variant.h match!
const int I2C_SDA_PIN = 11;     // make variant.h match!
const int NFC1_PIN = 9;         // can't change these or disable NFC!
const int NFC2_PIN = 10;        // can't change these or disable NFC!

const int ACC_INT1_PIN = 3;     // interrupt on rising, wakeup on rising
const int ACC_INT2_PIN = 2;     // not used

const int PS_CHARGER_PIN = 5;       // input, wakeup on rising
const int PS_CHARGING_PIN = 4;      // input
const int PS_CHARGER_ENABLE_PIN = 12;  // output, active high to disable, input float to enable
const int PS_LED_ENABLE_PIN = 13;   // output, active high to enable

const int LEDS_PIN = 16;

uint8_t KEYPAD_ROW_PINS[] = {17, 18, 19, 20, 22, 23};
uint8_t KEYPAD_COL_PINS[] = {24, 25, 28, 29, 30, 31};

///////////////
// Neopixels //
///////////////
typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} color_t;
const color_t LED_OFF = {0, 0, 0};
const color_t LED_RED = {127, 0, 0};
const color_t LED_GREEN = {0, 127, 0};
const color_t LED_BLUE = {0, 0, 127};
const color_t LED_WHITE = {127, 127, 127};
const color_t LEDS_OFF[] = {LED_OFF, LED_OFF, LED_OFF, LED_OFF, LED_OFF};
const color_t LEDS_GREEN[] = {LED_GREEN, LED_GREEN, LED_GREEN, LED_GREEN, LED_GREEN};
//const color_t LEDS_OFF[] = {LED_OFF{0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}};
//const color_t LEDS_ON[] = {{127, 127, 127}, {127, 127, 127}, {127, 127, 127}, {127, 127, 127}, {127, 127, 127}};
const unsigned long LEDS_BLINK_INTERVAL = 500;
const int LEDS_DATA_LENGTH = sizeof(LEDS_OFF);
const int LEDS_NUMPIXELS = 5;
const float LEDS_LOW_BATTERY_LEVEL = 30.0;
Adafruit_NeoPixel leds = Adafruit_NeoPixel(LEDS_NUMPIXELS, LEDS_PIN, NEO_GRB + NEO_KHZ800);
color_t ledsValue[5] = {};
bool ledsBlink;
bool ledsBlinkOn;
unsigned long ledsLastBlink;

///////////////
// Bluetooth //
///////////////
const char* BLE_NAME = "RemoteControl";
const unsigned short BLE_ADVERTISING_INTERVAL = 50;
BLEPeripheral blePeriph;
BLEService bleServ("1234");
BLEUnsignedCharCharacteristic buttonDownChar("0001", BLERead | BLENotify);
BLEUnsignedCharCharacteristic buttonUpChar("0002", BLERead | BLENotify);
BLEFixedLengthCharacteristic ledsChar("0003", BLERead | BLEWrite, LEDS_DATA_LENGTH);
BLEUnsignedCharCharacteristic chargingChar("0004", BLERead | BLENotify);
BLEFloatCharacteristic batteryLevelChar("0005", BLERead | BLENotify);
BLEUnsignedCharCharacteristic resetChar("0099", BLEWrite);

////////////
// Keypad //
////////////
const uint8_t KEYPAD_ROWS = sizeof(KEYPAD_ROW_PINS);
const uint8_t KEYPAD_COLS = sizeof(KEYPAD_COL_PINS);
char KEYPAD_MAP[KEYPAD_ROWS][KEYPAD_COLS] = {
    {0x11, 0x12, 0x13, 0x14, 0x15, 0x16},
    {0x21, 0x22, 0x23, 0x24, 0x25, 0x26},
    {0x31, 0x32, 0x33, 0x34, 0x35, 0x36},
    {0x41, 0x42, 0x43, 0x44, 0x45, 0x46},
    {0x51, 0x52, 0x53, 0x54, 0x55, 0x56},
    {0x61, 0x62, 0x63, 0x64, 0x65, 0x66}
};
Keypad keypad = Keypad(makeKeymap(KEYPAD_MAP), KEYPAD_ROW_PINS, KEYPAD_COL_PINS, KEYPAD_ROWS, KEYPAD_COLS);
bool keypadIdle;

///////////////////
// Accelerometer //
///////////////////
bool accelSetup = false;
const uint8_t ACC_ADDRESS = 0x1d;
const range_t ACCEL_RANGE = ADXL345_RANGE_2_G;
const dataRate_t ACCEL_RATE = ADXL345_DATARATE_25_HZ;
const float ACCEL_THRESHOLD = 1.5;
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();
bool accelIdle;
volatile bool accelInterrupted = false;

/*
const unsigned long ACCEL_READ_INTERVAL = 500;
typedef struct {
    float x;
    float y;
    float z;
} accel_data_t;
*/
//sensors_event_t accelEvent;  
//accel_data_t accelLastValue;
//unsigned long accelLastRead;
//float accelValue = 0;

//////////////////
// Power supply //
//////////////////
bool psSetup = false;
const unsigned long PS_CHECK_INTERVAL = 1000;
unsigned long psLastCheck;
bool psOnCharger = false;
bool psCharging = false;
bool psBatteryLevelChanged = false;
float psBatteryLevel = 0;

//////////
// Idle //
//////////
const unsigned long IDLE_THRESHOLD = 10000;
bool isIdle;
unsigned long idleStart;



void setup() {
    digitalWrite(LED_PIN, LOW); // turn on built-in LED
#ifdef DEBUG
    Serial.begin(9600);
#endif

    setupLEDs();
    setupBluetooth();
    setupKeypad();
    setupAccel();
    setupPowerSupply();
    
#ifdef DEBUG
    Serial.println("Ready");
#endif
    digitalWrite(LED_PIN, HIGH); // turn off built-in LED
}

void loop() {
    loopLEDs();
    loopBluetooth();
    loopKeypad();
    loopAccel();
    loopPowerSupply();
    
    checkIdle();
}


void setupBluetooth() {
    pinMode(BTN_PIN, INPUT_PULLUP);
    digitalWrite(LED_PIN, HIGH);
    
    blePeriph.setDeviceName(BLE_NAME);
    blePeriph.setLocalName(BLE_NAME);
    blePeriph.setAdvertisedServiceUuid(bleServ.uuid());
    blePeriph.setAdvertisingInterval(BLE_ADVERTISING_INTERVAL);
    
    // Add service
    blePeriph.addAttribute(bleServ);

    // Add characteristics
    blePeriph.addAttribute(buttonDownChar);
    blePeriph.addAttribute(buttonUpChar);
    blePeriph.addAttribute(ledsChar);
    blePeriph.addAttribute(chargingChar);
    blePeriph.addAttribute(batteryLevelChar);
    blePeriph.addAttribute(resetChar);

    // Initialize characteristic values
    buttonDownChar.setValue(0);
    buttonUpChar.setValue(0);
    ledsChar.setValue((unsigned char*)ledsValue, LEDS_DATA_LENGTH);
    chargingChar.setValue(psCharging);
    batteryLevelChar.setValue(psBatteryLevel);

    // Initialize BLE:
    blePeriph.begin();

#ifdef DEBUG
    Serial.println("BLE setup");
#endif
    
}

void loopBluetooth() {
    blePeriph.poll();

    char buttonValue = digitalRead(BTN_PIN);
    static char lastButtonValue = HIGH;
    
    if (buttonValue != lastButtonValue) {
        lastButtonValue = buttonValue;
        
#ifdef DEBUG
        Serial.print("Button: ");
        Serial.print(buttonValue, DEC);
        Serial.println();
#endif

        if (buttonValue == LOW) {
            buttonDownChar.setValue(0x99);
            buttonUpChar.setValue(0);
        } else {
            buttonUpChar.setValue(0x99);
            buttonDownChar.setValue(0);
        }
    }
    
    if (ledsChar.written()) {
        const unsigned char* ledsState = ledsChar.value();
        memcpy(ledsValue, ledsState, LEDS_DATA_LENGTH);
        setLEDs();
#ifdef DEBUG
        dumpLEDs(ledsValue);
#endif
    }
    if (resetChar.written()) {
#ifdef DEBUG
        Serial.println("Resetting...");
#endif
        delay(1000);
        digitalWrite(RESET_PIN, LOW);
    }
}

void setupKeypad() {
    keypad.addEventListener(keypadEvent);
#ifdef DEBUG
    Serial.println("Keypad setup");
#endif
}

void loopKeypad() {
    keypadIdle = !keypad.getKey();
}

void keypadEvent(KeypadEvent key) {
    switch (keypad.getState()) {
        case PRESSED:
            buttonDownChar.setValue(key);
            buttonUpChar.setValue(0);
#ifdef DEBUG
            Serial.print("Key down: ");
            Serial.println(key);
#endif
            break;
        case RELEASED:
            buttonUpChar.setValue(key);
            buttonDownChar.setValue(0);
#ifdef DEBUG
            Serial.print("Key up: ");
            Serial.println(key);
#endif
            break;
    }
}

void setupAccel() {
    if (!accel.begin(ACC_ADDRESS)) {
#ifdef DEBUG
        Serial.println("ADXL345 not detected!");
#endif
        return;
    }
    accel.setRange(ACCEL_RANGE);
    accel.setDataRate(ACCEL_RATE);
    
    pinMode(ACC_INT1_PIN, INPUT_PULLDOWN);
    pinMode(ACC_INT2_PIN, INPUT_PULLDOWN);  // not used
    
    accel.writeRegister(ADXL345_REG_INT_ENABLE, 0);         // disable interrupts
    accel.writeRegister(ADXL345_REG_INT_MAP, 0);            // map all interrupts to INT1
    accel.writeRegister(ADXL345_REG_POWER_CTL, 0);          // turn off link and put in standby
    accel.writeRegister(ADXL345_REG_ACT_INACT_CTL, 0xf0);   // ac-coupled x, y, z activity
    accel.writeRegister(ADXL345_REG_THRESH_ACT, ACCEL_THRESHOLD * 1000.0 / 62.5);
    accel.writeRegister(ADXL345_REG_INT_ENABLE, 0x10);      // enable activity interrupt
    accel.writeRegister(ADXL345_REG_POWER_CTL, 0x08);       // turn on measurement mode
    accel.readRegister(ADXL345_REG_INT_SOURCE);             // read to clear any interrupts
    
    attachInterrupt(digitalPinToInterrupt(ACC_INT1_PIN), accelInterrupt, RISING);
    accelSetup = true;
#ifdef DEBUG
    Serial.println("ADXL345 setup");
#endif
}

void accelInterrupt() {
    accelInterrupted = true;
}

void loopAccel() {
    if (! accelSetup) return;
    
    if (accelInterrupted) {
        accelInterrupted = false;
        accelIdle = false;
        accel.readRegister(ADXL345_REG_INT_SOURCE); // read to clear interrupts
    } else
        accelIdle = true;
}

void setupPowerSupply() {
    pinMode(PS_CHARGER_PIN, INPUT_PULLDOWN);    // pulldown isn't really needed
    pinMode(PS_CHARGING_PIN, INPUT_PULLUP);

    pinMode(PS_CHARGER_ENABLE_PIN, OUTPUT);     // enable charger managment
    digitalWrite(PS_CHARGER_ENABLE_PIN, HIGH);     // disable charger
    
    pinMode(PS_LED_ENABLE_PIN, OUTPUT);
    digitalWrite(PS_LED_ENABLE_PIN, HIGH);     // enable leds
    
    pinMode(RESET_PIN, OUTPUT);
    digitalWrite(RESET_PIN, HIGH);
    
    FuelGauge.begin();
    if (FuelGauge.version() == 0xffff) {
#ifdef DEBUG
        Serial.println("MAX17043 not detected!");
#endif
        return;
    }
    // TODO: put fuel gauge in active mode (library doesn't support this)
    psLastCheck = millis();
    psSetup = true;
#ifdef DEBUG
    Serial.println("MAX17043 setup");
#endif
}

void loopPowerSupply() {
    // TODO: remove comment
    //if (! psSetup) return;
    if ((millis() - psLastCheck) < PS_CHECK_INTERVAL) return;
    psLastCheck = millis();
    
    bool charger = digitalRead(PS_CHARGER_PIN);
    if (charger && !psOnCharger) {
        psOnCharger = true;
        psBatteryLevelChanged = true;
        pinMode(PS_CHARGER_ENABLE_PIN, INPUT); // enable charger
    } else if (!charger && psOnCharger) {
        psOnCharger = false;
        psBatteryLevelChanged = true;
        pinMode(PS_CHARGER_ENABLE_PIN, OUTPUT);     // enable charger managment
        digitalWrite(PS_CHARGER_ENABLE_PIN, HIGH);     // disable charger
    }

    bool charging = !digitalRead(PS_CHARGING_PIN);
    if (psOnCharger && charging && !psCharging) {
        psCharging = true;
        psBatteryLevelChanged = true;
        chargingChar.setValue(1);
#ifdef DEBUG
        Serial.println("Started charging");
#endif
    } else if (!psOnCharger || (!charging && psCharging)) {
        psCharging = false;
        psBatteryLevelChanged = true;
        chargingChar.setValue(0);
#ifdef DEBUG
        Serial.println("Stopped charging");
#endif
    }
    
    // TODO: remove comment
    //float level = (int)FuelGauge.percent();
    // TODO: remove line
    float level = (int)20.0;
    
    if (level != psBatteryLevel) {
        psBatteryLevel = level;
        psBatteryLevelChanged = true;
        batteryLevelChar.setValue(psBatteryLevel);
#ifdef DEBUG
        Serial.print("Battery level: ");
        Serial.println(level);
#endif
    }
}

void setupLEDs() {
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);
    leds.begin();
    setLEDs(LEDS_OFF);
    memcpy(ledsValue, LEDS_OFF, LEDS_DATA_LENGTH);
#ifdef DEBUG
    Serial.println("LEDs setup");
#endif
}

void loopLEDs() {
    if (psOnCharger) {
        if (psBatteryLevelChanged) {
            psBatteryLevelChanged = false;
            if (psCharging) {
                digitalWrite(LED_PIN, LOW);
                color_t colors[LEDS_NUMPIXELS];
                for (int i = 0; i < LEDS_NUMPIXELS; i++) {
                    bool on = psBatteryLevel >= (((float)i * 100.0 / (float)LEDS_NUMPIXELS) + (50.0 / (float)LEDS_NUMPIXELS));
                    memcpy(&colors[i], on ? &LED_RED : &LED_OFF, sizeof(color_t));
                }
                setLEDs(colors);
            } else {
                digitalWrite(LED_PIN, HIGH);
                setLEDs(LEDS_GREEN);
            }
        }
        return;
    }
    
    if (psBatteryLevelChanged) {
        psBatteryLevelChanged = false;
        digitalWrite(LED_PIN, HIGH);
        if (psBatteryLevel < LEDS_LOW_BATTERY_LEVEL) {
            if (!ledsBlink) {
                ledsBlink = true;
                ledsBlinkOn = true;
                ledsLastBlink = millis() - LEDS_BLINK_INTERVAL;
            }
        } else {
            ledsBlink = false;
            setLEDs(ledsValue);
        }
    }
    
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

void setLEDs() {
    if (ledsBlink) return;
    setLEDs(ledsValue);
}
    
void setLEDs(const color_t values[]) {
    for(int i = 0; i < LEDS_NUMPIXELS; i++)
        leds.setPixelColor(i, values[i].red, values[i].green, values[i].blue);
    leds.show();
}

void dumpLEDs(color_t leds[]) {
    Serial.print("LEDs: ");
    for (int i = 0; i < LEDS_NUMPIXELS; i++) {
        if (i > 0)
            Serial.print(", ");
        Serial.print(leds[i].red);
        Serial.print(':');
        Serial.print(leds[i].green);
        Serial.print(':');
        Serial.print(leds[i].blue);
    }
    Serial.println();
}
    
void checkIdle() {
    if (psOnCharger) {
        isIdle = false;
        return;
    }
    
    if (keypadIdle && accelIdle) {
        if (!isIdle) {
            isIdle = true;
            idleStart = millis();
        } else if ((idleStart != 0) && ((millis() - idleStart) > IDLE_THRESHOLD)) {
#ifdef DEBUG
            Serial.println("Going to sleep");
#endif            
            idleStart = 0;
            enterSleep();
        }
    } else {
        if (isIdle) {
            isIdle = false;
            if (idleStart == 0) {
#ifdef DEBUG
                Serial.println("Waking up");
#endif
                // Should never be here
            }
        }
    }
}

void enterSleep() {
    setLEDs(LEDS_OFF);
    digitalWrite(PS_LED_ENABLE_PIN, LOW);  // disble leds
    // TODO: put fuel gauge in hibernate mode (library doesn't support this)
    // charger should already be disabled
    nRF5x_lowPower.enableWakeupByInterrupt(ACC_INT1_PIN, RISING);
    nRF5x_lowPower.enableWakeupByInterrupt(PS_CHARGER_PIN, RISING);
    nRF5x_lowPower.powerMode(POWER_MODE_OFF);
}

    
