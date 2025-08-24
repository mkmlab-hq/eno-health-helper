from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, List, Dict, Any
import numpy as np

from ..face.mediapipe_face_roi import FaceMeshROIExtractor
from ..algorithms.chrom import extract_rppg_chrom
from ..algorithms.pca_ica import extract_rppg_pca, extract_rppg_ica
from ..signal.processing import compute_bpm_from_signal


AlgorithmName = Literal['chrom', 'pca', 'ica']


@dataclass
class RPPGResult:
	bpm: float
	metadata: Dict[str, Any]


class RPPGPipeline:
	def __init__(self, algorithm: AlgorithmName = 'chrom', sample_rate_hz: float = 30.0, roi_extractor: Optional[FaceMeshROIExtractor] = None):
		self.algorithm: AlgorithmName = algorithm
		self.sample_rate_hz = float(sample_rate_hz)
		self.roi_extractor = roi_extractor or FaceMeshROIExtractor()

	def _select_algorithm(self, rgb_traces: np.ndarray) -> np.ndarray:
		if self.algorithm == 'chrom':
			return extract_rppg_chrom(rgb_traces, self.sample_rate_hz)
		elif self.algorithm == 'pca':
			return extract_rppg_pca(rgb_traces, self.sample_rate_hz)
		elif self.algorithm == 'ica':
			return extract_rppg_ica(rgb_traces, self.sample_rate_hz)
		else:
			raise ValueError(f"Unsupported algorithm: {self.algorithm}")

	def process_video_frames(self, frames_bgr: List[np.ndarray]) -> RPPGResult:
		rgb_traces = self.roi_extractor.extract_roi_mean_rgb(frames_bgr)  # (3, N)
		signal = self._select_algorithm(rgb_traces)
		bpm, meta = compute_bpm_from_signal(signal, self.sample_rate_hz)
		return RPPGResult(bpm=bpm, metadata=meta)