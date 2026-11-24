// Template from the scaffold's unity module (docs/process/modules/unity.md, "Review").
// Verified under URP (Unity 6000.6, D3D12); not yet under HDRP. Copy it into a runtime folder of the Unity project
// (for example Assets/Scripts/Tools/HeadlessCapture.cs); from then on the copy is the project's own.
//
// Takes one picture from a player without a window:
//   <Player>.exe -batchmode -capture tmp/shots/<view-key>.png [-captureWidth 1440] [-captureHeight 900]
//                [-captureCamera "<GameObject name>"] [-captureFrames 30] -logFile tmp/shots/<view-key>.log
// -batchmode keeps the window away; never add -nographics (no graphics device: the picture would be flat grey, so
// the capture refuses with exit 3).
// The project sets up the view itself (scene, seed, camera position) from its own arguments before the capture.
using System;
using System.Collections;
using System.IO;
using UnityEngine;

public sealed class HeadlessCapture : MonoBehaviour
{
    string outputPath;
    string cameraName;
    int width = 1440;
    int height = 900;
    int settleFrames = 30; // frames to wait before the picture: streaming, LODs and first-frame effects settle

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void InstallIfRequested()
    {
        var args = Environment.GetCommandLineArgs();
        var path = Argument(args, "-capture");
        if (path == null)
            return;
        var host = new GameObject(nameof(HeadlessCapture));
        DontDestroyOnLoad(host);
        var capture = host.AddComponent<HeadlessCapture>();
        capture.outputPath = path;
        capture.cameraName = Argument(args, "-captureCamera");
        capture.width = IntArgument(args, "-captureWidth", capture.width);
        capture.height = IntArgument(args, "-captureHeight", capture.height);
        capture.settleFrames = IntArgument(args, "-captureFrames", capture.settleFrames);
    }

    static string Argument(string[] args, string name)
    {
        var i = Array.IndexOf(args, name);
        return i >= 0 && i + 1 < args.Length ? args[i + 1] : null;
    }

    static int IntArgument(string[] args, string name, int fallback) =>
        int.TryParse(Argument(args, name), out var value) ? value : fallback;

    IEnumerator Start()
    {
        if (SystemInfo.graphicsDeviceType == UnityEngine.Rendering.GraphicsDeviceType.Null)
        {
            Debug.LogError("[HeadlessCapture] no graphics device (-nographics?); nothing written");
            Application.Quit(3);
            yield break;
        }

        for (var i = 0; i < settleFrames; i++)
            yield return null;

        var camera = FindCamera();
        if (camera == null)
        {
            Debug.LogError($"[HeadlessCapture] no camera named '{cameraName ?? "(MainCamera tag)"}'; nothing written");
            Application.Quit(2);
            yield break;
        }

        var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
        var previousTarget = camera.targetTexture;
        camera.targetTexture = target;
        camera.Render();
        camera.targetTexture = previousTarget;

        var previousActive = RenderTexture.active;
        RenderTexture.active = target;
        var picture = new Texture2D(width, height, TextureFormat.RGB24, false);
        picture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        picture.Apply();
        RenderTexture.active = previousActive;

        var fullPath = Path.GetFullPath(outputPath);
        Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
        File.WriteAllBytes(fullPath, picture.EncodeToPNG());
        Debug.Log($"[HeadlessCapture] wrote {fullPath} ({width}x{height}) from camera '{camera.name}'");

        Destroy(picture);
        target.Release();
        Destroy(target);
        Application.Quit(0);
    }

    Camera FindCamera()
    {
        if (cameraName == null)
            return Camera.main;
        // No ?. here: Unity objects override == null, and ?. would skip that check.
        var host = GameObject.Find(cameraName);
        return host != null ? host.GetComponent<Camera>() : null;
    }
}
