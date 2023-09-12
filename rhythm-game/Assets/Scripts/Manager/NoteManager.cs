using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class NoteManager : MonoBehaviour
{

    public int bpm = 0; // 노트를 1분에 이 개수만큼 생성하는 것으로 생각하면 된다. 
    List<NoteInfo> notes; // index0에 해당하는 note들의 정보를 저장

    int noteInterval = 800;

    

    [SerializeField] Transform tfNoteAppear = null;
    [SerializeField] GameObject goNote = null;
    [SerializeField] GameObject startLongNote = null;
    [SerializeField] GameObject endLongNote = null;
    int index_size;
    [SerializeField] int lineNum;
    // Start is called before the first frame update
    void Start()
    {
        //Debug.Log(this.gameObject.name);
        
        index_size = GameManager.instance.index_size;
        List<int> temp = check();

        if (lineNum < index_size)
        {
            gameObject.SetActive(true);
            gameObject.transform.position = new Vector3(temp[lineNum],550,0);
        }
        else
        {
            gameObject.SetActive(false);
        }
        

        switch (lineNum)
        {
            case 0 : notes = GameManager.instance.test_data.index0; break;
            case 1 : notes = GameManager.instance.test_data.index1; break;
            case 2 : notes = GameManager.instance.test_data.index2; break;
            case 3 : notes = GameManager.instance.test_data.index3; break;
            case 4 : notes = GameManager.instance.test_data.index4; break;
            case 5 : notes = GameManager.instance.test_data.index5; break;
            case 6 : notes = GameManager.instance.test_data.index6; break;
            case 7 : notes = GameManager.instance.test_data.index7; break;
            case 8 : notes = GameManager.instance.test_data.index8; break;
            case 9 : notes = GameManager.instance.test_data.index9; break;
            case 10: notes = GameManager.instance.test_data.index10; break;
            case 11: notes = GameManager.instance.test_data.index11; break;
            case 12: notes = GameManager.instance.test_data.index12; break;
            case 13: notes = GameManager.instance.test_data.index13; break;
            case 14: notes = GameManager.instance.test_data.index14; break;
            case 15: notes = GameManager.instance.test_data.index15; break;
            case 16: notes = GameManager.instance.test_data.index16; break;
            case 17: notes = GameManager.instance.test_data.index17; break;
            case 18: notes = GameManager.instance.test_data.index18; break;
            case 19: notes = GameManager.instance.test_data.index19; break;


            default: Debug.Log("Line Index 벗어남"); break;
        }

        if (lineNum == 3)
        {
            GameObject s_note = Instantiate(goNote, tfNoteAppear.position, Quaternion.identity);
            s_note.gameObject.tag = "StartNote";
        }

        for (int i = 0; i < notes.Count; i++)
        {
            //Debug.Log(notes[i].sec);

            GameObject targetNote = goNote;

            if(notes[i].property%10 == 1) targetNote = startLongNote;
            else if(notes[i].property%10 == 2) targetNote = endLongNote;

            GameObject t_note = Instantiate(targetNote, tfNoteAppear.position + new Vector3(0, notes[i].sec * noteInterval, 0), Quaternion.identity);
            t_note.transform.SetParent(this.transform);
        }
    }

    private void OnTriggerExit2D(Collider2D collision)
    { // Collider에 들어오면 발동
        if (collision.CompareTag("Note") || collision.CompareTag("StartNote"))
        {
            Destroy(collision.gameObject);
        }
    }

    private List<int> check()
    {
        List<int> positions = new List<int>();
        switch(index_size)
        {
            case 1:
                positions.Add(0);
                break;
            case 2:
                positions.Add(0);
                positions.Add(75);
                break;
            case 3:
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                break;
            case 4:
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                break;
            case 5:
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                break;
            case 6:
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                break;
            case 7:
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                break;
            case 8:
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                break;
            case 9:
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                break;
            case 10:
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                break;
            case 11:
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                break;
            case 12:
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                break;
            case 13:
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                break;
            case 14:
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                positions.Add(525);
                break;
            case 15:
                positions.Add(-525);
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                positions.Add(525);
                break;
            case 16:
                positions.Add(-525);
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                positions.Add(525);
                positions.Add(600);
                break;
            case 17:
                positions.Add(-600);
                positions.Add(-525);
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                positions.Add(525);
                positions.Add(600);
                break;
            case 18:
                positions.Add(-600);
                positions.Add(-525);
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                positions.Add(525);
                positions.Add(600);
                positions.Add(675);
                break;
            case 19:
                positions.Add(-675);
                positions.Add(-600);
                positions.Add(-525);
                positions.Add(-450);
                positions.Add(-375);
                positions.Add(-300);
                positions.Add(-225);
                positions.Add(-150);
                positions.Add(-75);
                positions.Add(0);
                positions.Add(75);
                positions.Add(150);
                positions.Add(225);
                positions.Add(300);
                positions.Add(375);
                positions.Add(450);
                positions.Add(525);
                positions.Add(600);
                positions.Add(675);
                break;
        }
        for(int i = 0;i<positions.Count;i++)
        {
            positions[i] = positions[i] + 950;
        }

        return positions;
    }
}
