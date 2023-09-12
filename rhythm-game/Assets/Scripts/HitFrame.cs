using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HitFrame : MonoBehaviour
{
    AudioSource mySound; //Hit Sound
    float time;

    private void Start()
    {
        mySound = GetComponent<AudioSource>();
    }

    private void Update()
    {
        time += Time.deltaTime;
        //Debug.Log(time);
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.CompareTag("Note"))
        {
            mySound.Play();
            Debug.Log(time);
        }
    }

}
