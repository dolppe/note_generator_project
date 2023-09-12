using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager instance;
    //AudioSource myAudio;

    // 외부에서 싱글톤 오브젝트를 가져올때 사용할 프로퍼티
    public static GameManager Instance
    {
        get
        {
            // 만약 싱글톤 변수에 아직 오브젝트가 할당되지 않았다면
            if (instance == null)
                // 씬에서 GameManager 오브젝트를 찾아 할당
                instance = FindObjectOfType<GameManager>();

            // 싱글톤 오브젝트를 반환
            return instance;
        }
    }

    public TestData test_data;
    public bool musicStart = false;
    public int index_size;
    [SerializeField]
    public string fileName;

    void Awake()
    {
        instance = this;
        

        string test_json_str = File.ReadAllText(Application.dataPath + fileName)
               .Replace("\"0\"", "\"index0\"").Replace("\"1\"", "\"index1\"").Replace("\"2\"", "\"index2\"").Replace("\"3\"", "\"index3\"").Replace("\"4\"", "\"index4\"").Replace("\"5\"", "\"index5\"").Replace("\"6\"", "\"index6\"")
               .Replace("\"7\"", "\"index7\"").Replace("\"8\"", "\"index8\"").Replace("\"9\"", "\"index9\"").Replace("\"10\"", "\"index10\"").Replace("\"11\"", "\"index11\"").Replace("\"12\"", "\"index12\"").Replace("\"13\"", "\"index13\"")
               .Replace("\"14\"", "\"index14\"").Replace("\"15\"", "\"index15\"").Replace("\"16\"", "\"index16\"").Replace("\"17\"", "\"index17\"").Replace("\"18\"", "\"index18\"").Replace("\"19\"", "\"index19\"")
               .Replace(" ", string.Empty).Replace("\n", string.Empty).Replace("\r", string.Empty).Replace("\t", string.Empty);

        int start_idx = test_json_str.IndexOf("notes", 0, test_json_str.Length) + 7;
        test_json_str = test_json_str.Substring(start_idx, test_json_str.Length - start_idx - 1);
        for(int i = 0;i<20;i++)
        {
            if(test_json_str.IndexOf("index" + i, 0) == -1 )
            {
                index_size = i;
                break;
            }
        }


        //Debug.Log(test_json_str);

        test_data = JsonUtility.FromJson<TestData>(test_json_str);
        //test_data.printData();
        Debug.Log(test_data);
    }

}

[System.Serializable]
public class TestData
{
    public List<NoteInfo> index0;
    public List<NoteInfo> index1;
    public List<NoteInfo> index2;
    public List<NoteInfo> index3;
    public List<NoteInfo> index4;
    public List<NoteInfo> index5;
    public List<NoteInfo> index6;
    public List<NoteInfo> index7;
    public List<NoteInfo> index8;
    public List<NoteInfo> index9;
    public List<NoteInfo> index10;
    public List<NoteInfo> index11;
    public List<NoteInfo> index12;
    public List<NoteInfo> index13;
    public List<NoteInfo> index14;
    public List<NoteInfo> index15;
    public List<NoteInfo> index16;
    public List<NoteInfo> index17;
    public List<NoteInfo> index18;
    public List<NoteInfo> index19;

