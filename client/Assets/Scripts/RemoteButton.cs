using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class RemoteButton : Button {

    private AudioSource audioSource;
    private TCPRemoteClient client;

    protected override void Start() {
        base.Start();
        audioSource = transform.parent.GetComponent<AudioSource>();
        client = TCPRemoteClient.client;
    }

    public override void OnPointerDown(PointerEventData eventData) {
        base.OnPointerDown(eventData);
        if (eventData.button != PointerEventData.InputButton.Left)
            return;
        audioSource.Play();
        client.sendButtonDown(gameObject.name);
     }

    public override void OnPointerUp(PointerEventData eventData) {
        base.OnPointerUp(eventData);
        if (eventData.button != PointerEventData.InputButton.Left)
            return;
        client.sendButtonUp(gameObject.name);
     }

}
