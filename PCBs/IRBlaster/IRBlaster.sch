EESchema Schematic File Version 4
LIBS:power
LIBS:device
LIBS:74xx
LIBS:audio
LIBS:interface
LIBS:IRBlaster-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "IRBlaster v1"
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_01x04 J3
U 1 1 5DBC6553
P 7400 1700
F 0 "J3" H 7479 1692 50  0000 L CNN
F 1 "Regulator" H 7479 1601 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x04_Pitch2.54mm" H 7400 1700 50  0001 C CNN
F 3 "~" H 7400 1700 50  0001 C CNN
	1    7400 1700
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x05 J4
U 1 1 5DBC660A
P 2200 4100
F 0 "J4" H 2120 4517 50  0000 C CNN
F 1 "Front Panel 1" H 2120 4426 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x05_Pitch2.54mm" H 2200 4100 50  0001 C CNN
F 3 "~" H 2200 4100 50  0001 C CNN
	1    2200 4100
	-1   0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J2
U 1 1 5DBC66E4
P 2200 1800
F 0 "J2" H 2120 2017 50  0000 C CNN
F 1 "Power" H 2120 1926 50  0000 C CNN
F 2 "terminals:Terminal_5mm_2pos" H 2200 1800 50  0001 C CNN
F 3 "~" H 2200 1800 50  0001 C CNN
	1    2200 1800
	-1   0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J5
U 1 1 5DBC672C
P 6100 2300
F 0 "J5" H 6179 2292 50  0000 L CNN
F 1 "Blaster 1" H 6179 2201 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 6100 2300 50  0001 C CNN
F 3 "~" H 6100 2300 50  0001 C CNN
	1    6100 2300
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J6
U 1 1 5DBC676C
P 6100 3500
F 0 "J6" H 6179 3492 50  0000 L CNN
F 1 "Blaster 2" H 6179 3401 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 6100 3500 50  0001 C CNN
F 3 "~" H 6100 3500 50  0001 C CNN
	1    6100 3500
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J7
U 1 1 5DBC67C5
P 6100 4700
F 0 "J7" H 6179 4692 50  0000 L CNN
F 1 "Blaster 3" H 6179 4601 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 6100 4700 50  0001 C CNN
F 3 "~" H 6100 4700 50  0001 C CNN
	1    6100 4700
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J8
U 1 1 5DBC67EF
P 6100 5900
F 0 "J8" H 6179 5892 50  0000 L CNN
F 1 "Blaster 4" H 6179 5801 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 6100 5900 50  0001 C CNN
F 3 "~" H 6100 5900 50  0001 C CNN
	1    6100 5900
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R2
U 1 1 5DBC6D56
P 3200 3450
F 0 "R2" H 3268 3496 50  0000 L CNN
F 1 "10K" H 3268 3405 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 3240 3440 50  0001 C CNN
F 3 "~" H 3200 3450 50  0001 C CNN
	1    3200 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:CP1 C1
U 1 1 5DBC6DC4
P 5650 1350
F 0 "C1" H 5765 1396 50  0000 L CNN
F 1 "10uF" H 5765 1305 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D5.0mm_P2.50mm" H 5650 1350 50  0001 C CNN
F 3 "~" H 5650 1350 50  0001 C CNN
	1    5650 1350
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_02x04_Top_Bottom J1
U 1 1 5DBC738C
P 4900 1100
F 0 "J1" H 4950 1417 50  0000 C CNN
F 1 "Raspberry Pi" H 4950 1326 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x04_Pitch2.54mm" H 4900 1100 50  0001 C CNN
F 3 "~" H 4900 1100 50  0001 C CNN
	1    4900 1100
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R1
U 1 1 5DBC75E9
P 2800 3450
F 0 "R1" H 2868 3496 50  0000 L CNN
F 1 "750" H 2868 3405 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 2840 3440 50  0001 C CNN
F 3 "~" H 2800 3450 50  0001 C CNN
	1    2800 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R3
U 1 1 5DBC7689
P 3600 3450
F 0 "R3" H 3668 3496 50  0000 L CNN
F 1 "750" H 3668 3405 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 3640 3440 50  0001 C CNN
F 3 "~" H 3600 3450 50  0001 C CNN
	1    3600 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R5
U 1 1 5DBC78D7
P 4700 2650
F 0 "R5" H 4768 2696 50  0000 L CNN
F 1 "0" H 4768 2605 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 4740 2640 50  0001 C CNN
F 3 "~" H 4700 2650 50  0001 C CNN
	1    4700 2650
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R4
U 1 1 5DBC793D
P 3950 3100
F 0 "R4" V 3745 3100 50  0000 C CNN
F 1 "4K" V 3836 3100 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 3990 3090 50  0001 C CNN
F 3 "~" H 3950 3100 50  0001 C CNN
	1    3950 3100
	0    1    1    0   
