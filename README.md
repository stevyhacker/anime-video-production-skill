# Anime Video Production

An Agent Skill for turning an anime-video brief into a finished, reviewable film: character references, shot direction, generation, editing, sound, upscaling and validation.

It grew out of an experiment making a short *Wheel of Time* fan video with Pika H3 Flex, Google Colab, ComfyUI, Real-ESRGAN and FFmpeg. The skill is not tied to that story or those tools: it respects the generator, reference material, format and budget you choose.

## Install

```bash
npx -y skills add stevyhacker/anime-video-production-skill \
  --skill anime-video-production \
  --global
```

The command lets you choose supported agents interactively. Omit `--global` to install for the current project. You can also copy `skills/anime-video-production` to the skills directory used by your agent.

Then ask your agent:

> Use $anime-video-production to make a 30-second anime scene from my brief. Keep the character design consistent, edit the shots together, and check the final video and audio.

## What it covers

- Break a brief into readable shots with clear action, dialogue and camera direction.
- Use visual references for character continuity and keep their provenance.
- Run Pika H3 Flex on a compatible Colab/ComfyUI setup, with budget checks, recorded model details and runtime cleanup, when that is the chosen workflow.
- Keep source clips and edit decisions, compare an AI upscale to a conventional resize, and improve transitions without masking dialogue.
- Check the delivered video and distinguish sampled frames, automated speech checks and actual playback review.

The optional `cut_from_edl.py` helper makes frame-aligned cuts in a single constant-frame-rate source, with audio crossfades. It requires Python 3, FFmpeg with libx264, and ffprobe. See [the finishing reference](skills/anime-video-production/references/finishing.md) for its EDL format and limitations.

## Validate

```bash
python3 -m unittest discover -s tests -v
```

This exercises the helper on generated video and audio; it does not validate the subjective quality of a creative edit or a remote generation service.

## Related

[The making-of post and video demo](https://stevan.bogosavljevic.me/blog/posts/making-dumais-wells-anime/) · [Pika H3 Flex](https://github.com/Pika-Labs/Pika-H3-Flex) · [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)

This is an independent community skill. Using it does not include model weights, GPU time, third-party content or rights to reference material.

## License

MIT for the skill and helper code. Third-party models, media and services have their own terms.
