# Generals native macOS merge map

**Goal:** one Apple-Silicon-native Zero Hour project that keeps dvcdsys's direct D3D8→Metal renderer and CWC support, adds Log1037's Retina/HiDPI and ProGen work, and ports OKJID's AVAudioEngine backend.

**Recommended base:** `dvcdsys/GeneralsGameCode-macOS` (`main`). Keep its renderer and CWC functionality as the canonical implementation. Do not merge any of the three repositories wholesale.

This is a verified source-level plan, not a claim that the three trees have been locally compiled or diffed together in this environment. GitHub's current branch-comparison view did not expose the full `progen` diff here. The included audit commands resolve the remaining ProGen and OKJID commit/file inventories locally without guessing hashes or paths.

## 1. Architecture decision

| Piece | Canonical source | Integration method | Decision |
|---|---|---|---|
| D3D8 → Metal renderer | dvcdsys | Keep in place | **Do not replace** |
| CWC support and Guard-from-Position work | dvcdsys | Keep in place; use as regression test | **Do not re-port** |
| Retina / HiDPI / window resize behavior | Log1037 | Port the behavior, adapt implementation to dvcdsys's Metal/display code | **Manual port** |
| ProGen code fixes | Log1037 `progen` | Extract source-only delta and port hunk-by-hunk | **Manual port; exact delta listed by audit script** |
| ProGen mod package | Log1037 `progen` | Keep outside the engine; install/select as mod data, subject to its license | **Separate from engine** |
| AVAudioEngine backend | OKJID `okji/feat/macos-port` | Port audio adapter and build integration only | **Selective file port** |
| OKJID Metal renderer | OKJID | None | **Do not copy**; it duplicates dvcdsys's D3D8 adapter with a different implementation |
| OKJID Cocoa main loop/window layer | OKJID | Reference only; port isolated fixes only if required | **Do not copy wholesale** |
| Log1037 SDL/DXVK build plumbing | Log1037 | None, except portable concepts | **Do not copy** |
| Log1037 launcher | Log1037 | Keep dvcdsys launcher; selectively compare path-picker behavior | **Do not replace** |

