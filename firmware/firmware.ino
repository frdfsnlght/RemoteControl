/*
    Firmware for Remote Control project using SparkFun nRF52832 Breakout
    https://www.sparkfun.com/products/13990
    
    Hardware:
    --------------
    SparkFun nRF52832 Breakout
    ADXL345 Digital Accelerometer (eBay generic)
    MCP738312 LiPo Charger (custom PCB)
    Neopixels
    
    Required libraries:
    -------------------
    Adafruit ADXL345 by Adafruit
    Adafruit Unified Sensor by Adafruit
    BLEPeripheral by Sandeep Mistry
    Keypad by Mark Stanley, Alexander Brevig
    Adafruit Neopixel by Adafruit (not included directly but needed by NeoPixel-Patterns
    
    Required libraries but must be manually installed from zip:
    ---------------------------------------------------------
    https://github.com/mristau/Arduino_nRF5x_lowPower
    https://github.com/frdfsnlght/NeoPixel-Patterns
    
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
#include <Keypad.h>                 // All the buttons!
#include <Arduino_nRF5x_lowPower.h> // Low power!

#include <NeoPixelController.h>     // LED patterns
#include <BlinkNeoPixelPattern.h>
#include <ScanNeoPixelPattern.h>
#include <Colors.h>

#define DEBUG

#ifdef DEBUG
#define debug(x) Serial.print(x)
#define debugln(x) Serial.println(x)
#define debugnum(x, y) Serial.print(x, y)
#define debugnumln(x, y) Serial.println(x, y)
#else
#define debug(x)
#define debugln(x)
#define debugnum(x, y)
#define debugnumln(x, y)
#endif

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
const int PS_CHARGING_PIN = 4;      // input, active low
const int PS_CHARGER_ENABLE_PIN = 12;  // output, active high to disable, input float to enable
const int PS_LED_ENABLE_PIN = 13;   // output, active high to enable

const int LEDS_PIN = 16;

uint8_t KEYPAD_ROW_PINS[] = {17, 18, 19, 20, 22, 23};
uint8_t KEYPAD_COL_PINS[] = {31, 29, 25, 30, 28, 24};

void(* reset) (void) = 0;


//=============================================================================
// Settings
//
typedef struct {
    float wakeupAcceleration;
    unsigned long sleepTime;
    unsigned long deepSleepTime;
    float ledBrightness;
} settings_t;
settings_t settings;
const float DEFAULT_WAKEUPACCELERATION = 1.5;            // g's
const unsigned long DEFAULT_SLEEPTIME = 10000;           // 10 seconds in milliseconds
const unsigned long DEFAULT_DEEPSLEEPTIME = 3600000;     // 1 hour in milliseconds
const float DEFAULT_LEDBRIGHTNESS = 0.5f;                // 50% brightness
uint32_t* settingsAddress;

#define FLASH_WAIT_READY { while (NRF_NVMC->READY == NVMC_READY_READY_Busy); }

//=============================================================================
// Power supply
//
bool psSetup = false;
const unsigned long PS_CHECK_INTERVAL = 1000;
unsigned long psLastCheck;
bool psOnCharger = false;
bool psCharging = false;
bool psChanged = false;

//=============================================================================
// Keypad
//
const uint8_t KEYPAD_ROWS = sizeof(KEYPAD_ROW_PINS);
const uint8_t KEYPAD_COLS = sizeof(KEYPAD_COL_PINS);
const unsigned int KEYPAD_DEBOUNCE_TIME = 100;
char KEYPAD_MAP[KEYPAD_ROWS][KEYPAD_COLS] = {
    {0x11, 0x12, 0x13, 0x14, 0x15, 0x16},
    {0x21, 0x22, 0x23, 0x24, 0x25, 0x26},
    {0x31, 0x32, 0x33, 0x34, 0x35, 0x36},
    {0x41, 0x42, 0x43, 0x44, 0x45, 0x46},
    {0x51, 0x52, 0x53, 0x54, 0x55, 0x56},
    {0x61, 0x62, 0x63, 0x64, 0x65, 0x66}
};
Keypad keypad = Keypad(makeKeymap(KEYPAD_MAP), KEYPAD_ROW_PINS, KEYPAD_COL_PINS, KEYPAD_ROWS, KEYPAD_COLS);
unsigned char keypadButton[2];
bool keypadIdle;

//=============================================================================
// LEDs
//
const int LEDS_NUMPIXELS = 5;
const int LEDS_NUMSEGMENTS = 1;
const int LEDS_DATA_LENGTH = LEDS_NUMPIXELS * 3;
const int LEDS_CHARGING_SCAN_INTERVAL = 0.2;
NeoPixelController leds = NeoPixelController(LEDS_NUMPIXELS, LEDS_NUMSEGMENTS, LEDS_PIN, NEO_GRB + NEO_KHZ800);
ScanNeoPixelPattern chargingPattern = ScanNeoPixelPattern();
uint8_t ledsValue[LEDS_DATA_LENGTH] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

//=============================================================================
// Bluetooth
//
const char* BLE_NAME = "BLERemote";
const unsigned short BLE_ADVERTISING_INTERVAL = 50;
BLEPeripheral blePeriph;
BLEService bleServ("1234");
BLEFixedLengthCharacteristic buttonChar("0001", BLENotify, (unsigned char)sizeof(keypadButton));
BLEFixedLengthCharacteristic ledsChar("0002", BLERead | BLEWrite, LEDS_DATA_LENGTH);
BLEUnsignedCharCharacteristic chargingChar("0003", BLERead | BLENotify);
BLEFloatCharacteristic wakeupAccelerationChar("0005", BLERead | BLEWrite);
BLEUnsignedLongCharacteristic sleepTimeChar("0007", BLERead | BLEWrite);
BLEUnsignedLongCharacteristic deepSleepTimeChar("0008", BLERead | BLEWrite);
BLEUnsignedLongCharacteristic ledBrightnessChar("0009", BLERead | BLEWrite);
BLEUnsignedCharCharacteristic saveSettingsChar("0090", BLEWrite);
BLEUnsignedCharCharacteristic resetChar("0099", BLEWrite);

//=============================================================================
// Accelerometer
//
bool accelSetup = false;
const uint8_t ACC_ADDRESS = 0x1d;
const range_t ACCEL_RANGE = ADXL345_RANGE_2_G;
const dataRate_t ACCEL_RATE = ADXL345_DATARATE_25_HZ;
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();
bool accelIdle;
volatile bool accelInterrupted = false;

bool isIdle = false;
unsigned long idleStart = 0;
bool isSleeping = false;

//=============================================================================
// Time
//
unsigned long lastMillis;
unsigned long realMillis;

//=============================================================================
// Stats
//
unsigned long bootTime;
unsigned long bluetoothConnectedTime;
unsigned long bluetoothConnections = 0;


void setup() {
    setupTime();
    
    bootTime = time();
    
    digitalWrite(LED_PIN, LOW); // turn on built-in LED
#ifdef DEBUG
    Serial.begin(115200);
#endif

    loadSettings();
    
    setupBluetooth();
    setupPowerSupply();
    setupLEDs();
    setupKeypad();
    setupAccelerometer();
    
    digitalWrite(LED_PIN, HIGH); // turn off built-in LED
    
    debugln("Ready");
}

void loop() {
    loopTime();
    loopBluetooth();
    loopPowerSupply();
    loopLEDs();
    loopKeypad();
    loopAccelerometer();
    checkIdle();
}


//=============================================================================
// Settings
//

// NVM manipulation inspired by https://github.com/arduino-org/arduino-core-nrf52/blob/master/libraries/BLE/BLEBondStore.cpp

void loadSettings() {
    debugln("Loading settings...");
    
    int offset = NRF_FICR->CODESIZE - (NRF_UICR->NRFFW[0] / NRF_FICR->CODEPAGESIZE);
    debug("offset="); debugnumln(offset, DEC);
	settingsAddress = (uint32_t *)(NRF_FICR->CODEPAGESIZE * (NRF_FICR->CODESIZE - 2 - (uint32_t)offset));
    debug("settingsAddress="); debugnumln((uint32_t)settingsAddress, HEX);
    debug("page="); debugnumln((uint32_t)settingsAddress / NRF_FICR->CODEPAGESIZE, HEX);
    
    if (*settingsAddress != 0xFFFFFFFF) {
        debug("*settingsAddress="); debugnumln(*settingsAddress, HEX);
        memcpy(&settings, settingsAddress, sizeof(settings_t));
        debugln("Loaded settings:");
    } else {
        debugln("No saved settings found, loading defaults:");
        settings.wakeupAcceleration = DEFAULT_WAKEUPACCELERATION;
        settings.sleepTime = DEFAULT_SLEEPTIME;
        settings.deepSleepTime = DEFAULT_DEEPSLEEPTIME;
        settings.ledBrightness = DEFAULT_LEDBRIGHTNESS;
    }
    debug("wakeupAcceleration: "); debugnumln(settings.wakeupAcceleration, DEC);
    debug("sleepTime: "); debugnumln(settings.sleepTime, DEC);
    debug("deepSleepTime: "); debugnumln(settings.deepSleepTime, DEC);
    debug("ledBrightness: "); debugnumln(settings.ledBrightness, DEC);
    debugln("Done loading settings");
}

void saveSettings() {
    debugln("Saving settings...");

    // Erase a page of flash...
    
    int32_t pageNo = (uint32_t)settingsAddress / NRF_FICR->CODEPAGESIZE;
    debug("Erasing page 0x"); debugnumln(pageNo, HEX);
    while(sd_flash_page_erase(pageNo) == NRF_ERROR_BUSY);
    FLASH_WAIT_READY

    // Write a page to flash...

    debugln("Writig flash...");
    while (sd_flash_write((uint32_t*)settingsAddress, (uint32_t*)&settings, (uint32_t)sizeof(settings_t)/4) == NRF_ERROR_BUSY);
    FLASH_WAIT_READY
  
    debugln("Done saving settings");
}

//=============================================================================
// Bluetooth
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
    blePeriph.addAttribute(buttonChar);
    blePeriph.addAttribute(ledsChar);
    blePeriph.addAttribute(chargingChar);
    blePeriph.addAttribute(wakeupAccelerationChar);
    blePeriph.addAttribute(sleepTimeChar);
    blePeriph.addAttribute(deepSleepTimeChar);
    blePeriph.addAttribute(ledBrightnessChar);
    blePeriph.addAttribute(saveSettingsChar);
    blePeriph.addAttribute(resetChar);
    
    // Initialize readable characteristic values
    ledsChar.setValue(ledsValue, LEDS_DATA_LENGTH);
    chargingChar.setValue(psCharging);
    wakeupAccelerationChar.setValue(settings.wakeupAcceleration);
    sleepTimeChar.setValue(settings.sleepTime);
    deepSleepTimeChar.setValue(settings.deepSleepTime);
    ledBrightnessChar.setValue(settings.ledBrightness);

    blePeriph.setEventHandler(BLEConnected, bluetoothConnected);
    
    // Initialize BLE:
    blePeriph.begin();

    debugln("BLE setup");
    
}

void bluetoothConnected(BLECentral& central) {
    bluetoothConnectedTime = time();
    bluetoothConnections++;
    if (bluetoothConnections == 1) {
        debug("Connected in ");
        debugln(bluetoothConnectedTime - bootTime);
    }
}

void loopBluetooth() {
    blePeriph.poll();

    
    if (ledsChar.written()) {
        const unsigned char* ledsState = ledsChar.value();
        memcpy(ledsValue, ledsState, LEDS_DATA_LENGTH);
        setLEDs();
        dumpLEDs(ledsValue);
    }
    if (wakeupAccelerationChar.written()) {
        settings.wakeupAcceleration = wakeupAccelerationChar.value();
        debug("Set wakeupAcceleration to ");
        debugln(settings.wakeupAcceleration);
        if (accelSetup)
            setAccelerationThreshold();
    }
    if (sleepTimeChar.written()) {
        settings.sleepTime = sleepTimeChar.value();
        debug("Set sleepTime to ");
        debugln(settings.sleepTime);
    }
    if (deepSleepTimeChar.written()) {
        settings.deepSleepTime = deepSleepTimeChar.value();
        debug("Set deepSleepTime to ");
        debugln(settings.deepSleepTime);
    }
    if (ledBrightnessChar.written()) {
        settings.ledBrightness = ledBrightnessChar.value();
        debug("Set ledBrightness to ");
        debugln(settings.ledBrightness);
    }
    
    if (saveSettingsChar.written()) {
        saveSettings();
    }
    if (resetChar.written()) {
        debugln("Resetting...");
        delay(1000);
        reset();
    }
}

//=============================================================================
// Power supply
//

void setupPowerSupply() {
    pinMode(PS_CHARGER_PIN, INPUT_PULLDOWN);    // pulldown isn't really needed
    //pinMode(PS_CHARGING_PIN, INPUT_PULLUP);
    pinMode(PS_CHARGING_PIN, INPUT);

    pinMode(PS_CHARGER_ENABLE_PIN, OUTPUT);     // enable charger managment
    digitalWrite(PS_CHARGER_ENABLE_PIN, HIGH);     // disable charger
    
    pinMode(PS_LED_ENABLE_PIN, OUTPUT);
    digitalWrite(PS_LED_ENABLE_PIN, HIGH);     // enable leds
    
    psLastCheck = time();
    psSetup = true;
    psChanged = true;
    debugln("Power supply setup");
}

void loopPowerSupply() {
    if ((time() - psLastCheck) < PS_CHECK_INTERVAL) return;
    psLastCheck = time();
    
    bool charger = digitalRead(PS_CHARGER_PIN);
    if (charger && !psOnCharger) {
        psChanged = true;
        psOnCharger = true;
        pinMode(PS_CHARGER_ENABLE_PIN, INPUT); // enable charger
        debugln("On charger");
    } else if (!charger && psOnCharger) {
        psChanged = true;
        psOnCharger = false;
        pinMode(PS_CHARGER_ENABLE_PIN, OUTPUT);     // enable charger managment
        digitalWrite(PS_CHARGER_ENABLE_PIN, HIGH);     // disable charger
        debugln("Off charger");
        if (psCharging) {
            psCharging = false;
            chargingChar.setValue(0);
            debugln("Stopped charging");
        }
    }

    if (psOnCharger) {
        bool charging = !digitalRead(PS_CHARGING_PIN);
        if (charging && !psCharging) {
            psChanged = true;
            psCharging = true;
            chargingChar.setValue(1);
            debugln("Started charging");
        } else if (!charging && psCharging) {
            psChanged = true;
            psCharging = false;
            chargingChar.setValue(0);
            debugln("Stopped charging");
        }
    }
    
}

//=============================================================================
// LEDs
//

void setupLEDs() {
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);
    leds.setupSegment(0, 0, LEDS_NUMPIXELS);
    leds.begin();
    leds.setSegmentColor(COLOR_OFF, 0);
    for (int i = 0; i < LEDS_DATA_LENGTH; i++)
        ledsValue[i] = 0;
    chargingPattern.setup(SCALECOLOR(COLOR_GREEN, settings.ledBrightness), LEDS_CHARGING_SCAN_INTERVAL);
    debugln("LEDs setup");
}

void loopLEDs() {
    leds.update();
    
    if (psChanged) {
        if (psOnCharger) {
            if (psCharging) {
                digitalWrite(LED_PIN, LOW);
                leds.play(chargingPattern, 0);
            } else {
                digitalWrite(LED_PIN, HIGH);
                leds.setSegmentColor(SCALECOLOR(COLOR_GREEN, settings.ledBrightness), 0);
            }
        } else {
            digitalWrite(LED_PIN, HIGH);
            if (leds.isSegmentActive(0))
                leds.stop(0);
            setLEDs(ledsValue);
        }
        psChanged = false;
    }
}


void setLEDs() {
    if (leds.isSegmentActive(0) || isSleeping) return;
    setLEDs(ledsValue);
}
    
void setLEDs(uint8_t values[]) {
    for(int i = 0; i < LEDS_NUMPIXELS; i++) {
        uint32_t color = COLOR(values[3 * i], values[3 * i + 1], values[3 * i + 2]);
        leds.setPixelColor(i, SCALECOLOR(color, settings.ledBrightness), 0);
        debug("pixel ");
        debugnum(i, DEC);
        debug(": ");
        debugnumln(color, HEX);
    }
    leds.show();
}

void dumpLEDs(uint8_t values[]) {
#ifdef DEBUG
    Serial.print("LEDs: ");
    for (int i = 0; i < LEDS_NUMPIXELS; i++) {
        if (i > 0)
            Serial.print(", ");
        Serial.print(values[3 * i]);
        Serial.print(':');
        Serial.print(values[3 * i + 1]);
        Serial.print(':');
        Serial.print(values[3 * i + 2]);
    }
    Serial.println();
#endif
}

//=============================================================================
// Keypad
//

void setupKeypad() {
    keypad.addEventListener(keypadEvent);
    keypad.setDebounceTime(KEYPAD_DEBOUNCE_TIME);
    debugln("Keypad setup");
}

void loopKeypad() {
    if (psOnCharger) return;
    
    keypadIdle = !keypad.getKeys(); // allows event handler to trigger for multiple keys
    //keypadIdle = !keypad.getKey();
    
    char buttonValue = digitalRead(BTN_PIN);
    static char lastButtonValue = HIGH;
    
    if (buttonValue != lastButtonValue) {
        lastButtonValue = buttonValue;
        keypadIdle = false;
        debug("Button: ");
        debugnumln(buttonValue, DEC);

        if (buttonValue == LOW) {
            keypadButton[0] = 0x01;
            keypadButton[1] = 0x99;
            buttonChar.setValue(keypadButton, sizeof(keypadButton));
        } else {
            keypadButton[0] = 0x00;
            keypadButton[1] = 0x99;
            buttonChar.setValue(keypadButton, sizeof(keypadButton));
        }
    }
    
}

void keypadEvent(KeypadEvent key) {
    switch (keypad.getState()) {
        case PRESSED:
            keypadButton[0] = 0x01;
            keypadButton[1] = key;
            buttonChar.setValue(keypadButton, sizeof(keypadButton));
            debug("Key down: ");
            debugnumln(key, HEX);
            break;
        case RELEASED:
            keypadButton[0] = 0x00;
            keypadButton[1] = key;
            buttonChar.setValue(keypadButton, sizeof(keypadButton));
            debug("Key up: ");
            debugnumln(key, HEX);
            break;
    }
}

//=============================================================================
// Accelerometer
//

void setupAccelerometer() {
    if (!accel.begin(ACC_ADDRESS)) {
        debugln("ADXL345 not detected!");
        return;
    }
    accel.setRange(ACCEL_RANGE);
    accel.setDataRate(ACCEL_RATE);
    
    pinMode(ACC_INT1_PIN, INPUT_PULLDOWN);
    pinMode(ACC_INT2_PIN, INPUT_PULLDOWN);  // not used
    
    setAccelerationThreshold();
    
    attachInterrupt(digitalPinToInterrupt(ACC_INT1_PIN), accelerometerInterrupt, RISING);
    accelSetup = true;
    debugln("Accelerometer setup");
}

void setAccelerationThreshold() {
    accel.writeRegister(ADXL345_REG_INT_ENABLE, 0);         // disable interrupts
    accel.writeRegister(ADXL345_REG_INT_MAP, 0);            // map all interrupts to INT1
    accel.writeRegister(ADXL345_REG_POWER_CTL, 0);          // turn off link and put in standby
    accel.writeRegister(ADXL345_REG_ACT_INACT_CTL, 0xf0);   // ac-coupled x, y, z activity
    accel.writeRegister(ADXL345_REG_THRESH_ACT, settings.wakeupAcceleration * 1000.0 / 62.5);
    accel.writeRegister(ADXL345_REG_INT_ENABLE, 0x10);      // enable activity interrupt
    accel.writeRegister(ADXL345_REG_POWER_CTL, 0x08);       // turn on measurement mode
    accel.readRegister(ADXL345_REG_INT_SOURCE);             // read to clear any interrupts
}

void accelerometerInterrupt() {
    accelInterrupted = true;
}

void loopAccelerometer() {
    if (! accelSetup) return;
    
    if (accelInterrupted) {
        accelInterrupted = false;
        accelIdle = false;
        accel.readRegister(ADXL345_REG_INT_SOURCE); // read to clear interrupts
    } else
        accelIdle = true;
}

//=============================================================================
// Idle
//
    
void checkIdle() {
    if (psOnCharger) {
        isIdle = false;
        if (isSleeping) {
            debugln("Waking up");
            isSleeping = false;
            exitSleep();
        }
        return;
    }
    
    unsigned long now = time();
    
    if (keypadIdle && accelIdle) {
        if (!isIdle) {
            isIdle = true;
            isSleeping = false;
            idleStart = now;
        } else if ((!isSleeping) && (settings.sleepTime > 0) && ((now - idleStart) > settings.sleepTime)) {
            debugln("Going to sleep");
            isSleeping = true;
            enterSleep();
            
        } else if ((now - idleStart) > settings.deepSleepTime) {
            debugln("Going to deep sleep");
            debug("Then: ");
            debugnumln(idleStart, DEC);
            debug("Now: ");
            debugnumln(now, DEC);
            debug("Elapsed: ");
            debugnumln(now - idleStart, DEC);
            enterDeepSleep();
        }
    } else {
        if (isIdle) {
            isIdle = false;
            if (isSleeping) {
                debugln("Waking up");
                isSleeping = false;
                exitSleep();
            }
        }
    }
}

void enterSleep() {
    if (leds.isSegmentActive(0))
        leds.stop(0);
    leds.setSegmentColor(COLOR_OFF, 0);
    digitalWrite(PS_LED_ENABLE_PIN, LOW);  // disable leds
}

void exitSleep() {
    digitalWrite(PS_LED_ENABLE_PIN, HIGH);  // enable leds
    delay(100);
    setLEDs();
}

void enterDeepSleep() {
    if (leds.isSegmentActive(0))
        leds.stop(0);
    leds.setSegmentColor(COLOR_OFF, 0);
    digitalWrite(PS_LED_ENABLE_PIN, LOW);  // disble leds
    delay(1000);
    nRF5x_lowPower.enableWakeupByInterrupt(ACC_INT1_PIN, RISING);
    nRF5x_lowPower.enableWakeupByInterrupt(PS_CHARGER_PIN, RISING);
    nRF5x_lowPower.powerMode(POWER_MODE_OFF);
}

//=============================================================================
// Time
// It appears that the millis() function rolls over at 512000 for some stupid reason.
// So, I've implemented my own version.
//

void setupTime() {
    lastMillis = millis();
    realMillis = lastMillis;
}

void loopTime() {
    unsigned long now = millis();
    if (now < lastMillis) {
        // we've rolled over
        realMillis += (512000 - lastMillis) + now;
    } else {
        realMillis += now - lastMillis;
    }
    lastMillis = now;
}

unsigned long time() {
    return realMillis;
}


