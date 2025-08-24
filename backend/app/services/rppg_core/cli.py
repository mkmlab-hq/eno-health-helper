import argparse
import cv2

from .pipeline import RPPGPipeline


def main():
	parser = argparse.ArgumentParser(description="rPPG pipeline CLI")
	parser.add_argument('--video', type=str, required=True, help='Path to a video file')
	parser.add_argument('--algo', type=str, default='chrom', choices=['chrom', 'pca', 'ica'])
	parser.add_argument('--fps', type=float, default=30.0, help='Fallback FPS if video metadata is missing')
	args = parser.parse_args()

	cap = cv2.VideoCapture(args.video)
	if not cap.isOpened():
		raise SystemExit(f"Failed to open video: {args.video}")
	fps = cap.get(cv2.CAP_PROP_FPS) or args.fps
	fps = fps if fps and fps > 0 else args.fps
	frames = []
	while True:
		ok, frame = cap.read()
		if not ok:
			break
		frames.append(frame)
	cap.release()

	pipe = RPPGPipeline(algorithm=args.algo, sample_rate_hz=fps)
	res = pipe.process_video_frames(frames)
	print(f"BPM: {res.bpm:.2f}")
	print(f"Meta: {res.metadata}")


if __name__ == '__main__':
	main()