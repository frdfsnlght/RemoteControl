﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class RemoteScreen : MonoBehaviour {

    public SettingsScreen settingsScreen;
    public NotConnectedOverlay notConnectedOverlay;
    public TMP_Text versionField;

    private void Start() {
        if (settingsScreen.IsVisible())
            settingsScreen.Hide();
        if (notConnectedOverlay.IsVisible())
            notConnectedOverlay.Hide();
        versionField.text = "v" + Application.version;
    }

    public void OnSettings() {
        settingsScreen.Show();
    }

    private void Update() {
        if (TCPRemoteClient.client.connected && notConnectedOverlay.IsVisible())
            notConnectedOverlay.Hide();
        else if (!TCPRemoteClient.client.connected && !notConnectedOverlay.IsVisible())
            notConnectedOverlay.Show();
    }

}
