# Pika H3 Flex on Colab / ComfyUI

Use this reference only when the user chooses Pika H3 Flex or a compatible local ComfyUI/Colab workflow. Verify current upstream documentation, hardware requirements, Colab balance and runtime pricing before launching; old release information is a measured example, not a service guarantee.

## Direction and prompts

- Choose text-to-video/FL2VA for an unanchored shot, first/last-frame conditioning for explicit endpoint geometry, and Ref2VA for character or multimodal reference-guided scenes. Reference conditioning is not a seamless-continuation guarantee.
- For Ref2VA, [Pika's prompt guide](https://github.com/Pika-Labs/Pika-H3-Flex/blob/main/docs/prompt-guidance.md) recommends `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music`. Specify what each image supplies and exclude unwanted reference layout/background. Write shots in playback order; describe deliberate action, camera and final state. Use stable speaker IDs and dialogue tags like `<d>[English] ...</d>` as supported by the current guide. Place voice characteristics outside the tags.
- Check the source story and user-provided canon when relevant. Prefer a few staged actions and concise lines over too many simultaneous beats. Include silence or off-screen dialogue intentionally, not by assuming the model will interpret it correctly. Verify generated speech and motion separately from the prompt.

## Operator checklist

- Inspect `colab --help`, `colab skill`, `colab usage`, and `colab sessions`; CLI syntax and GPU entitlement can change. A session is billable until stopped. Ask for spending authority when it is not already given. Never automatically buy credits.
- Before allocation, check whether the selected GPU can plausibly fit the requested canvas, clip length, model weights and reference encoding. Check the runtime disk/RAM after allocation. A lower resolution or alternate GPU is a creative and performance trade-off: preserve the user's resolution requirement, describe material compromises and avoid unsupported promises.
- Prepare prompts, reference files, exact requested graph and download/cleanup steps before starting a billable runtime. Keep one named session, avoid duplicate submissions after a timeout (check queue/history first), monitor status and a conservative elapsed/budget limit, download and validate finished clips, and stop that session in cleanup. Recover a timeout by inspecting existing remote state before resubmitting. Do not stop unrelated sessions.
- Pin or record the actual ComfyUI commit, model repository/revision, model file hashes, LoRA, package versions, scheduler/sigmas, seed, geometry and GPU. Verify downloaded files against trusted provider metadata when available. For multiple clips reuse the loaded server when appropriate. User data and credentials do not belong in shared prompts or logs.

## Recorded working configuration—not a universal default

A 2026-10-30 test used ComfyUI commit `b5a432157de6b8884f81104cd02926adf4d597e4` and `Comfy-Org/MiniMax-H3` revision `912b6e38b2092ec4d2e86d24183e0d59ea059d48`: the compressed Ref2VA base, Qwen3-VL 32B NVFP4 text encoder, video/audio VAEs and the Pika Ref2VA LoRA; six-step LCM with sigmas `1.0, 0.972973, 0.923077, 0.8, 0.571429, 0.333333, 0.0`, LoRA strength 1.0, 24 fps. Fifteen seconds requested 362 model frames and was trimmed to 360 frames. The five files totaled about 42 GB. Two 1344 × 768 / 15 s reference-guided clips on an A100 40 GB took roughly 11 minutes each for the logged generation request; setup and download were separate. A G4 96 GB was also used for an earlier text-only sample. Rates, availability, memory requirements and speed are not guaranteed; never extrapolate a quoted Pika benchmark to total runtime.

The [official Pika repository](https://github.com/Pika-Labs/Pika-H3-Flex), [ComfyUI Ref2VA template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_pika_h3_flex_ref2va.json) and [text-to-video template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_pika_h3_flex_t2v.json) are starting points. Resolve dependencies and sampling against the installed versions; generic Euler sampling is not automatically equivalent to the published adapter schedule.
