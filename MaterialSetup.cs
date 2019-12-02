using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System.IO;

public class MaterialSetup : EditorWindow
{
    List<string> m_TexturePaths = new List<string>();
    bool m_AlsoFindJPG = false;

    [MenuItem("MoonShine/Find Material Texture")]
    public static void ShowWindow()
    {
        EditorWindow.GetWindow(typeof(MaterialSetup));
    }

    private void OnGUI()
    {
        EditorGUILayout.LabelField("--------  自動為Material找貼圖  --------");
        EditorGUILayout.LabelField("先選取貼圖資料夾，按下紀錄路徑按鈕，然後選取要尋找的材質球，按下Find按鈕即可");

        if (GUILayout.Button("選擇貼圖資料夾"))
        {
            m_TexturePaths.Clear();
            foreach(Object _Obj in Selection.objects)
            {
                m_TexturePaths.Add(AssetDatabase.GetAssetPath(_Obj));
            }
        }

        if(m_TexturePaths.Count == 0)
            EditorGUILayout.LabelField("尚未選擇貼圖資料夾！");
        else
            EditorGUILayout.LabelField("貼圖資料夾 : ");

        foreach(string _S in m_TexturePaths)
            EditorGUILayout.LabelField(_S);

        m_AlsoFindJPG = EditorGUILayout.Toggle("Also find JPG", m_AlsoFindJPG);

        if (GUILayout.Button("Find"))
        {
            if (m_TexturePaths.Count > 0)
                Find();
        }
    }

    void Find()
    {
        if (Selection.objects == null)
            return;
        if (Selection.objects.Length == 0)
            return;

        foreach (Object _Obj in Selection.objects)
        {
            Material _M = _Obj as Material;
            if (_M == null)
                continue;

            Texture2D _Texture = FindTex(_M.name, "_BaseColor");
            if (_Texture != null)
                _M.SetTexture("_MainTex", _Texture);

            _Texture = FindTex(_M.name, "_Metallic");
            if (_Texture != null)
                _M.SetTexture("_MetallicGlossMap", _Texture);

            _Texture = FindTex(_M.name, "_Normal");
            if (_Texture != null)
                _M.SetTexture("_BumpMap", _Texture);

            if (_M.HasProperty("_SpecGlossMap"))
            {
                _Texture = FindTex(_M.name, "_Roughness");
                if (_Texture != null)
                    _M.SetTexture("_SpecGlossMap", _Texture);
            }
        }
    }

    Texture2D FindTex(string materialName, string textureType)
    {
        Texture2D _Tex = null;

        foreach(string _Path in m_TexturePaths)
        {
            _Tex = (Texture2D)AssetDatabase.LoadAssetAtPath(_Path + "/" + materialName + textureType + ".png", typeof(Texture2D));

            //try lower
            if(_Tex == null)
                _Tex = (Texture2D)AssetDatabase.LoadAssetAtPath(_Path + "/" + materialName.ToLower() + textureType + ".png", typeof(Texture2D));

            //try jpg
            if (_Tex == null)
                _Tex = (Texture2D)AssetDatabase.LoadAssetAtPath(_Path + "/" + materialName + textureType + ".jpg", typeof(Texture2D));

            //try jpg lower
            if (_Tex == null)
                _Tex = (Texture2D)AssetDatabase.LoadAssetAtPath(_Path + "/" + materialName.ToLower() + textureType + ".jpg", typeof(Texture2D));
        }

        return _Tex;
    }
}
