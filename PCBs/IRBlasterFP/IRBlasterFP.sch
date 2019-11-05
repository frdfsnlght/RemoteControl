EESchema Schematic File Version 4
LIBS:power
LIBS:device
LIBS:74xx
LIBS:audio
LIBS:interface
LIBS:IRBlasterFP-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "IRBlasterFP v1"
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Interface_Optical:TSOP382xx U1
U 1 1 5DBC6E83
P 5800 3100
F 0 "U1" V 5741 3388 50  0000 L CNN
F 1 "TSOP38238" V 5832 3388 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 5750 2725 50  0001 C CNN
F 3 "http://www.vishay.com/docs/82491/tsop382.pdf" H 6450 3400 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/vishay-semiconductor-opto-division/TSOP38238/751-1227-ND/1681362" H 5800 3100 50  0001 C CNN "DigiKey"
	1    5800 3100
	0    1    1    0   
$EndComp
$Comp
L Device:LED D1
U 1 1 5DBC6F3B
P 5100 5100
F 0 "D1" V 5138 4982 50  0000 R CNN
F 1 "IR_OUT" V 5047 4982 50  0000 R CNN
F 2 "LEDs:LED_D3.0mm" H 5100 5100 50  0001 C CNN
F 3 "~" H 5100 5100 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/broadcom-limited/HLMP-1700-B0002/516-1791-1-ND/1966497" H 5100 5100 50  0001 C CNN "DigiKey"
	1    5100 5100
	0    -1   -1   0   
$EndComp
$Comp
L Device:LED D2
U 1 1 5DBC71CC
P 5700 5100
F 0 "D2" V 5738 4982 50  0000 R CNN
F 1 "STATUS" V 5647 4982 50  0000 R CNN
F 2 "LEDs:LED_D3.0mm" H 5700 5100 50  0001 C CNN
F 3 "~" H 5700 5100 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/broadcom-limited/HLMP-1700-B0002/516-1791-1-ND/1966497" H 5700 5100 50  0001 C CNN "DigiKey"
	1    5700 5100
	0    -1   -1   0   
$EndComp
$Comp
L Connector_Generic:Conn_01x05 J1
U 1 1 5DBC76CB
P 4500 4000
F 0 "J1" H 4420 4417 50  0000 C CNN
F 1 "Front Panel" H 4420 4326 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x05_Pitch2.54mm" H 4500 4000 50  0001 C CNN
F 3 "~" H 4500 4000 50  0001 C CNN
	1    4500 4000
	-1   0    0    -1  
$EndComp
$Comp
L power:PWR_FLAG #FLG0101
U 1 1 5DBF5299
P 6400 3800
F 0 "#FLG0101" H 6400 3875 50  0001 C CNN
F 1 "PWR_FLAG" H 6400 3974 50  0000 C CNN
F 2 "" H 6400 3800 50  0001 C CNN
F 3 "~" H 6400 3800 50  0001 C CNN
	1    6400 3800
	1    0    0    -1  
$EndComp
Wire Wire Line
	5600 3900 5600 3500
Wire Wire Line
	4700 4100 5700 4100
Wire Wire Line
	5100 5250 5100 5600
Wire Wire Line
	5700 5600 5700 5250
Wire Wire Line
	5700 5600 6400 5600
Wire Wire Line
	6400 5600 6400 5250
Connection ~ 5700 5600
Wire Wire Line
	4800 5600 5100 5600
Connection ~ 5100 5600
Wire Wire Line
	6000 3500 6000 3800
Wire Wire Line
	4700 3800 6000 3800
Connection ~ 6000 3800
Wire Wire Line
	6000 3800 6400 3800
Wire Wire Line
	5800 3500 5800 4000
Wire Wire Line
	4700 4200 5100 4200
Wire Wire Line
	4700 4000 5800 4000
Text Label 5250 3800 0    50   ~ 0
3.3V
Text Label 5250 3900 0    50   ~ 0
GND
Text Label 5250 4000 0    50   ~ 0
IR_IN
Text Label 5250 4100 0    50   ~ 0
STATUS
Text Label 4850 4200 0    50   ~ 0
IR_OUT
$Comp
L Device:CP1 C1
U 1 1 5DC1CE96
P 6400 5100
F 0 "C1" H 6515 5146 50  0000 L CNN
F 1 "1uF" H 6515 5055 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D5.0mm_P2.50mm" H 6400 5100 50  0001 C CNN
F 3 "~" H 6400 5100 50  0001 C CNN
	1    6400 5100
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R1
U 1 1 5DC1D2DC
P 5100 4600
F 0 "R1" H 5168 4646 50  0000 L CNN
F 1 "750" H 5168 4555 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P1.90mm_Vertical" V 5140 4590 50  0001 C CNN
F 3 "~" H 5100 4600 50  0001 C CNN
	1    5100 4600
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R2
U 1 1 5DC1D326
P 5700 4600
F 0 "R2" H 5768 4646 50  0000 L CNN
F 1 "750" H 5768 4555 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P1.90mm_Vertical" V 5740 4590 50  0001 C CNN
F 3 "~" H 5700 4600 50  0001 C CNN
	1    5700 4600
	1    0    0    -1  
$EndComp
Wire Wire Line
	4700 3900 4800 3900
Wire Wire Line
	4800 3900 4800 5600
Connection ~ 4800 3900
Wire Wire Line
	4800 3900 5600 3900
Wire Wire Line
	6400 3800 6400 4950
Connection ~ 6400 3800
Wire Wire Line
	5100 5600 5700 5600
Wire Wire Line
	6400 5750 6400 5600
Connection ~ 6400 5600
Wire Wire Line
	5100 4450 5100 4200
Wire Wire Line
	5700 4100 5700 4450
Wire Wire Line
	5700 4750 5700 4950
Wire Wire Line
	5100 4750 5100 4950
$Comp
L power:PWR_FLAG #FLG0102
U 1 1 5DC1EE70
P 6400 5750
F 0 "#FLG0102" H 6400 5825 50  0001 C CNN
F 1 "PWR_FLAG" H 6400 5924 50  0000 C CNN
F 2 "" H 6400 5750 50  0001 C CNN
F 3 "~" H 6400 5750 50  0001 C CNN
	1    6400 5750
	-1   0    0    1   
$EndComp
$EndSCHEMATC
