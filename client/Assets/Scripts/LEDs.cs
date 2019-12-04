using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class LEDs : MonoBehaviour {

    private Image[] leds;

    // Start is called before the first frame update
    void Start() {
        leds = GetComponentsInChildren<Image>();
    }

    public void SetColors(byte[] colors) {
        for (int i = 0; i < leds.Length; i++) {
            leds[i].color = new Color(
                (float)colors[i * 3] / 255f,
                (float)colors[i * 3 + 1] / 255f,
                (float)colors[i * 3 + 2] / 255f
            );
        }
    }

}
