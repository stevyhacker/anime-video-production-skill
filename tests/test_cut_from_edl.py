import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/anime-video-production/scripts/cut_from_edl.py'


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg and ffprobe required')
class CutFromEdlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / 'input.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                        'testsrc2=size=320x180:rate=24:duration=3', '-f', 'lavfi', '-i',
                        'sine=frequency=440:sample_rate=32000:duration=3', '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(self.source)], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cut(self, segments, fade=0.25, output='result.mp4'):
        edl = self.root / 'edl.json'
        edl.write_text(json.dumps({'segments': segments}))
        target = self.root / output
        cmd = [sys.executable, str(SCRIPT), '--input', str(self.source), '--edl', str(edl),
               '--output', str(target), '--audio-crossfade', str(fade)]
        return subprocess.run(cmd, capture_output=True, text=True), target

    def test_crossfade_and_hard_cut_have_exact_length(self):
        segments = [{'start_frame': 0, 'end_frame': 24}, {'start_frame': 48, 'end_frame': 72}]
        for fade in (0.25, 0):
            with self.subTest(fade=fade):
                result, target = self.run_cut(segments, fade, f'result-{fade}.mp4')
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['frames'], 48)
                self.assertAlmostEqual(report['container_seconds'], 2.0, places=2)
                self.assertAlmostEqual(report['audio_seconds'], 2.0, places=2)
                self.assertTrue(report['full_decode_passed'])
                self.assertTrue(target.is_file())

    def test_single_segment(self):
        result, _ = self.run_cut([{'start_frame': 12, 'end_frame': 36}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['frames'], 24)

    def test_rejects_missing_handles_before_writing(self):
        segments = [{'start_frame': 0, 'end_frame': 20}, {'start_frame': 1, 'end_frame': 24}]
        result, target = self.run_cut(segments)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Insufficient source handles', result.stderr)
        self.assertFalse(target.exists())

    def test_never_overwrites_output(self):
        segments = [{'start_frame': 0, 'end_frame': 24}]
        target = self.root / 'existing.mp4'
        target.write_bytes(b'keep me')
        result, _ = self.run_cut(segments, output='existing.mp4')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_bytes(), b'keep me')


if __name__ == '__main__':
    unittest.main()
