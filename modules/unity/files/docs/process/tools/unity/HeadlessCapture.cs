// Template from the scaffold's unity module (docs/process/modules/unity.md, "Review").
// Verified under URP and HDRP (Unity 6000.6, D3D12). Copy it into a runtime folder of the Unity project
// (for example Assets/Scripts/Tools/HeadlessCapture.cs); from then on the copy is the project's own.
//
// Takes one picture from a player without a window:
//   <Player>.exe -batchmode -capture tmp/shots/<view-key>.png [-captureWidth 1440] [-captureHeight 900]
//                [-captureCamera "<GameObject name>"] [-captureFrames N] -logFile tmp/shots/<view-key>.log
// A batchmode player renders no camera by itself, so the camera renders into the picture's texture every settle frame:
// streaming, LODs and auto-exposure settle (HDRP's exposure needs about 600 frames, the default there; 30 elsewhere).
// Exit codes: 0 written, 2 no camera, 3 no graphics device, 4 the picture is flat, one colour or nearly
// (written, for a look).
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
    int settleFrames = -1; // frames rendered before the picture; -1: 600 under HDRP (auto-exposure), else 30

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

        var camera = FindCamera();
        if (camera == null)
        {
            Debug.LogError($"[HeadlessCapture] no camera named '{cameraName ?? "(MainCamera tag)"}'; nothing written");
            Application.Quit(2);
            yield break;
        }

        if (settleFrames < 0)
            settleFrames = IsHdrp() ? 600 : 30;
        var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
        var previousTarget = camera.targetTexture;
        camera.targetTexture = target;
        for (var i = 0; i < settleFrames; i++)
        {
            camera.Render();
            yield return null;
        }
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
        var flat = IsFlat(picture);
        if (flat)
            Debug.LogError($"[HeadlessCapture] {fullPath} is flat (nearly one colour): the camera did not render (exposure, " +
                           "pipeline, or nothing in view); exit 4");
        else
            Debug.Log($"[HeadlessCapture] wrote {fullPath} ({width}x{height}, {settleFrames} settle frames) " +
                      $"from camera '{camera.name}'");

        Destroy(picture);
        target.Release();
        Destroy(target);
        Application.Quit(flat ? 4 : 0);
    }

    static bool IsHdrp()
    {
        var pipeline = UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline;
        return pipeline != null && pipeline.GetType().Name.Contains("HDRenderPipeline");
    }

    // Flat: the brightness hardly varies (standard deviation under 2 of 255), which a white-out or a black frame gives
    // even when a few values differ by one.
    static bool IsFlat(Texture2D picture)
    {
        var pixels = picture.GetPixels32();
        double sum = 0, sumOfSquares = 0;
        foreach (var p in pixels)
        {
            double luma = 0.2126 * p.r + 0.7152 * p.g + 0.0722 * p.b;
            sum += luma;
            sumOfSquares += luma * luma;
        }
        var mean = sum / pixels.Length;
        return sumOfSquares / pixels.Length - mean * mean < 2.0 * 2.0;
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
