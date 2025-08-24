import numpy as np
from ..pipeline import RPPGPipeline


def generate_synthetic_frames(num_frames: int, fps: float, bpm: float, frame_size=(64, 64)):
	"""Generate gray frames whose RGB mean follows a sinusoid at the given BPM."""
	frames = []
	omega = (bpm / 60.0) * 2 * np.pi
	for t in range(num_frames):
		mean = 0.5 + 0.4 * np.sin(omega * (t / fps))
		val = int(np.clip(mean, 0, 1) * 255)
		frame = np.full((*frame_size, 3), val, dtype=np.uint8)
		frames.append(frame)
	return frames


def test_pipeline_chrom_synthetic():
	fps = 30.0
	target_bpm = 72.0
	frames = generate_synthetic_frames(600, fps, target_bpm)
	pipe = RPPGPipeline(algorithm='chrom', sample_rate_hz=fps)
	res = pipe.process_video_frames(frames)
	assert 60.0 <= res.bpm <= 90.0