$EndComp
$Comp
L Device:Q_NPN_Darlington_CBE Q1
U 1 1 5DBC7A61
P 4600 3100
F 0 "Q1" H 4791 3146 50  0000 L CNN
F 1 "ZTX602/3" H 4791 3055 50  0000 L CNN
F 2 "my-transistors:TO-92_Inline_Wide_Reverse" H 4800 3200 50  0001 C CNN
F 3 "https://www.diodes.com/assets/Datasheets/ZTX602.pdf" H 4600 3100 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/diodes-incorporated/ZTX603/ZTX603-ND/92547" H 4600 3100 50  0001 C CNN "DigiKey"
	1    4600 3100
	1    0    0    -1  
$EndComp
$Comp
L Device:Q_NPN_Darlington_CBE Q2
U 1 1 5DBC89C2
P 4600 4300
F 0 "Q2" H 4791 4346 50  0000 L CNN
F 1 "ZTX602/3" H 4791 4255 50  0000 L CNN
F 2 "my-transistors:TO-92_Inline_Wide_Reverse" H 4800 4400 50  0001 C CNN
F 3 "https://www.diodes.com/assets/Datasheets/ZTX602.pdf" H 4600 4300 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/diodes-incorporated/ZTX603/ZTX603-ND/92547" H 4600 4300 50  0001 C CNN "DigiKey"
	1    4600 4300
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R6
U 1 1 5DBC8AAB
P 4700 3850
F 0 "R6" H 4768 3896 50  0000 L CNN
F 1 "0" H 4768 3805 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 4740 3840 50  0001 C CNN
F 3 "~" H 4700 3850 50  0001 C CNN
	1    4700 3850
	1    0    0    -1  
$EndComp
$Comp
L Device:Q_NPN_Darlington_CBE Q3
U 1 1 5DBC9714
P 4600 5500
F 0 "Q3" H 4791 5546 50  0000 L CNN
F 1 "ZTX602/3" H 4791 5455 50  0000 L CNN
F 2 "my-transistors:TO-92_Inline_Wide_Reverse" H 4800 5600 50  0001 C CNN
F 3 "https://www.diodes.com/assets/Datasheets/ZTX602.pdf" H 4600 5500 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/diodes-incorporated/ZTX603/ZTX603-ND/92547" H 4600 5500 50  0001 C CNN "DigiKey"
	1    4600 5500
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R7
U 1 1 5DBC9773
P 4700 5050
F 0 "R7" H 4768 5096 50  0000 L CNN
F 1 "0" H 4768 5005 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 4740 5040 50  0001 C CNN
F 3 "~" H 4700 5050 50  0001 C CNN
	1    4700 5050
	1    0    0    -1  
$EndComp
$Comp
L Device:Q_NPN_Darlington_CBE Q4
U 1 1 5DBC9984
P 4600 6700
F 0 "Q4" H 4791 6746 50  0000 L CNN
F 1 "ZTX602/3" H 4791 6655 50  0000 L CNN
F 2 "my-transistors:TO-92_Inline_Wide_Reverse" H 4800 6800 50  0001 C CNN
F 3 "https://www.diodes.com/assets/Datasheets/ZTX602.pdf" H 4600 6700 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/diodes-incorporated/ZTX603/ZTX603-ND/92547" H 4600 6700 50  0001 C CNN "DigiKey"
	1    4600 6700
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R8
U 1 1 5DBC9A2A
P 4700 6250
F 0 "R8" H 4768 6296 50  0000 L CNN
F 1 "0" H 4768 6205 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical" V 4740 6240 50  0001 C CNN
F 3 "~" H 4700 6250 50  0001 C CNN
	1    4700 6250
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 3100 4200 3100
Wire Wire Line
	4200 3100 4200 4300
Wire Wire Line
	4200 4300 4400 4300
Connection ~ 4200 3100
Wire Wire Line
	4200 3100 4400 3100
Wire Wire Line
	4200 4300 4200 5500
Wire Wire Line
	4200 5500 4400 5500
Connection ~ 4200 4300
Wire Wire Line
	4200 5500 4200 6700
Wire Wire Line
	4200 6700 4400 6700
Connection ~ 4200 5500
Wire Wire Line
	4700 2800 4700 2900
Wire Wire Line
	4700 4000 4700 4100
Wire Wire Line
	4700 5200 4700 5300
Wire Wire Line
	4700 6400 4700 6500
Wire Wire Line
	4700 3300 4700 3400
Wire Wire Line
	4700 3400 5250 3400
Wire Wire Line
	5250 3400 5250 4600
