using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class SettingsScreen : MonoBehaviour {

    public TMP_InputField addressField;
    public TMP_InputField portField;

    private void Awake() {
        gameObject.SetActive(false);
    }

    private void OnEnable() {
        Debug.Log("opened settings");
        addressField.text = TCPRemoteClient.client.address;
        portField.text = TCPRemoteClient.client.port.ToString();
    }

    public void OnCancel() {
        gameObject.SetActive(false);
    }

    public void OnOK() {
        TCPRemoteClient.client.address = addressField.text;
        TCPRemoteClient.client.port = int.Parse(portField.text);
        TCPRemoteClient.client.Reconnect();
        gameObject.SetActive(false);
    }

}
