#if UNITY_EDITOR
using System.Collections;
using System.IO;
using UnityEngine;

/// <summary>
/// Editor-only trailer capture with a locked clock. Time.captureFramerate makes every frame advance
/// the game by exactly 1/fps seconds no matter how long rendering takes, so lights, particles and
/// animation never blink or stutter (screen recording at the editor's uneven real-time rate does).
/// Each frame of Camera.main is written as a JPG; assemble them with make_trailer.py.
///
/// Usage (play mode, e.g. from an editor script or the Unity MCP bridge):
///   TrailerRecorder.Record("Recordings/shot01", 4.2f, t => { /* t = 0..1: move camera / actors */ });
/// </summary>
public sealed class TrailerRecorder : MonoBehaviour
{
    public static bool Busy { get; private set; }
    public static int Written { get; private set; }

    public static int Fps = 30;
    public static int Width = 1920, Height = 1080;
    public static int JpgQuality = 93;

    public static void Record(string dir, float seconds, System.Action<float> step)
    {
        if (Busy) { Debug.LogWarning("[Trailer] already recording"); return; }
        var go = new GameObject("__TrailerRecorder");
        go.AddComponent<TrailerRecorder>().StartCoroutine(go.GetComponent<TrailerRecorder>().Run(dir, seconds, step));
    }

    private IEnumerator Run(string dir, float seconds, System.Action<float> step)
    {
        Busy = true; Written = 0;
        Directory.CreateDirectory(dir);
        Time.captureFramerate = Fps;
        int n = Mathf.Max(1, Mathf.RoundToInt(seconds * Fps));
        var rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
        var tex = new Texture2D(Width, Height, TextureFormat.RGB24, false);

        for (int w = 0; w < 6; w++) { if (step != null) step(0f); yield return null; }   // let poses settle

        for (int i = 0; i < n; i++)
        {
            if (step != null)
            {
                try { step(i / (float)Mathf.Max(1, n - 1)); }
                catch (System.Exception e) { Debug.LogWarning("[Trailer] " + e.Message); }
            }
            yield return new WaitForEndOfFrame();
            var cam = Camera.main;
            if (cam == null) continue;
            var prev = cam.targetTexture;
            cam.targetTexture = rt;
            cam.Render();
            cam.targetTexture = prev;
            var was = RenderTexture.active;
            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            tex.Apply(false);
            RenderTexture.active = was;
            File.WriteAllBytes(Path.Combine(dir, "f_" + i.ToString("D4") + ".jpg"), tex.EncodeToJPG(JpgQuality));
            Written = i + 1;
        }

        Time.captureFramerate = 0;
        rt.Release();
        Destroy(tex);
        Busy = false;
        Debug.Log("[Trailer] wrote " + Written + " frames to " + dir);
        Destroy(gameObject);
    }
}
#endif
