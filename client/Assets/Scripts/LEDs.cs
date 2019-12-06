using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class LEDs : MonoBehaviour {

    public Color offColor;

    private Image[] leds;

    void Start() {
        leds = GetComponentsInChildren<Image>();
        foreach (Image led in leds)
            led.color = offColor;
    }

    public void SetColors(byte[] colors) {
        for (int i = 0; i < leds.Length; i++) {
            if ((colors[i * 3] == 0) && (colors[i * 3 + 1] == 0) && (colors[i * 3 + 2] == 0))
                leds[i].color = offColor;
            else
                leds[i].color = new Color(
                    (float)colors[i * 3] / 255f,
                    (float)colors[i * 3 + 1] / 255f,
                    (float)colors[i * 3 + 2] / 255f
                );
        }
    }

}
