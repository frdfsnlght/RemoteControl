EESchema Schematic File Version 4
LIBS:power
LIBS:device
LIBS:74xx
LIBS:audio
LIBS:interface
LIBS:Connector-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Remote Control Connector"
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_01x08 J2
U 1 1 5DBA2725
P 5400 4400
F 0 "J2" H 5479 4392 50  0000 L CNN
F 1 "Accel" H 5479 4301 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x08_Pitch2.54mm" H 5400 4400 50  0001 C CNN
F 3 "~" H 5400 4400 50  0001 C CNN
	1    5400 4400
	1    0    0    -1  
$EndComp
Wire Wire Line
	5200 5300 5100 5300
Wire Wire Line
	5100 5300 5100 4800
Wire Wire Line
	5100 4800 5200 4800
Wire Wire Line
	5100 3600 5200 3600
Connection ~ 5100 4800
Text Label 5100 3800 0    50   ~ 0
GND
Text Label 4700 3400 0    50   ~ 0
3.3V
Text Label 4900 3500 0    50   ~ 0
VBAT
Wire Wire Line
	5200 5400 4900 5400
Wire Wire Line
	4900 5400 4900 3500
Wire Wire Line
	4900 3500 5200 3500
Wire Wire Line
	4700 3400 5200 3400
Wire Wire Line
	5200 4700 4700 4700
NoConn ~ 5200 3200
NoConn ~ 5200 3300
Wire Wire Line
	5200 4200 4300 4200
Wire Wire Line
	5200 4300 4700 4300
Connection ~ 4700 4300
Wire Wire Line
	4700 4300 4700 3400
Text Label 4700 3000 0    50   ~ 0
AC_INT1
Text Label 4700 3100 0    50   ~ 0
AC_INT2
Text Label 4700 2800 0    50   ~ 0
CHG_PRESENT
Text Label 4700 2300 0    50   ~ 0
~CHG_EN
Text Label 4700 2900 0    50   ~ 0
~CHARGING
Text Label 4700 2700 0    50   ~ 0
SCL
Text Label 4700 2400 0    50   ~ 0
SDA
Wire Wire Line
	4700 4300 4700 4600
Wire Wire Line
	5100 3600 5100 4800
Wire Wire Line
	5200 4600 4700 4600
Connection ~ 4700 4600
Wire Wire Line
	4700 4600 4700 4700
Wire Wire Line
	5200 4100 4500 4100
Wire Wire Line
	4500 4100 4500 2700
Wire Wire Line
	4500 2700 5200 2700
Wire Wire Line
	3700 2900 5200 2900
Wire Wire Line
	4300 4200 4300 2400
Wire Wire Line
	4300 2400 5200 2400
Wire Wire Line
	5200 4400 4100 4400
Wire Wire Line
	4100 4400 4100 3100
Wire Wire Line
	4100 3100 5200 3100
Wire Wire Line
	5200 4500 3900 4500
Wire Wire Line
	3900 4500 3900 3000
Wire Wire Line
	3900 3000 5200 3000
Text Label 4700 2200 0    50   ~ 0
LED_EN
Wire Wire Line
	3500 2800 3500 5600
Wire Wire Line
	3500 2800 5200 2800
Wire Wire Line
	4500 4100 4500 5700
Connection ~ 4500 4100
Wire Wire Line
	4300 4200 4300 5800
Connection ~ 4300 4200
$Comp
L Connector_Generic:Conn_01x15 J1
U 1 1 5DC13B06
P 5400 2900
F 0 "J1" H 5479 2942 50  0000 L CNN
F 1 "MCU" H 5479 2851 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x15_Pitch2.54mm" H 5400 2900 50  0001 C CNN
F 3 "~" H 5400 2900 50  0001 C CNN
	1    5400 2900
	1    0    0    -1  
$EndComp
Wire Wire Line
	3100 2200 5200 2200
Wire Wire Line
	3300 2300 5200 2300
Wire Wire Line
	3300 2300 3300 5900
Wire Wire Line
	3100 2200 3100 6000
NoConn ~ 5200 2500
NoConn ~ 5200 2600
$Comp
L Connector_Generic:Conn_01x08 J3
U 1 1 5DC1B29E
P 5400 5600
F 0 "J3" H 5479 5592 50  0000 L CNN
F 1 "Power Supply" H 5479 5501 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x08_Pitch2.54mm" H 5400 5600 50  0001 C CNN
F 3 "~" H 5400 5600 50  0001 C CNN
	1    5400 5600
	1    0    0    -1  
$EndComp
Wire Wire Line
	5200 5500 3700 5500
Wire Wire Line
	3700 5500 3700 2900
Wire Wire Line
	5200 5600 3500 5600
Wire Wire Line
	5200 5700 4500 5700
Wire Wire Line
	5200 5800 4300 5800
Wire Wire Line
	5200 5900 3300 5900
Wire Wire Line
	5200 6000 3100 6000
$EndSCHEMATC
