# Anime video finishing and validation

## Editing and sound

Keep a reversible source and identify edits against the source time base. Choose cuts based on action and story: remove repeated poses, preserve cause before effect, keep important spoken lines intact, and check continuity of framing, lighting and sound. A contact sheet helps locate candidate cuts; it does not establish how the edit feels in motion. When possible inspect the transitions in playback and listen to them.

For a single assembled source with constant frame rate and an audio track, the helper accepts an EDL like:

```json
{"segments":[{"start_frame":0,"end_frame":354},{"start_frame":456,"end_frame":666},{"start_frame":948,"end_frame":1080}]}
```

End frames are exclusive; use the actual media frame rate. Invoke:

```bash
python "<skill-directory>/scripts/cut_from_edl.py" --input source.mp4 --edl edit.json --output edit.mp4 --audio-crossfade 0.25
```

The helper requires sufficient audio handles around each cut, makes hard picture cuts, overlaps audio symmetrically, re-encodes H.264/AAC, never overwrites an existing destination, and verifies output timing, frames and decode. It does not choose cuts, protect dialogue automatically, establish constant frame rate for every possible input, or replace a listening/playback review. For multiple sources, sound design, fades to black, J/L cuts or more complex timelines, use the appropriate editor or a custom graph.

When music, speech and effects are baked into one generated soundtrack, treat all as one track unless usable stems are actually available. A speech recognizer can check likely words but cannot verify vocal quality or lip sync. Make purposeful SFX cues subordinate to dialogue, avoid covering line endings, allow enough room for tails, and measure output loudness/true peak. The previous project used a short whoosh and low impact near the attack, a quieter bridge into a reaction, and a small gain lift on the last line; those positions and levels are examples, not a universal recipe. If the soundtrack cannot be directly heard, state this and do not claim subjective sound quality.

## 1080p comparison and upscale

A measured option for anime is [Real-ESRGAN AnimeVideo-v3](https://github.com/xinntao/Real-ESRGAN/blob/master/docs/anime_video_model.md). First compare a short character/action sample to a conventional Lanczos resize, using identical source frames and aspect-ratio policy. Inspect faces, fine lines, noise and a sequence of consecutive frames. Neural models may smooth texture, alter detail, produce seams or flicker. Do not process the full video merely because the output dimensions increase; proceed when the test looks preferable and the user has authorized that scope.

For an approved 2× frame workflow, extract all source frames in order, run the chosen model in a separate directory, assert that the expected frame sequence is complete, resize/pad or crop to the requested output while explicitly preserving aspect ratio, and remux the original audio without re-encoding where possible. Preserve source fps and exact duration unless instructed otherwise. On macOS, GPU access or a compatible Vulkan/Metal backend may be required; check it with a single-frame test before launching a batch. The documented 1344 × 768 project used 1890 × 1080 picture plus 15-pixel side bars for a 1920 × 1080 canvas; this padding is specific to that 7:4 source, not a default for other videos.

## Validation

- Use `ffprobe` to compare dimensions, frame rate, duration, frame count and audio properties; run a complete `ffmpeg ... -f null -` decode.
- Verify audio is preserved after a visual-only upscale, preferably comparing decoded audio hashes. If only audio is edited, compare encoded picture stream hashes when stream-copy is used.
- Review actual output around every edit and at representative early/middle/late shots. Consecutive sampled frames are a partial flicker check, not proof of full temporal stability. An automated transcript is not a substitute for listening.
- Save relevant source clips, prompts, references, manifests, EDL, mix graph, outputs and validation evidence. Remove only intermediates created for the task after successful validation and when safe; preserve the user's assets.
