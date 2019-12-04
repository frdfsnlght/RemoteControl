using UnityEngine;

public class NotConnectedOverlay : MonoBehaviour {

    private void Awake() {
        Hide();
    }

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
