using UnityEngine;
using System;
using System.IO;
using System.Text;
using System.Net.Sockets;
using System.Threading;
using System.Reflection;

public class TCPRemoteClient : MonoBehaviour {

    public static TCPRemoteClient client;

    public LEDs leds;

    [System.NonSerialized]
    public bool connected = false;

    private bool quit = false;
    private Thread thread = null;
    private TcpClient socket = null;
    private StreamReader reader = null;
    private StreamWriter writer = null;
    private ButtonMessage buttonMessage = new ButtonMessage();

    private string address = null;
    private int port = 1970;
    private string apiKey = null;

    private void Awake() {
        client = this;
        thread = new Thread(Loop);
        thread.IsBackground = true;
        thread.Start();
    }

    private void Start() {
        Reconnect();
    }

    private void OnApplicationQuit() {
        Quit();
    }

    private void Loop() {
        while (!quit) {
            try {
                socket = new TcpClient();

                if ((address != null) && (address != "")) {
                    Debug.Log("Connecting to " + address + ":" + port + "...\n");
                    socket.Connect(address, port);
                    reader = new StreamReader(socket.GetStream(), Encoding.UTF8);
                    writer = new StreamWriter(socket.GetStream(), Encoding.UTF8);
                    writer.AutoFlush = true;
                    
                    HelloMessage helloMessage = new HelloMessage();
                    helloMessage.hello = "TCPRemote";
                    helloMessage.apiKey = apiKey;
                    sendData(helloMessage);

                    Debug.Log("Connected\n");
                    connected = true;

                    string json;
                    while ((json = reader.ReadLine()) != null) {
                        UnknownMessage msg = JsonUtility.FromJson<UnknownMessage>(json);
                        processMessage(msg, json);
                    }
                    Debug.Log("Disconnected\n");
                }

            } catch (Exception e) {
                connected = false;
                Debug.LogException(e);
            } finally {
                connected = false;
                if (reader != null) reader.Dispose();
                if (writer != null) writer.Dispose();
                if (socket != null) socket.Dispose();
                reader = null;
                writer = null;
                socket = null;
            }

            if (!quit) Thread.Sleep(1000);
        }
    }

    private void processMessage(UnknownMessage msg, string json) {
        if (msg.error != null) {
            Debug.LogError("Client: " + msg.error);
            return;
        }
        if (msg.action == "setLEDs") {
            SetLEDsMessage setLEDsMessage = JsonUtility.FromJson<SetLEDsMessage>(json);
            leds.SetColors(setLEDsMessage.colors);
        }
    }

    public void Reconnect() {
        address = PlayerPrefs.GetString("address", null);
        port = PlayerPrefs.GetInt("port", 1970);
        apiKey = PlayerPrefs.GetString("apiKey", null);
        if (! connected) return;
        if (reader != null) reader.Close();
    }

    public void Quit() {
        if (quit) return;
        quit = true;
        if (reader != null) reader.Close();
    }

    public void sendButtonDown(string button) {
        if (! connected) return;
        buttonMessage.button = button;
        buttonMessage.state = "down";
        sendData(buttonMessage);
    }

    public void sendButtonUp(string button) {
        if (! connected) return;
        buttonMessage.button = button;
        buttonMessage.state = "up";
        sendData(buttonMessage);
    }

    private void sendData(object data) {
        string json = JsonUtility.ToJson(data);
        writer.WriteLine(json);
    }

}
