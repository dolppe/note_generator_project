using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StartMusic : MonoBehaviour // only in Line3 Hit Frame to start music
{
    AudioSource myAudio; //BGM

    private void Start()
    {
        myAudio = GetComponent<AudioSource>();
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (!GameManager.instance.musicStart && collision.CompareTag("StartNote"))
        {
            myAudio.Play();
            GameManager.instance.musicStart = true;
        }
    }
}
