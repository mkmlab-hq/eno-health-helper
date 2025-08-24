from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np


@dataclass
class SOTAResult:
	bpm: float
	metadata: Dict[str, Any]


class BaseSOTAModel(ABC):
	"""Abstract interface for SOTA rPPG models (e.g., DeepPhys, PhysNet, RhythmNet, POS)."""

	@abstractmethod
	def predict_bpm(self, frames_bgr: List[np.ndarray], fps: float) -> SOTAResult:
		"""Estimate BPM from raw frames."""
		raise NotImplementedError


class DummyPOSModel(BaseSOTAModel):
	"""Lightweight placeholder using CHROM-like projection to mimic POS behavior."""
	def __init__(self):
		pass

	def predict_bpm(self, frames_bgr: List[np.ndarray], fps: float) -> SOTAResult:
		# Minimal placeholder: compute mean RGB traces and FFT-based BPM
		from ..face.mediapipe_face_roi import FaceMeshROIExtractor
		from ..signal.processing import compute_bpm_from_signal
		from ..algorithms.chrom import extract_rppg_chrom

		extractor = FaceMeshROIExtractor()
		rgb_traces = extractor.extract_roi_mean_rgb(frames_bgr)
		signal = extract_rppg_chrom(rgb_traces, fps)
		bpm, meta = compute_bpm_from_signal(signal, fps)
		return SOTAResult(bpm=bpm, metadata={"backend": "dummy_pos", **meta})