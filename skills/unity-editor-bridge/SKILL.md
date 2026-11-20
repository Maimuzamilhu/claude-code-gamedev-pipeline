---
name: unity-editor-bridge
description: Drive a running Unity editor from the agent - run C# snippets inside the editor, wait for compiles, read the console, enter play mode and test gameplay, move objects, take screenshots and start builds. Use whenever the user works on a Unity project and wants the agent to do or check something in the editor, says "Unity MCP", "run this in Unity", "test it in play mode", "why does Unity show errors", or the bridge stops responding.
---

# Unity editor bridge

The agent talks to the Unity editor through an MCP server running inside the editor (the
open-source **MCP for Unity** package by CoplayDev: https://github.com/CoplayDev/unity-mcp).
It exposes tools such as `execute_code`, `read_console`, `manage_editor`, `manage_scene`,
`manage_gameobject`. The single most useful one is `execute_code`: it compiles a C# snippet and
runs it in the editor, so you can inspect and change anything the editor can.

## Setup (explain to the user step by step)

1. In Unity: **Window → Package Manager → + → Add package from git URL**, paste the URL from the
   CoplayDev README, then open **Window → MCP for Unity** and start the server.
2. Register it with the agent (the package's window shows the exact command for Claude Code).
3. Test: run `return Application.unityVersion;` through `execute_code`.

If the MCP tools are not available in the session, use `scripts/unity_bridge.py`. It is a
tiny client that talks to the same HTTP endpoint (default `http://127.0.0.1:8080/mcp`):

```bash
python scripts/unity_bridge.py -c "return UnityEditor.EditorApplication.isCompiling;"
python scripts/unity_bridge.py snippet.cs          # run a file
python scripts/unity_bridge.py --tool read_console '{"action":"get","types":["error"]}'
```

## Writing snippets that compile

The snippet compiler is older than your project compiler. Learned the hard way:

- Write **C# 6**: no `out var`, no tuples, no `is` patterns, no local functions, no `switch`
  expressions. Lambdas assigned to `System.Action<...>` variables work.
- Float literals need `f` (`0.5f`). Fully qualify editor types (`UnityEditor.AssetDatabase`).
- End with `return <something>;`. Return a short string summary, not huge objects.
- Avoid obsolete APIs the compiler rejects (for example `GetInstanceID` on newer Unity).
- Do not reuse a variable name already declared by the wrapper (`ok`, `result`); prefix yours.
- Private fields: use reflection
  (`typeof(T).GetField("name", BindingFlags.NonPublic | BindingFlags.Instance)`).

## Everyday recipes

- **After editing scripts**: `AssetDatabase.Refresh();` then poll
  `EditorApplication.isCompiling` every few seconds until false. Then read the console for
  `error CS` lines before doing anything else.
- **Count console entries**: `UnityEditor.LogEntries` is internal; reach it with
  `System.Type.GetType("UnityEditor.LogEntries,UnityEditor")` and call `GetCount`.
- **Play-mode test**: enter play mode with `EditorApplication.isPlaying = true`, wait, then run
  snippets that teleport the player, set inputs and read state. Return measured numbers
  (distance moved, which door angle, which state the enemy is in), not "looks fine".
- **Repeatable tests**: put long tests in a MonoBehaviour in the project (`Assets/Editor` or a
  dev-only script) and only trigger it from the snippet. The snippet stays short and the test
  lives in version control.
- **Screenshots**: render `Camera.main` into a RenderTexture and write a PNG, then look at it.

## When things go wrong

| Symptom | Cause and fix |
|---|---|
| Connection refused | Editor closed or server stopped. Ask the user to open the project and start the MCP window. If the editor is hung, restart it with `-projectPath`. |
| A long call (build, bake) "times out" | The socket drops but the editor keeps working. Do not start it twice. Watch a result file or the editor log instead. |
| `EditorApplication.delayCall` work never runs | The editor does not tick while its window is in the background. Call the method directly, or ask the user to click into Unity. |
| Errors you cannot see | The live log is `%LOCALAPPDATA%/Unity/Editor/Editor.log` (Windows), `~/Library/Logs/Unity/Editor.log` (macOS). The project's `Logs/` folder can be stale. |
| A modal dialog appeared (package resolver, "save scene?") | Snippets block until it closes. Ask the user to answer it, then turn the prompt off in that package's settings. |

## Builds

Builds can take 5 to 15 minutes. Write a build method in `Assets/Editor/` that writes a one-line
result (success, time, size, error count) to a text file, call it, and wait on that file.
Batch all fixes and build once at the end.

> **Example (HOLD STILL):** every gameplay fix was verified through this bridge with numbers:
> scripted play-mode probes that opened doors 120 times from random positions, played the whole
> story to all three endings, and soaked the robots for hours counting stuck events. The
> trailer frames were also captured through it (see `game-trailer`).
