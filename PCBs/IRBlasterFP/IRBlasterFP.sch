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
P 5100 4550
F 0 "D1" V 5138 4432 50  0000 R CNN
F 1 "IR_OUT" V 5047 4432 50  0000 R CNN
F 2 "LEDs:LED_D3.0mm" H 5100 4550 50  0001 C CNN
F 3 "~" H 5100 4550 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/broadcom-limited/HLMP-1700-B0002/516-1791-1-ND/1966497" H 5100 4550 50  0001 C CNN "DigiKey"
	1    5100 4550
	0    -1   -1   0   
$EndComp
$Comp
L Device:LED D2
U 1 1 5DBC71CC
P 5700 4550
F 0 "D2" V 5738 4432 50  0000 R CNN
F 1 "STATUS" V 5647 4432 50  0000 R CNN
F 2 "LEDs:LED_D3.0mm" H 5700 4550 50  0001 C CNN
F 3 "~" H 5700 4550 50  0001 C CNN
F 4 "https://www.digikey.com/product-detail/en/broadcom-limited/HLMP-1700-B0002/516-1791-1-ND/1966497" H 5700 4550 50  0001 C CNN "DigiKey"
	1    5700 4550
	0    -1   -1   0   
$EndComp
$Comp
L Connector_Generic:Conn_01x05 J1
U 1 1 5DBC76CB
P 4500 4000
F 0 "J1" H 4420 4417 50  0000 C CNN
F 1 "Front Panel 2" H 4420 4326 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x05_Pitch2.54mm" H 4500 4000 50  0001 C CNN
F 3 "~" H 4500 4000 50  0001 C CNN
	1    4500 4000
	-1   0    0    -1  
$EndComp
$Comp
L Device:CP1 C1
U 1 1 5DBC7797
P 6400 4650
F 0 "C1" H 6515 4696 50  0000 L CNN
F 1 "1uF" H 6515 4605 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D5.0mm_P2.50mm" H 6400 4650 50  0001 C CNN
F 3 "~" H 6400 4650 50  0001 C CNN
	1    6400 4650
	1    0    0    -1  
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
	4700 3900 4800 3900
Wire Wire Line
	5600 3900 5600 3500
Wire Wire Line
	4700 4100 5700 4100
Wire Wire Line
	5700 4100 5700 4400
Wire Wire Line
	5100 4700 5100 4900
Wire Wire Line
	5100 4900 5500 4900
Wire Wire Line
	5700 4900 5700 4700
Wire Wire Line
	5700 4900 6400 4900
Wire Wire Line
	6400 4900 6400 4800
Connection ~ 5700 4900
Wire Wire Line
	6400 4500 6400 3800
Wire Wire Line
	4800 3900 4800 4900
Wire Wire Line
	4800 4900 5100 4900
Connection ~ 4800 3900
Wire Wire Line
	4800 3900 5600 3900
Connection ~ 5100 4900
Connection ~ 6400 3800
Wire Wire Line
	6000 3500 6000 3800
Wire Wire Line
	4700 3800 6000 3800
Connection ~ 6000 3800
Wire Wire Line
	6000 3800 6400 3800
Wire Wire Line
	5800 3500 5800 4000
$Comp
L power:PWR_FLAG #FLG0102
U 1 1 5DC1E0EE
P 5500 4900
F 0 "#FLG0102" H 5500 4975 50  0001 C CNN
F 1 "PWR_FLAG" H 5500 5074 50  0000 C CNN
F 2 "" H 5500 4900 50  0001 C CNN
F 3 "~" H 5500 4900 50  0001 C CNN
	1    5500 4900
	1    0    0    -1  
$EndComp
Connection ~ 5500 4900
Wire Wire Line
	5500 4900 5700 4900
Wire Wire Line
	4700 4200 5100 4200
Wire Wire Line
	5100 4200 5100 4400
Wire Wire Line
	4700 4000 5800 4000
$EndSCHEMATC
