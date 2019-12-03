using UnityEngine;
using System;
using System.IO;
using System.Text;
using System.Net.Sockets;
using System.Threading;
using System.Reflection;

public class TCPRemoteClient : MonoBehaviour {

    public static TCPRemoteClient client;

    public string address = "localhost";
    public int port = 1970;
    public string apiKey = null;

    public LEDs leds;

    private bool connected = false;
    private bool quit = false;
    private Thread thread = null;
    private TcpClient socket = null;
    private StreamReader reader = null;
    private StreamWriter writer = null;
    private ButtonMessage buttonMessage = new ButtonMessage();

    private void Awake() {
        client = this;
        thread = new Thread(Loop);
        thread.IsBackground = true;
        thread.Start();
    }

    private void OnApplicationQuit() {
        Quit();
    }

    private void Loop() {
        while (!quit) {
            try {
                socket = new TcpClient();

                Debug.Log("Connecting to " + address + ":" + port + "...\n");
                socket.Connect(address, port);
                reader = new StreamReader(socket.GetStream(), Encoding.UTF8);
                writer = new StreamWriter(socket.GetStream(), Encoding.UTF8);
                writer.AutoFlush = true;
                
                HelloMessage helloMessage = new HelloMessage();
                helloMessage.name = "TCPRemote";
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

            } catch (Exception e) {
                connected = false;
                Debug.LogException(e);
            } finally {
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
