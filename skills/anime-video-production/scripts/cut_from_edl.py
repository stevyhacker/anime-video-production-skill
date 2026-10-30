#!/usr/bin/env python3
"""Cut one CFR video by frame ranges, with optional symmetric audio crossfades."""
import argparse
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def ffprobe(path):
    command = ['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(path)]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def seconds(frames, rate):
    return frames * rate.denominator / rate.numerator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--edl', type=Path, required=True, help='JSON object with segments: start_frame inclusive, end_frame exclusive')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--audio-crossfade', type=float, default=0.25, help='Seconds; zero makes hard audio cuts')
    args = parser.parse_args()
    if not args.input.is_file() or not args.edl.is_file():
        raise ValueError('Input video and EDL must exist')
    if args.output.resolve() == args.input.resolve() or args.output.exists():
        raise ValueError('Output already exists or is the source; choose a new path')
    if not math.isfinite(args.audio_crossfade) or args.audio_crossfade < 0 or args.audio_crossfade > 2:
        raise ValueError('Audio crossfade must be between 0 and 2 seconds')
    info = ffprobe(args.input)
    videos = [s for s in info['streams'] if s['codec_type'] == 'video']
    audios = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if len(videos) != 1 or not audios:
        raise ValueError('Expected one video stream and at least one audio stream')
    vid = videos[0]
    rate = Fraction(vid.get('avg_frame_rate', '0/1'))
    nominal = Fraction(vid.get('r_frame_rate', '0/1'))
    if rate <= 0 or rate != nominal:
        raise ValueError('Expected a stable frame rate; inspect or conform this source first')
    frames = int(vid.get('nb_read_frames') or vid.get('nb_frames') or 0)
    if frames <= 0:
        raise ValueError('Could not determine the video frame count')
    source_duration = seconds(frames, rate)
    declared_duration = float(vid.get('duration') or info['format'].get('duration') or source_duration)
    if abs(declared_duration - source_duration) > max(0.1, 2 / float(rate)):
        raise ValueError('Frame count and duration disagree; source may have variable timing')
    data = json.loads(args.edl.read_text())
    ranges = data.get('segments') if isinstance(data, dict) else None
    if not isinstance(ranges, list) or not 1 <= len(ranges) <= 30:
        raise ValueError('EDL must contain 1–30 segments')
    segments = []
    for segment in ranges:
        if not isinstance(segment, dict):
            raise ValueError('Each segment must be an object')
        start, end = segment.get('start_frame'), segment.get('end_frame')
        if type(start) is not int or type(end) is not int or not (0 <= start < end <= frames):
            raise ValueError(f'Invalid frame range: {start!r}–{end!r}; source has {frames} frames')
        segments.append((start, end))
    count = len(segments)
    half = args.audio_crossfade / 2
    if count > 1 and args.audio_crossfade:
        for i, (start, end) in enumerate(segments):
            a, b = seconds(start, rate), seconds(end, rate)
            if (i and a < half) or (i < count - 1 and b + half > source_duration):
                raise ValueError('Insufficient source handles for this crossfade; shorten it or adjust the EDL')
            extra = (half if i else 0) + (half if i < count - 1 else 0)
            if b - a + extra < args.audio_crossfade:
                raise ValueError('A segment is too short for the requested crossfade')
    filters = []
    if count == 1:
        filters.append('[0:v]null[v0]')
        filters.append('[0:a:0]anull[a0]')
    else:
        filters.append('[0:v]split=' + str(count) + ''.join(f'[v{i}]' for i in range(count)))
        filters.append('[0:a:0]asplit=' + str(count) + ''.join(f'[a{i}]' for i in range(count)))
    for i, (start, end) in enumerate(segments):
        filters.append(f'[v{i}]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS[vt{i}]')
        start_sec = seconds(start, rate) - (half if i else 0)
        end_sec = seconds(end, rate) + (half if i < count - 1 else 0)
        filters.append(f'[a{i}]atrim=start={start_sec:.9f}:end={end_sec:.9f},asetpts=PTS-STARTPTS[at{i}]')
    if count == 1:
        filters.append('[vt0]null[vout]')
        filters.append('[at0]anull[aout]')
    else:
        filters.append(''.join(f'[vt{i}]' for i in range(count)) + f'concat=n={count}:v=1:a=0[vout]')
        if args.audio_crossfade:
            previous = 'at0'
            for i in range(1, count):
                out = 'aout' if i == count - 1 else f'ax{i}'
                filters.append(f'[{previous}][at{i}]acrossfade=d={args.audio_crossfade:.9f}:c1=tri:c2=tri[{out}]')
                previous = out
        else:
            filters.append(''.join(f'[at{i}]' for i in range(count)) + f'concat=n={count}:v=0:a=1[aout]')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-n', '-i', str(args.input), '-filter_complex', ';'.join(filters),
           '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(args.output)]
    subprocess.run(cmd, check=True)
    result = ffprobe(args.output)
    out_video = next(s for s in result['streams'] if s['codec_type'] == 'video')
    out_audio = next((s for s in result['streams'] if s['codec_type'] == 'audio'), None)
    expected_frames = sum(end - start for start, end in segments)
    actual_frames = int(out_video.get('nb_read_frames') or out_video.get('nb_frames') or 0)
    expected_duration = seconds(expected_frames, rate)
    actual_duration = float(result['format']['duration'])
    audio_duration = float(out_audio.get('duration') or 0) if out_audio else 0
    output_rate = Fraction(out_video.get('avg_frame_rate', '0/1'))
    if (not out_audio or actual_frames != expected_frames or output_rate != rate
            or abs(actual_duration - expected_duration) > max(0.05, 1 / float(rate))
            or abs(audio_duration - expected_duration) > max(0.08, 2 / float(rate))):
        raise RuntimeError(f'Output validation failed: {actual_frames}/{expected_frames} frames, {actual_duration}/{expected_duration} seconds')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(args.output), '-f', 'null', '-'], check=True)
    print(json.dumps({'output': str(args.output), 'frames': actual_frames, 'fps': str(rate),
                      'expected_seconds': expected_duration, 'container_seconds': actual_duration,
                      'audio_seconds': audio_duration,
                      'audio_crossfade_seconds': args.audio_crossfade, 'full_decode_passed': True}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
