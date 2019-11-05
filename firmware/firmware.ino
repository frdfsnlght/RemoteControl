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

    
    * Arduio Low Power by Arduino
    
    WARNING: You must make some modifications to the default SparkFun nRF52832 Breakout library before
    this code will work:
    
    The default I2C pins must be changed. They are hard-coded in the board's varient.h file located at:
        <user dir>\AppData\Local\Arduino15\packages\SparkFun\hardware\nRF5\0.2.3\variants\SparkFun_nRF52832_Breakout\variant.h
    Change the definitions for PIN_WIRE_SDA and PIN_WIRE_SCL to match I2C_SCL_PIN and I2C_SDA_PIN, defined below.
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
#include <MAX17043.h>               // Battery fuel gauge
#include <Arduino_nRF5x_lowPower.h> // Low power!

#define DEBUG

//////////////
// Hardware //
//////////////
const int LED_PIN = 7;          // builtin LED, used only for testing
const int BTN_PIN = 6;          // builtin button, used only for testing

const int I2C_SCL_PIN = 8;      // make varient.h match!
const int I2C_SDA_PIN = 11;     // make varient.h match!
const int NFC1_PIN = 9;         // can't change these or disable NFC!
const int NFC2_PIN = 10;        // can't change these or disable NFC!

const int ACC_INT1_PIN = 3;     // interrupt on rising
const int ACC_INT2_PIN = 2;     // not used

const int BAT_CHG_PRESENT_PIN = 5;  // input, interrupt on rising, wakeup
const int BAT_CHARGING_PIN = 4;     // input, interrupt on falling, wakeup
const int BAT_CHG_ENABLE_PIN = 12;  // output, active high to disable, input float to enable
const int BAT_LED_ENABLE_PIN = 13;  // output, active high

const int LEDS_PIN = 16;

byte KEYPAD_ROW_PINS[] = {17, 18, 19, 20, 22, 23};
byte KEYPAD_COL_PINS[] = {24, 25, 28, 29, 30, 31};

///////////////
// Neopixels //
///////////////
typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} color_t;
const color_t LEDS_OFF[] = {{0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}};
const color_t LEDS_ON[] = {{127, 127, 127}, {127, 127, 127}, {127, 127, 127}, {127, 127, 127}, {127, 127, 127}};
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
BLEFloatCharacteristic batteryChar("0005", BLERead | BLENotify);
BLEFloatCharacteristic accelChar("0006", BLERead | BLENotify);

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
const uint8_t ACC_ADDRESS = 0x1d;
const unsigned long ACCEL_READ_INTERVAL = 500;
const float ACCEL_THRESHOLD = 1.5;
typedef struct {
    float x;
    float y;
    float z;
} accel_data_t;
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();
sensors_event_t accelEvent;  
accel_data_t accelLastValue;
unsigned long accelLastRead;
float accelValue = 0;
bool accelIdle;
volatile bool accelInterrupted = false;

///////////////////////////
// Charger/battery level //
///////////////////////////
bool batterySetup = false;
const unsigned long BATTERY_READ_INTERVAL = 1000;
unsigned long batteryLastRead;
bool batteryCharging = false;
bool batteryStateChanged = false;
float batteryLevel = 0;

//////////
// Idle //
//////////
const unsigned long IDLE_THRESHOLD = 10000;
bool isIdle;
unsigned long idleStart;



void setup() {
    digitalWrite(LED_PIN, LOW);
#ifdef DEBUG
    Serial.begin(9600);
#endif

    setupLEDs();
    setupBluetooth();
    setupKeypad();
    setupAccel();
    setupBattery();
    
#ifdef DEBUG
    Serial.println("Ready");
#endif
    digitalWrite(LED_PIN, HIGH);
}

void loop() {
    loopLEDs();
    loopBluetooth();
    loopKeypad();
    loopAccel();
    loopBattery();
    
    checkIdle();
}


//======================================================
// Testing
//

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
    blePeriph.addAttribute(batteryChar);
    blePeriph.addAttribute(accelChar);

    // Initialize characteristic values
    buttonDownChar.setValue(0);
    buttonUpChar.setValue(0);
    ledsChar.setValue((unsigned char*)ledsValue, LEDS_DATA_LENGTH);
    chargingChar.setValue(batteryCharging);
    batteryChar.setValue(batteryLevel);

    //blePeriph.setEventHandler(BLEConnected, bleConnectedHandler);
    //blePeriph.setEventHandler(BLEDisconnected, bleDisconnectedHandler);
    
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
            buttonDownChar.setValue('A');
            buttonUpChar.setValue(0);
        } else {
            buttonUpChar.setValue('A');
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
    
}