Sources: [dvcdsys project](https://github.com/dvcdsys/GeneralsGameCode-macOS), [Log1037 project and branch scope](https://github.com/Log1037/CNC-Generals-for-macOS/blob/main/README.en.md), [OKJID macOS port architecture](https://github.com/OKJID/GameClient/blob/okji/feat/macos-port/Platform/MacOS/docs/README.md).

## 2. Log1037's published commit series: exact commit/file map

Log1037 documented and published eight focused commits on August 10, 2026. The abbreviations below are the short SHAs shown in its merged [PR #1](https://github.com/Log1037/CNC-Generals-for-macOS/pull/1). The PR merge commit is `9358726`. These are **Log1037 changes**, not dvcdsys commit IDs.

| Log1037 commit | Feature | Relevant file groups recorded in the engineering log | Decision for dvcdsys |
|---|---|---|---|
| `d19874f` — `fix(filesystem): support portable asset roots` | Game-data/runtime roots and paths work independently of one maintainer's machine | `Core/GameEngineDevice/Source/StdDevice/Common/StdBIGFileSystem.cpp`; `Core/GameEngineDevice/Source/StdDevice/Common/StdLocalFileSystem.cpp`; `scripts/get-assets.sh`; `scripts/build/macos/deploy-macos-zh.sh`; `scripts/build/macos/run-macos-zh.sh`; `packaging/macos/GeneralsXLauncher.m`; `scripts/build/macos/package-macos-zh-app.sh`; `安装将军正版资源.command` | Compare against dvcdsys's existing `\` path normalization, asset picker, and launcher first. Port only missing behavior. Do not copy the launcher or its runtime layout blindly. |
| `0af28ba` — `fix(timing): decouple render and simulation rates` | Fixed-step accumulator; rendering cap and simulation speed become separate | `Core/GameEngine/Include/Common/FramePacer.h`; `Core/GameEngine/Source/Common/FramePacer.cpp`; `Core/GameEngine/Include/Common/FrameRateLimit.h`; `Core/GameEngine/Source/Common/FrameRateLimit.cpp`; `GeneralsMD/Code/GameEngine/Source/Common/GameEngine.cpp`; `GeneralsMD/Code/GameEngine/Source/GameLogic/ScriptEngine/ScriptActions.cpp`; `GeneralsMD/Code/CompatLib/Source/time_compat.cpp`; related view/command translation files | **Do not transplant initially.** dvcdsys already reports 120-FPS rendering with logic timing decoupled. Test parity first; borrow only a demonstrated missing fix. |
| `40051cb` — `fix(rendering): restore videos and scaled effects` | Video/cinematic and scaled/offscreen effect fixes | `Core/GameEngineDevice/Source/W3DDevice/GameClient/W3DVideoBuffer.cpp`; `Core/GameEngineDevice/Source/VideoDevice/FFmpeg/FFmpegVideoPlayer.cpp`; `GeneralsMD/Code/GameEngineDevice/Source/VideoDevice/FFmpeg/FFmpegVideoPlayer.cpp`; `Core/GameEngine/Source/GameClient/GUI/LoadScreen.cpp`; `Core/GameEngineDevice/Source/W3DDevice/GameClient/W3DShaderManager.cpp`; `Core/GameEngineDevice/Source/W3DDevice/GameClient/W3DSmudge.cpp`; `Core/GameEngineDevice/Source/W3DDevice/GameClient/W3DTreeBuffer.cpp`; `cmake/dx8.cmake` | **Selective port only.** Keep engine-level video/effect fixes after reviewing each hunk. Drop assumptions about DXVK texture locks, MoltenVK, and the SDL swapchain. Test against both vanilla and CWC. |
| `762b24f` — `fix(macos): improve Retina windows and shutdown` | Physical-pixel vs logical-point model; resize and fullscreen fixes; safe shutdown | `GeneralsMD/Code/Main/SDL3Main.cpp`; `GeneralsMD/Code/GameEngineDevice/Source/SDL3GameEngine.cpp`; `GeneralsMD/Code/GameEngineDevice/Source/W3DDevice/GameClient/W3DDisplay.cpp`; `Core/Libraries/Source/WWVegas/WW3D2/dx8wrapper.cpp`; `GeneralsMD/Code/Main/MacDisplayKick.cpp`; `GeneralsMD/Code/Main/CMakeLists.txt`; `cmake/config-build.cmake`; `cmake/apply-dxvk-macos-retina.cmake`; `scripts/build/macos/bundle-macos-generals.sh`; `scripts/build/macos/bundle-macos-zh.sh` | **Port the behavior, not the commit.** `SDL3Main.cpp`, `SDL3GameEngine.cpp`, `apply-dxvk-macos-retina.cmake`, and DXVK/swapchain changes are not portable to the direct-Metal renderer. Implement point/pixel separation, resize propagation, resolution-dependent resource rebuilds, and fullscreen-state tracking against dvcdsys's own platform/Metal code. Add the CoreGraphics “display kick” recovery only if a reproducible stranded-fullscreen bug justifies it. |
| `4831537` — `fix(fonts): improve CJK fallback and metrics` | Font fallback, glyph metrics, scaling | `Core/GameEngine/Source/GameClient/GlobalLanguage.cpp`; `Core/Libraries/Source/WWVegas/WW3D2/render2dsentence.cpp`; `GeneralsMD/Code/GameEngineDevice/Source/W3DDevice/GameClient/GUI/W3DGameFont.cpp`; `Core/GameEngine/Source/GameClient/Input/Mouse.cpp`; Generals/ZH `ControlBar.cpp` variants; deploy/run scripts | Optional but potentially useful at Retina resolutions. Port the font/glyph logic only after comparing dvcdsys's shared-engine revision. Don't copy SDL-specific cursor drawing or the Log font deployment assumptions without adapting them. |
| `a590cd8` — `feat(extras): add localized display controls` | In-game settings panel and local single-player helpers | `GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks/Menus/ExtrasMenu.cpp`; `Core/GameEngine/Source/GameClient/GUI/Gadget/GadgetHorizontalSlider.cpp`; `Core/GameEngineDevice/Source/W3DDevice/GameClient/GUI/Gadget/W3DHorizontalSlider.cpp`; `GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks/Menus/QuitMenu.cpp`; `GeneralsMD/Code/GameEngine/Source/GameClient/MessageStream/MetaEvent.cpp` | Out of initial scope. Add later as a discrete UI feature; audit any gameplay/helper actions so they remain disabled in network games and replays. |
| `cb1df93` — `build(macos): add portable local app packaging` | Launcher, resource selection, app packaging | `packaging/macos/GeneralsXLauncher.m`; `scripts/build/macos/package-macos-zh-app.sh`; `scripts/build/macos/deploy-macos-zh.sh`; `scripts/build/macos/run-macos-zh.sh`; `scripts/get-assets.sh`; `docs/BUILD/MACOS.md` | Keep dvcdsys's existing launcher and bundle workflow. Port only missing user-facing asset-discovery behavior if wanted. Do not import this commit's DXVK/Vulkan build assumptions. |
| `85ac2c8` — `docs(macos): document personalized fork setup` | Setup/build/engineering documentation | `README*`, `NOTICE*`, `docs/HOWTO/*`, `docs/BUILD/*`, `docs/WORKDIR/reports/*` | Write new documentation for the combined project. Do not present Log1037's DXVK build instructions as applying to the Metal build. |

Reference for the exact names and file groups: [Log1037's engineering changelog](https://github.com/Log1037/CNC-Generals-for-macOS/blob/main/docs/WORKDIR/reports/MACOS_LOCAL_FORK_CHANGELOG.en.md) and [PR #1 commit list](https://github.com/Log1037/CNC-Generals-for-macOS/pull/1).

### Retina implementation map

Log1037's implementation makes a precise distinction:

- SDL window geometry is in logical points.
- drawable/swapchain and engine render-target dimensions are physical pixels.
- backing density is stored separately and must not be applied twice.
- a live resize must update the engine target and rebuild size-dependent resources.
- fullscreen enter/leave must update platform/window state and wait for a settled size before recalculating targets.

For dvcdsys, re-express these rules at the *current* Metal drawable/display boundary. Do not assume its window backend is identical to OKJID's Cocoa layer or Log1037's SDL3 layer. Locate the actual integration points in the checked-out tree with:

```bash
rg -n 'Resize_And_Position_Window|Set_Device_Resolution|drawableSize|contentsScale|backingScaleFactor|windowDidEndLiveResize|NSWindow|SDL_GetWindowSizeInPixels|viewport|render.*scale' \
  Core GeneralsMD extensions launcher cmake scripts
```

The goal is a single size contract: visible window points → backing scale → drawable pixel size → engine render target → UI/mouse mapping. `3456×2234` should be treated as an example display mode, not hard-coded into the port.

## 3. Log1037 `progen` branch delta

The current README says `progen` is additive on top of `main` and includes ProGen-specific source changes, Tomahawk Storm support, a Laser Comanche fix, and the ProGen mod set. That means the merge must distinguish **engine source changes** from **mod packages/overlays**.

The browser session exposed the branch's stated scope but not the complete current `main...progen` file diff. Therefore, I am deliberately not inventing ProGen commit SHAs or claiming unverified source paths. The audit script below emits the exact commit sequence and file list from Git itself.

| ProGen delta type | Treatment |
|---|---|
| `.cpp`, `.h`, `.inl` game-engine changes needed for Tomahawk Storm/Laser Comanche | Port hunks individually to dvcdsys's engine version. These can conflict semantically even when Git merges the text cleanly. |
| `.big`, `.ini`, `.wnd`, maps, other mod payload/overlays | Keep in a separate `mods/ProGen/` or user-installed mod location. Do not mix mod content with retail assets or make the engine binary ProGen-only. Confirm upstream mod permissions before distributing. |
| Log1037-only SDL, DXVK, Vulkan, MoltenVK, Fontconfig/FreeType build glue | Do not import as part of ProGen. Reuse only game-logic changes that are genuinely required by the mod. |
| Files that appear in both `main` and `progen` | They are shared Log1037 base work, not unique ProGen changes. Do not port them a second time. |

## 4. OKJID AVAudioEngine: exact source-file map

OKJID's documented macOS branch is `okji/feat/macos-port`. Its macOS implementation lists the following audio files:

| OKJID file | Purpose | Port guidance |
|---|---|---|
| `Platform/MacOS/Source/Audio/MacOSAudioManager.h` | SAGE `AudioManager` interface adapter | Compare class/API with dvcdsys's audio manager interface; adapt rather than replacing unrelated platform factories. |
| `Platform/MacOS/Source/Audio/MacOSAudioManager.cpp` | Queue, source pool, priority eviction, sound requests, archive/file loading, spatial audio | Best C++ integration starting point; check interface/vtable and audio-event semantics against dvcdsys's baseline. |
| `Platform/MacOS/Source/Audio/AVAudioBridge.h` | C/Objective-C boundary | Keep a narrow bridge so the rest of the engine does not need Objective-C types. |
| `Platform/MacOS/Source/Audio/AVAudioBridge.mm` | `AVAudioEngine`, `AVAudioPlayerNode`, `AVAudioEnvironmentNode` implementation | Compile as Objective-C++; retain queue/thread safety and lifetime handling, then test load/unload/stop paths under game transitions. |
| `Platform/MacOS/Source/Main/MacOSGameEngine.h` and `.mm` | Platform factory and lifecycle integration | **Do not copy wholesale.** Port only audio-manager construction, ownership, shutdown, and any minimal declarations. |
| `Platform/MacOS/CMakeLists.txt` | Build sources, Objective-C++ compilation, framework linkage | Add the audio source files and required Apple frameworks to dvcdsys's existing target. Do not import all of OKJID's target settings. |

Architecture reference: [OKJID's macOS port README](https://github.com/OKJID/GameClient/blob/okji/feat/macos-port/Platform/MacOS/docs/README.md) and [implementation status](https://github.com/OKJID/GameClient/blob/okji/feat/macos-port/Platform/MacOS/docs/IMPLEMENTATION_STATUS.md). The documented backend supports 2D/3D sound, a 64-source pool, listener positioning, WAV from files/`.big` archives, and music streaming. The status page says **ADPCM-encoded WAV is not supported** (PCM WAV is supported); make that a known limitation or add a tested decoder/fallback rather than silently dropping those sounds.

**Do not copy these OKJID files into dvcdsys:**

- `Platform/MacOS/Source/Metal/dx8wrapper_metal.mm`
- `Platform/MacOS/Source/Metal/MetalDevice8.*`
- `Platform/MacOS/Source/Metal/MetalInterface8.*`
- `Platform/MacOS/Source/Metal/MetalTexture8.*`, `MetalSurface8.*`, `MetalVertexBuffer8.*`, `MetalIndexBuffer8.*`, `MacOSShaders.metal`
- `Platform/MacOS/Source/Main/MacOSMain.mm` wholesale
- `Platform/MacOS/Source/FileSystem/MacOSLocalFileSystem.*` wholesale
- `Platform/MacOS/Source/Input/MacOSKeyboard.*` and `MacOSMouse.*` wholesale
- `Platform/MacOS/Source/GeneralsOnlineStubs.cpp`, SwiftUI launcher, and networking changes unless online play becomes a separate project goal

The listed Metal files are another full DX8→Metal adapter. Merging them alongside dvcdsys's adapter would create duplicate implementations, not combine them.

## 5. Ordered integration plan

1. **Freeze and baseline-test dvcdsys.** Create a feature branch, record its commit SHA, build from a clean directory, test vanilla Zero Hour and CWC, and preserve screenshots/logs. Do not start by merging another repository.
2. **Port Retina behavior** from Log1037 commit `762b24f`. Implement point/pixel separation, drawable resize handling, UI/mouse mapping, and resource rebuilds against the actual dvcdsys display and Metal code. Add fullscreen-exit recovery only if reproducible evidence needs it.
3. **Port ProGen engine deltas** after fetching `main` and `progen`. Keep mod packages separate. Test ProGen plus vanilla and CWC so mod fixes do not break shared gameplay.
4. **Port AVAudioEngine** from the four audio files and only the required factory/build changes. Keep video timing on wall-clock time; don't tie sound playback to the render loop. Check source-pool exhaustion, 3D positioning, music transitions, volume/mute, archive loading, and audio shutdown.
5. **Optional:** add the CJK font fixes from `4831537` and selected video/effect fixes from `40051cb`. Avoid the SDL/DXVK-specific portions.
6. **Do not initially port** Log1037's timer commit (`0af28ba`) or settings panel (`a590cd8`). Compare behavior first; dvcdsys already reports uncoupled render/simulation timing and 120-FPS rendering.
7. **Regression matrix:** 1× and scaled Retina modes; resizes; native fullscreen enter/exit; mouse aim/cursor alignment; vanilla campaign/cutscenes; CWC water/particles/shroud/UI; ProGen Tomahawk Storm/Laser Comanche; music and 2D/3D SFX; save/load/replays; app launch with game data on an external volume.

## 6. Reproducible audit commands (run on the Mac)

Run these commands from a new working directory. They fetch only the named branches (no submodules) and write exact SHAs, file lists, and relevant file-history into a timestamped log. Set `WORK` if you want another location.

```bash
#!/bin/bash
set -euo pipefail

WORK="${WORK:-$HOME/Projects/generals-native-merge-audit}"
LOG="${LOG:-$HOME/Desktop/generals-native-merge-audit-$(date +%Y%m%d-%H%M%S).log}"
mkdir -p "$(dirname "$WORK")" "$(dirname "$LOG")"

if [ ! -d "$WORK/.git" ]; then
  git clone --filter=blob:none --no-checkout \
    https://github.com/dvcdsys/GeneralsGameCode-macOS.git "$WORK"
fi

git -C "$WORK" remote get-url log1037 >/dev/null 2>&1 || \
  git -C "$WORK" remote add log1037 https://github.com/Log1037/CNC-Generals-for-macOS.git
git -C "$WORK" remote get-url okjid >/dev/null 2>&1 || \
  git -C "$WORK" remote add okjid https://github.com/OKJID/GameClient.git

git -C "$WORK" fetch --no-tags origin \
  refs/heads/main:refs/remotes/origin/main
git -C "$WORK" fetch --no-tags log1037 \
  refs/heads/main:refs/remotes/log1037/main \
  refs/heads/progen:refs/remotes/log1037/progen
git -C "$WORK" fetch --no-tags okjid \
  refs/heads/okji/feat/macos-port:refs/remotes/okjid/macos-port

{
  echo '=== Timestamp ==='; date
  echo '=== Repository SHAs ==='
  git -C "$WORK" rev-parse origin/main log1037/main log1037/progen okjid/macos-port

  echo; echo '=== Log1037 published eight-commit series ==='
  for c in d19874f 0af28ba 40051cb 762b24f 4831537 a590cd8 cb1df93 85ac2c8 9358726; do
    git -C "$WORK" show --stat --format=fuller "$c" || true
  done

  echo; echo '=== Exact ProGen commits ==='
  git -C "$WORK" log --reverse --format='%H%x09%ad%x09%s' --date=short \
    log1037/main..log1037/progen
  echo; echo '=== Exact ProGen changed paths ==='
  git -C "$WORK" diff --find-renames --name-status \
    log1037/main...log1037/progen
  echo; echo '=== ProGen C/C++/build source delta ==='
  git -C "$WORK" diff --find-renames --name-status \
    log1037/main...log1037/progen -- '*.c' '*.cc' '*.cpp' '*.cxx' '*.h' '*.hh' '*.hpp' '*.inl' '*.m' '*.mm' 'CMakeLists.txt' '*.cmake'
  echo; echo '=== ProGen mod-asset/config delta ==='
  git -C "$WORK" diff --find-renames --name-status \
    log1037/main...log1037/progen -- '*.big' '*.ini' '*.wnd' '*.map' '*.str' '*.xml' '*.jpg' '*.png' '*.tga' '*.dds'

  echo; echo '=== OKJID AVAudioEngine file history ==='
  for p in \
    Platform/MacOS/Source/Audio/MacOSAudioManager.h \
    Platform/MacOS/Source/Audio/MacOSAudioManager.cpp \
    Platform/MacOS/Source/Audio/AVAudioBridge.h \
    Platform/MacOS/Source/Audio/AVAudioBridge.mm \
    Platform/MacOS/Source/Main/MacOSGameEngine.h \
    Platform/MacOS/Source/Main/MacOSGameEngine.mm \
    Platform/MacOS/CMakeLists.txt; do
    echo "--- $p"
    git -C "$WORK" log --follow --date=short --format='%H%x09%ad%x09%s' \
      okjid/macos-port -- "$p"
  done

  echo; echo '=== dvcdsys source touchpoints for Retina, audio, CWC ==='
  git -C "$WORK" grep -n -I -E \
    'Resize_And_Position_Window|Set_Device_Resolution|drawableSize|contentsScale|backingScaleFactor|FramePacer|createAudioManager|AudioManager|AVAudio|Guard.from.Position|CWC' \
    origin/main -- Core Generals GeneralsMD extensions launcher macos_port_tests || true

  echo; echo '=== dvcdsys source history (current base) ==='
  for p in \
    Core/Libraries/Source/WWVegas/WW3D2/dx8wrapper.cpp \
    Core/GameEngine/Include/Common/FramePacer.h \
    Core/GameEngine/Source/Common/FramePacer.cpp \
    Core/GameEngineDevice/Source/StdDevice/Common/StdLocalFileSystem.cpp \
    Core/GameEngineDevice/Source/StdDevice/Common/StdBIGFileSystem.cpp; do
    echo "--- $p"
    git -C "$WORK" log --follow --date=short --format='%h %ad %s' \
      origin/main -- "$p" || true
  done
} 2>&1 | tee "$LOG"

echo "Audit log: $LOG"
```

### How to use the output

- Use the `Exact ProGen changed paths` list to make the ProGen half of the map exhaustive.
- Use the `OKJID AVAudioEngine file history` output to identify its introducing/fix commits; do not guess a commit based on the README.
- The dvcdsys `git grep` output names the exact local implementation sites. Compare those files to Log1037/OKJID sources before writing changes.
- After each feature lands, make a **new commit in the combined repository** with a focused message (for example `fix(macos): make Metal drawable Retina-aware`, `feat(audio): add AVAudioEngine backend`, `fix(progen): support Tomahawk Storm`). Do not recreate upstream commit history by cherry-picking entire foreign branches.

## 7. Important limitation

I could verify the Log1037 eight-commit series and OKJID's audio file layout, but I could not retrieve the live `main...progen` tree diff or the audio files' introducing commit hashes through the current web view. This map therefore gives exact verified commit SHAs where available and includes a local Git audit that obtains the unexposed details from the repositories. It does **not** claim to have performed a source-level compile or merged these changes.