    public void printData()
    {
        for (int i = 0; i < index0.Count; i++) { index0[i].printNoteInfo(); }
        for (int i = 0; i < index1.Count; i++) { index1[i].printNoteInfo(); }
        for (int i = 0; i < index2.Count; i++) { index2[i].printNoteInfo(); }
        for (int i = 0; i < index3.Count; i++) { index3[i].printNoteInfo(); }
        for (int i = 0; i < index4.Count; i++) { index4[i].printNoteInfo(); }
        for (int i = 0; i < index5.Count; i++) { index5[i].printNoteInfo(); }
        for (int i = 0; i < index6.Count; i++) { index6[i].printNoteInfo(); }
        for (int i = 0; i < index7.Count; i++) { index7[i].printNoteInfo(); }
        for (int i = 0; i < index8.Count; i++) { index8[i].printNoteInfo(); }
        for (int i = 0; i < index9.Count; i++) { index9[i].printNoteInfo(); }
        for (int i = 0; i < index10.Count; i++) { index10[i].printNoteInfo(); }
        for (int i = 0; i < index11.Count; i++) { index11[i].printNoteInfo(); }
        for (int i = 0; i < index12.Count; i++) { index12[i].printNoteInfo(); }
        for (int i = 0; i < index13.Count; i++) { index13[i].printNoteInfo(); }
        for (int i = 0; i < index14.Count; i++) { index14[i].printNoteInfo(); }
        for (int i = 0; i < index15.Count; i++) { index15[i].printNoteInfo(); }
        for (int i = 0; i < index16.Count; i++) { index16[i].printNoteInfo(); }
        for (int i = 0; i < index17.Count; i++) { index17[i].printNoteInfo(); }
        for (int i = 0; i < index18.Count; i++) { index18[i].printNoteInfo(); }
        for (int i = 0; i < index19.Count; i++) { index19[i].printNoteInfo(); }

    }

}

//[System.Serializable]
//public class TestData
//{
//    public List<NoteInfo> index0;
//    public List<NoteInfo> index1;
//    public List<NoteInfo> index2;
//    public List<NoteInfo> index3;
//    public List<NoteInfo> index4;
//    public List<NoteInfo> index5;
//    public List<NoteInfo> index6;
//    public List<NoteInfo> index7;
//    public List<NoteInfo> index8;
//    public List<NoteInfo> index9;
//    public List<NoteInfo> index10;
//    public List<NoteInfo> index11;
//    public List<NoteInfo> index12;

//    public void printData()
//    {
//        for (int i = 0; i < index0.Count; i++) { index0[i].printNoteInfo(); }
//        for (int i = 0; i < index1.Count; i++) { index1[i].printNoteInfo(); }
//        for (int i = 0; i < index2.Count; i++) { index2[i].printNoteInfo(); }
//        for (int i = 0; i < index3.Count; i++) { index3[i].printNoteInfo(); }
//        for (int i = 0; i < index4.Count; i++) { index4[i].printNoteInfo(); }
//        for (int i = 0; i < index5.Count; i++) { index5[i].printNoteInfo(); }
//        for (int i = 0; i < index6.Count; i++) { index6[i].printNoteInfo(); }
//        for (int i = 0; i < index7.Count; i++) { index7[i].printNoteInfo(); }
//        for (int i = 0; i < index8.Count; i++) { index8[i].printNoteInfo(); }
//        for (int i = 0; i < index9.Count; i++) { index9[i].printNoteInfo(); }
//        for (int i = 0; i < index10.Count; i++) { index10[i].printNoteInfo(); }
//        for (int i = 0; i < index11.Count; i++) { index11[i].printNoteInfo(); }
//        for (int i = 0; i < index12.Count; i++) { index12[i].printNoteInfo(); }
//    }
//}


[System.Serializable]
public class NoteInfo
{
    public int tick;
    public int duration;
    public int channelId;
    public int objectId;
    public int property;
    public int eventId;
    public int tickEnd;
    public float sec;
    public float secEnd;
    public int indexInChannel;

    public void printNoteInfo()
    {
        Debug.Log("tick : " + tick);
        Debug.Log("duration : " + duration);
        Debug.Log("channelId : " + channelId);
        Debug.Log("objectId : " + objectId);
        Debug.Log("property : " + property);
        Debug.Log("eventId : " + eventId);
        Debug.Log("tickEnd : " + tickEnd);
        Debug.Log("sec : " + sec);
        Debug.Log("secEnd : " + secEnd);
        Debug.Log("indexInChannel : " + indexInChannel);
    }
}

