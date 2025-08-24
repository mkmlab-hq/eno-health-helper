from __future__ import annotations
import numpy as np
try:
	import cv2  # type: ignore
except Exception:  # pragma: no cover
	cv2 = None  # type: ignore
try:
	import mediapipe as mp  # type: ignore
except Exception:  # pragma: no cover - allow runtime without mediapipe
	mp = None  # type: ignore
else:
	mp = mp


class FaceMeshROIExtractor:
	"""
	Extracts mean RGB time series from a face region using MediaPipe Face Mesh.
	Simplified approach: use the convex hull of detected landmarks as ROI.
	Falls back to a centered crop if no face is detected or mediapipe is unavailable.
	"""
	def __init__(self, max_num_faces: int = 1, refine_landmarks: bool = True, detection_confidence: float = 0.5, tracking_confidence: float = 0.5, roi_scale: float = 0.7):
		self.roi_scale = float(roi_scale)
		self.enabled = (mp is not None) and (cv2 is not None)
		if self.enabled:
			self._mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
				static_image_mode=False,
				max_num_faces=max_num_faces,
				refine_landmarks=refine_landmarks,
				min_detection_confidence=detection_confidence,
				min_tracking_confidence=tracking_confidence,
			)
		else:
			self._mp_face_mesh = None

	def __del__(self):
		try:
			if self._mp_face_mesh is not None:
				self._mp_face_mesh.close()
		except Exception:
			pass

	def _fallback_center_crop_mean(self, frame_bgr: np.ndarray) -> np.ndarray:
		h, w = frame_bgr.shape[:2]
		crop_w = int(w * self.roi_scale)
		crop_h = int(h * self.roi_scale)
		x0 = (w - crop_w) // 2
		y0 = (h - crop_h) // 2
		crop = frame_bgr[y0:y0+crop_h, x0:x0+crop_w]
		mean_bgr = crop.reshape(-1, 3).mean(axis=0)
		# Convert BGR to RGB order
		return mean_bgr[::-1]

	def extract_roi_mean_rgb(self, frames_bgr: list[np.ndarray]) -> np.ndarray:
		if not frames_bgr:
			raise ValueError("frames_bgr must be non-empty")
		means = []
		for frame_bgr in frames_bgr:
			if self.enabled and self._mp_face_mesh is not None:
				frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
				res = self._mp_face_mesh.process(frame_rgb)
				if res.multi_face_landmarks:
					landmarks = res.multi_face_landmarks[0]
					pts = []
					h, w = frame_bgr.shape[:2]
					for lm in landmarks.landmark:
						x = int(lm.x * w)
						y = int(lm.y * h)
						pts.append([x, y])
					pts = np.array(pts, dtype=np.int32)
					if pts.shape[0] >= 3:
						mask = np.zeros((h, w), dtype=np.uint8)
						from scipy.ndimage import binary_erosion
						# Build convex hull mask via OpenCV if available, else fallback to bbox
						if cv2 is not None:
							cv2.fillConvexPoly(mask, cv2.convexHull(pts), 255)
							kernel = np.ones((7, 7), np.uint8)
							mask = cv2.erode(mask, kernel, iterations=1)
						else:
							xmin, ymin = pts.min(axis=0)
							xmax, ymax = pts.max(axis=0)
							mask[ymin:ymax, xmin:xmax] = 255
						masked = frame_bgr * (mask[..., None] > 0)
						valid = mask > 0
						if np.any(valid):
							mean_bgr = masked[valid].reshape(-1, 3).mean(axis=0)
							means.append(mean_bgr[::-1])
							continue
			# Fallback
			means.append(self._fallback_center_crop_mean(frame_bgr))
		arr = np.asarray(means, dtype=np.float64)
		return arr.T