Wire Wire Line
	5250 4600 4700 4600
Wire Wire Line
	4700 4600 4700 4500
Wire Wire Line
	5250 4600 5250 5800
Wire Wire Line
	5250 5800 4700 5800
Wire Wire Line
	4700 5800 4700 5700
Connection ~ 5250 4600
Wire Wire Line
	5250 5800 5250 7000
Wire Wire Line
	5250 7000 4700 7000
Wire Wire Line
	4700 7000 4700 6900
Connection ~ 5250 5800
Wire Wire Line
	4700 2500 4700 2400
Wire Wire Line
	4700 2400 5900 2400
Wire Wire Line
	4700 3700 4700 3600
Wire Wire Line
	4700 3600 5900 3600
Wire Wire Line
	4700 4900 4700 4800
Wire Wire Line
	4700 4800 5900 4800
Wire Wire Line
	4700 6100 4700 6000
Wire Wire Line
	4700 6000 5900 6000
Wire Wire Line
	5900 2300 5800 2300
Wire Wire Line
	5800 2300 5800 3500
Wire Wire Line
	5800 3500 5900 3500
Wire Wire Line
	5800 3500 5800 4700
Wire Wire Line
	5800 4700 5900 4700
Connection ~ 5800 3500
Wire Wire Line
	5800 4700 5800 5900
Wire Wire Line
	5800 5900 5900 5900
Connection ~ 5800 4700
Wire Wire Line
	5200 1000 5400 1000
Wire Wire Line
	6000 1000 6000 1600
Wire Wire Line
	6000 1600 7200 1600
Wire Wire Line
	5200 1100 5400 1100
Wire Wire Line
	5400 1100 5400 1000
Connection ~ 5400 1000
Wire Wire Line
	5400 1000 5650 1000
Wire Wire Line
	5900 1700 7200 1700
Wire Wire Line
	2400 1800 5800 1800
Text Label 4000 1800 0    50   ~ 0
12V
Text Label 6600 1600 0    50   ~ 0
5V
Text Label 4050 1000 0    50   ~ 0
3.3V
Text Label 6600 1700 0    50   ~ 0
GND
Wire Wire Line
	2400 1900 5900 1900
Wire Wire Line
	5900 1900 5900 1700
Wire Wire Line
	5200 1200 5400 1200
Wire Wire Line
	5400 1200 5400 1700
Wire Wire Line
	5400 1700 5650 1700
Connection ~ 5900 1700
Wire Wire Line
	5650 1200 5650 1000
Connection ~ 5650 1000
Wire Wire Line
	5650 1000 6000 1000
Wire Wire Line
	5650 1500 5650 1700
Connection ~ 5650 1700
Wire Wire Line
	5650 1700 5900 1700
Wire Wire Line
	5800 1800 5800 2300
Connection ~ 5800 1800
Wire Wire Line
	5800 1800 7200 1800
Connection ~ 5800 2300
NoConn ~ 7200 1900
NoConn ~ 5200 1300
Wire Wire Line
	4700 1100 3200 1100
Wire Wire Line
	3200 1100 3200 3100
Wire Wire Line
	3200 3100 3600 3100
Wire Wire Line
	3200 3100 3200 3300
Connection ~ 3200 3100
Wire Wire Line
	3600 3300 3600 3100
Connection ~ 3600 3100
Wire Wire Line
	3600 3100 3800 3100
Wire Wire Line
	4700 1000 2700 1000
Wire Wire Line
	2700 1000 2700 3900
Wire Wire Line
	2700 3900 2400 3900
Wire Wire Line
	3200 3600 3200 4000
Wire Wire Line
	3200 4600 4700 4600
Connection ~ 4700 4600
Wire Wire Line
	2400 4000 3200 4000
Connection ~ 3200 4000
Wire Wire Line
	3200 4000 3200 4600
Wire Wire Line
	5400 1700 5400 3400
Wire Wire Line
	5400 3400 5250 3400
Connection ~ 5400 1700
Connection ~ 5250 3400
Wire Wire Line
	3600 3600 3600 4100
Wire Wire Line
	3600 4100 2400 4100
Text Label 4050 1100 0    50   ~ 0
IR_OUT
Wire Wire Line
	4700 1200 2800 1200
Wire Wire Line
	2800 4200 2400 4200
Wire Wire Line
	4700 1300 3050 1300
Wire Wire Line
	3050 1300 3050 4300
Wire Wire Line
	3050 4300 2400 4300
Text Label 4050 1200 0    50   ~ 0
STATUS
Text Label 4050 1300 0    50   ~ 0
IR_IN
Wire Wire Line
	2800 4200 2800 3600
Wire Wire Line
	2800 3300 2800 1200
$EndSCHEMATC
