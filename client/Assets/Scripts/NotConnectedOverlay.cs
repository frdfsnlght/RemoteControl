using UnityEngine;

public class NotConnectedOverlay : MonoBehaviour {

    public void Show() {
        gameObject.SetActive(true);
    }

    public void Hide() {
        gameObject.SetActive(false);
    }

    public bool IsVisible() {
        return gameObject.activeSelf;
    }
    
}
