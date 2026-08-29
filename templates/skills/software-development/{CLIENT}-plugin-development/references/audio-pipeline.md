<!-- GENERICIZED: 4×{CLIENT} | source: skills/software-development/{CLIENT} -->
# {CLIENT} audio & asset pipeline (verified 2026-08, {CLIENT})

## Track manifest is the timing contract
- `tracks.json` (schema `{CLIENT}`): per file — `durationMs`, `declaredS`,
  `bpm`, `beatMs`, `beatsTotal`, `vet`, `tempoVerified`, `ship`, `sha1`,
  `attribution`, `source`.
- The judge's beat-grid derives from the MANIFEST, never the decoded audio.
  Determinism rule: same track + same BPM = same note map every run.

## Exact duration: ffmpeg PCM sample count (not container read)
```bash
ffmpeg -v error -i track.ogg -f s16le -ac 2 -ar 44100 - 2>/dev/null | wc -c
# stereo interleaved: frames = bytes / 4 (2ch × 2 bytes); seconds = frames / 44100
```
- Container duration and decode differ by <1ms for Vorbis — measure BOTH and
  reconcile; the browser's `decodeAudioData` cannot run headless (no audio
  device), so ffmpeg is the deterministic reference.
- STEREO GOTCHA: counting bytes gives 2× the sample count unless you divide by
  4 (2 channels × 2 bytes). An independent verifier recounting "exactly 2×"
  is the interleaving, not a mismatch.

## Tempo: librosa beat track + cross-check
```python
import librosa
y, sr = librosa.load(f, sr=44100, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
```
- Onset autocorrelation can lock onto HALF-TIME for chiptune (energy method
  gave 60.1 where interval method gave 116–118 vs librosa 120.2). Cross-check
  with a second method (onset-interval histogram) before declaring BPM.
- Design BPM is a game-assignment within {CLIENT}'s 20–120 range; mark
  `tempoVerified: false` until a human ear confirms the music matches the grid.

## CC0 / CC-BY-SA provenance rules (from the OpMon-Data audit)
- License evidence is the ITEM PAGE (individual OGA item), not the collection
  page. Record attribution as `author — license, source URL`.
- CC-BY-SA assets can ship beside MIT code ONLY as a distinct asset layer:
  own directory, own LICENSE, per-file SHA-1 attribution ledger, and a
  build-time assertion that paid/original assets never reference that namespace.
- Attribution is UNFILLABLE when no composer credit survived repo history
  (squashed git history, empty metadata tags) → under "inspect at pull,
  exclude on doubt", EXCLUDE. Flip `vet: "exclude-provenance"`, `ship: false`.
- `.gitignore`-FIRST for provenance-dead files: excluded `.ogg`s must never
  enter git history (a file that never exists in history can't be resurrected
  by force-push). Do this before the first push, not as a manual sweep.
- Public repo license boundary: root `LICENSE` (MIT, engine) + island
  `assets/ccbysa/LICENSE` (CC-BY-SA) + the ledger visible to any visitor.

## Dev/test audio lane
- Keep test-only audio (unvetted compositions) in a README-flagged dir, never
  in the island's ship path; the manifest `ship: false` is the structural guard.
