import numpy as np
from typing import Literal
try:
	from sklearn.decomposition import PCA, FastICA  # type: ignore
except Exception:  # pragma: no cover
	PCA = None  # type: ignore
	FastICA = None  # type: ignore
from ..signal.processing import bandpass_filter_signal


def _ensure_traces_shape(rgb_traces: np.ndarray) -> np.ndarray:
	if rgb_traces.ndim != 2:
		raise ValueError("rgb_traces must be 2D")
	if rgb_traces.shape[0] == 3:
		return rgb_traces.T.astype(np.float64)
	elif rgb_traces.shape[1] == 3:
		return rgb_traces.astype(np.float64)
	else:
		raise ValueError("rgb_traces must have 3 channels")


def _select_component_by_band_power(components: np.ndarray, sample_rate_hz: float, min_bpm: float = 40.0, max_bpm: float = 180.0) -> np.ndarray:
	# components: (N, K)
	N, K = components.shape
	best_idx = 0
	best_power = -np.inf
	min_hz = min_bpm / 60.0
	max_hz = max_bpm / 60.0
	freqs = np.fft.rfftfreq(N, d=1.0 / sample_rate_hz)
	band_mask = (freqs >= min_hz) & (freqs <= max_hz)
	for k in range(K):
		spec = np.fft.rfft(components[:, k])
		power = np.abs(spec) ** 2
		band_power = np.sum(power[band_mask])
		if band_power > best_power:
			best_power = band_power
			best_idx = k
	return components[:, best_idx]


def extract_rppg_pca(rgb_traces: np.ndarray, sample_rate_hz: float, strategy: Literal['first', 'max_power'] = 'max_power') -> np.ndarray:
	if PCA is None:
		raise ImportError("scikit-learn is required for PCA-based rPPG. Please install scikit-learn.")
	traces = _ensure_traces_shape(rgb_traces)
	pca = PCA(n_components=3, whiten=True, random_state=42)
	pcs = pca.fit_transform(traces)  # (N, 3)
	if strategy == 'first':
		comp = pcs[:, 0]
	else:
		comp = _select_component_by_band_power(pcs, sample_rate_hz)
	return bandpass_filter_signal(comp, sample_rate_hz)


def extract_rppg_ica(rgb_traces: np.ndarray, sample_rate_hz: float) -> np.ndarray:
	if PCA is None or FastICA is None:
		raise ImportError("scikit-learn is required for ICA-based rPPG. Please install scikit-learn.")
	traces = _ensure_traces_shape(rgb_traces)
	pca = PCA(n_components=3, whiten=True, random_state=42)
	pcs = pca.fit_transform(traces)
	ica = FastICA(n_components=3, random_state=42, whiten=False, algorithm='parallel')
	ics = ica.fit_transform(pcs)  # (N, 3)
	comp = _select_component_by_band_power(ics, sample_rate_hz)
	return bandpass_filter_signal(comp, sample_rate_hz)