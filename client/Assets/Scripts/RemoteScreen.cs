using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RemoteScreen : MonoBehaviour {

    public SettingsScreen settingsScreen;
    public NotConnectedOverlay notConnectedOverlay;

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
