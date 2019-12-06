using UnityEngine;
using UnityEngine.EventSystems;
using TMPro;

public class SettingsScreen : MonoBehaviour, IPointerDownHandler {

    public TMP_InputField addressField;
    public TMP_InputField portField;
    public TMP_InputField apiKeyField;

    private void Update() {
        if (Input.GetKeyDown(KeyCode.Escape))
            OnCancel();
    }
    
    public void OnPointerDown(PointerEventData eventData) {
        OnCancel();
     }

    public void Show() {
        gameObject.SetActive(true);
        addressField.text = PlayerPrefs.GetString("address", "");
        portField.text = PlayerPrefs.GetInt("port", 1970).ToString();
        apiKeyField.text = PlayerPrefs.GetString("apiKey", "");
    }

    public void Hide() {
        gameObject.SetActive(false);
    }

    public bool IsVisible() {
        return gameObject.activeSelf;
    }

    public void OnCancel() {
        Hide();
    }

    public void OnOK() {
        string address = addressField.text;
        string portStr = portField.text;
        string apiKey = apiKeyField.text;
        int port;

        if (address != null) {
            address = address.Trim();
            if (address.Length == 0) address = null;
        }
        if (portStr != null) {
            portStr = portStr.Trim();
            if (portStr.Length == 0)
                port = 1970;
            else
                port = int.Parse(portStr);
        } else
            port = 1970;
        if (apiKey != null) {
            apiKey = apiKey.Trim();
            if (apiKey.Length == 0) apiKey = null;
        }

        PlayerPrefs.SetString("address", address);
        PlayerPrefs.SetInt("port", port);
        PlayerPrefs.SetString("apiKey", apiKey);
        PlayerPrefs.Save();
        
        TCPRemoteClient.client.Reconnect();

        Hide();        
    }

}
