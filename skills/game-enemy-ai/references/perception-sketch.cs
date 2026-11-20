// A compact structure for channel-based perception with a suspicion meter (Unity C#).
// Adapt the channels to your game. Not a drop-in file: read it, then build your own.
using System.Collections.Generic;
using UnityEngine;

public enum Sense { Sight, Hearing, Custom }

/// Per-channel concealment of a hiding spot: 0 = no cover, 1 = fully hidden from that sense.
[System.Serializable]
public struct Concealment { public float sight, hearing, custom; }

/// Every sound the world makes goes here; enemies poll it. The player can reason about what
/// gave them away, which is what makes the AI feel fair.
public static class NoiseBoard
{
    public struct Noise { public Vector3 pos; public float loudness; public float time; }
    static readonly List<Noise> noises = new List<Noise>();

    public static void Emit(Vector3 pos, float loudness)
    {
        noises.Add(new Noise { pos = pos, loudness = loudness, time = Time.time });
        if (noises.Count > 64) noises.RemoveAt(0);
    }

    /// Loudest noise heard at `ear` in the last `window` seconds after distance falloff and wall muffling.
    public static bool Loudest(Vector3 ear, float window, LayerMask walls, out Noise best, out float heard)
    {
        best = default(Noise); heard = 0f;
        foreach (var n in noises)
        {
            if (Time.time - n.time > window) continue;
            float d = Vector3.Distance(ear, n.pos);
            float v = n.loudness / (1f + d * d * 0.05f);
            if (Physics.Linecast(ear, n.pos, walls)) v *= 0.35f;          // through a wall
            if (v > heard) { heard = v; best = n; }
        }
        return heard > 0.05f;
    }
}

public class EnemyPerception : MonoBehaviour
{
    public Transform eyes;
    public float viewRange = 14f, viewAngle = 55f;
    public float riseSight = 0.9f, riseHearing = 0.6f, drain = 0.25f;   // per second
    public LayerMask walls;

    [Range(0, 1)] public float suspicion;      // 0..1, shown to the player
    public Vector3 lastCue;                    // where to investigate

    public float SightOf(Transform target, Concealment hide, float lightLevel, float moveSpeed)
    {
        Vector3 to = target.position + Vector3.up * 1.2f - eyes.position;
        if (to.magnitude > viewRange || Vector3.Angle(eyes.forward, to) > viewAngle) return 0f;
        if (Physics.Linecast(eyes.position, eyes.position + to, walls)) return 0f;
        float closeness = 1f - to.magnitude / viewRange;
        float motion = Mathf.Clamp01(0.35f + moveSpeed * 0.3f);          // still players are harder to see
        return closeness * motion * Mathf.Lerp(0.3f, 1f, lightLevel) * (1f - hide.sight);
    }

    public void Tick(Transform player, Concealment hide, float lightLevel, float moveSpeed)
    {
        float s = SightOf(player, hide, lightLevel, moveSpeed);
        NoiseBoard.Noise n; float heard;
        bool hears = NoiseBoard.Loudest(eyes.position, 1.5f, walls, out n, out heard);
        float gain = s * riseSight + (hears ? heard * riseHearing * (1f - hide.hearing) : 0f);
        if (gain > 0f)
        {
            suspicion = Mathf.Clamp01(suspicion + gain * Time.deltaTime);
            lastCue = s > 0f ? player.position : n.pos;
        }
        else suspicion = Mathf.Max(0f, suspicion - drain * Time.deltaTime);
    }
    // States read the meter: > 0.3 curious, > 0.6 investigate lastCue, 1.0 spotted -> pursue.
}