/*
void bleConnectedHandler(BLECentral& central) {
    Serial.println("BLE Connected");
    Serial.print("Central address: ");
    Serial.println(central.address());
}

void bleDisconnectedHandler(BLECentral& central) {
    Serial.println("BLE Disconnected");
}
*/

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
    accel.setRange(ADXL345_RANGE_2_G);
    accel.setDataRate(ADXL345_DATARATE_25_HZ);
    
    pinMode(ACC_INT1_PIN, INPUT_PULLDOWN);
    pinMode(ACC_INT2_PIN, INPUT_PULLDOWN);
    
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
    }
    
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
    
    if (totalDiff != accelValue) {
        accelValue = totalDiff;
        accelChar.setValue(accelValue);
        accelIdle = accelValue < (ACCEL_THRESHOLD * 3);
    }
    
}

void setupBattery() {
    pinMode(BAT_CHG_PRESENT_PIN, INPUT_PULLDOWN);
    pinMode(BAT_CHARGING_PIN, INPUT_PULLUP);
    pinMode(BAT_LED_ENABLE_PIN, OUTPUT);
    pinMode(BAT_CHG_ENABLE_PIN, OUTPUT);

    // TODO: does LED_ENABLE need a pulldown?
    digitalWrite(BAT_LED_ENABLE_PIN, LOW);      // disable leds
    digitalWrite(BAT_CHG_ENABLE_PIN, HIGH);     // disable charger
    
    //digitalWrite(BAT_LED_ENABLE_PIN, HIGH);      // enable leds
    //digitalWrite(BAT_CHG_ENABLE_PIN, LOW);       // never do this!
    
//    attachInterrupt(digitalPinToInterrupt(BAT_STAT_PIN), batteryInterrupt, FALLING);

    FuelGauge.begin();
    if (FuelGauge.version() == 0xffff) {
#ifdef DEBUG
        Serial.println("MAX17043 not detected!");
#endif
        return;
    }
    batteryLastRead = millis(); // to prevent reading the battery too soon
    batterySetup = true;
#ifdef DEBUG
    Serial.println("MAX17043 setup");
#endif
}

//volatile bool batteryInterrupted = false;
/*
void batteryInterrupt() {
    batteryInterrupted = true;
}
*/


void loopBattery() {
//    if (! batterySetup) return;
    if ((millis() - batteryLastRead) < BATTERY_READ_INTERVAL) return;
  
//    float level = (int)FuelGauge.percent();
float level = (int)20.0;
    batteryLastRead = millis();
    
    /*
    // TODO: redo this to handle charger/charging
    bool charging = !digitalRead(BAT_STAT_PIN);
    if (charging && !batteryCharging) {
        batteryCharging = true;
        batteryStateChanged = true;
        chargingChar.setValue(1);
#ifdef DEBUG
        Serial.println("Started charging");
#endif
    } else if (!charging && batteryCharging) {
        batteryCharging = false;
        batteryStateChanged = true;
        chargingChar.setValue(0);
#ifdef DEBUG
        Serial.println("Stopped charging");
#endif
    }
    */
    
    bool chargerPresent = digitalRead(BAT_CHG_PRESENT_PIN);
    bool charging = !digitalRead(BAT_CHARGING_PIN);
    
    Serial.print("Charger: ");
    Serial.println(chargerPresent);
    Serial.print("Charging: ");
    Serial.println(charging);
    
    if (level != batteryLevel) {
        batteryLevel = level;
        batteryStateChanged = true;
        batteryChar.setValue(batteryLevel);
#ifdef DEBUG
        Serial.print("Battery level: ");
        Serial.println(level);
#endif
    }
    /*
    if (batteryInterrupted) {
        batteryInterrupted = false;
        Serial.println("Battery interrupted!");
    }
    */
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
    if (batteryCharging) {
        digitalWrite(LED_PIN, LOW);
        if (batteryStateChanged) {
            batteryStateChanged = false;
            color_t colors[LEDS_NUMPIXELS];
            for (int i = 0; i < LEDS_NUMPIXELS; i++) {
                bool on = batteryLevel >= (((float)i * 100.0 / (float)LEDS_NUMPIXELS) + (50.0 / (float)LEDS_NUMPIXELS));
                colors[i].green = 0;
                colors[i].blue = 0;
                if (on)
                    colors[i].red = 255;
                else
                    colors[i].red = 0;
            }
            setLEDs(colors);
        }
        return;
    }
    
    if (batteryStateChanged) {
        batteryStateChanged = false;
        digitalWrite(LED_PIN, HIGH);
        if (batteryLevel < LEDS_LOW_BATTERY_LEVEL) {
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
    if (batteryCharging) {
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
    /*
    setLEDs(LEDS_OFF);
    nRF5x_lowPower.enableWakeupByInterrupt(ACC_INT1_PIN, RISING);
    nRF5x_lowPower.enableWakeupByInterrupt(BAT_STAT_PIN, FALLING);
    nRF5x_lowPower.powerMode(POWER_MODE_OFF);
    */
}

    
