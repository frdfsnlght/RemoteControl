using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RemoteScreen : MonoBehaviour {

    public SettingsScreen settingsScreen;

    public void OnSettings() {
        settingsScreen.gameObject.SetActive(true);
    }


}
