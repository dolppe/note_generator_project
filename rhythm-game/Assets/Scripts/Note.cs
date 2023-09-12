using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Note : MonoBehaviour
{
    public float noteSpeed;
    
    // Update is called once per frame
    void Update()
    {
        transform.localPosition += Vector3.down * noteSpeed * Time.deltaTime; // 1초에 노트 스피드만큼 아래쪽으로 이동
    }
}
