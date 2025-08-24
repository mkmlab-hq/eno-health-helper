import numpy as np
from ..signal.processing import bandpass_filter_signal, detrend_signal, normalize_signal


def _ensure_traces_shape(rgb_traces: np.ndarray) -> np.ndarray:
	if rgb_traces.ndim != 2:
		raise ValueError("rgb_traces must be 2D")
	# Accept (3, N) or (N, 3); return (N, 3)
	if rgb_traces.shape[0] == 3:
		return rgb_traces.T.astype(np.float64)
	elif rgb_traces.shape[1] == 3:
		return rgb_traces.astype(np.float64)
	else:
		raise ValueError("rgb_traces must have 3 channels")


def extract_rppg_chrom(rgb_traces: np.ndarray, sample_rate_hz: float) -> np.ndarray:
	"""
	Extract a 1D rPPG signal using the CHROM method (de Haan & Jeanne, 2013).
	Input rgb_traces is either shape (3, N) or (N, 3) in RGB order.
	Returns a 1D filtered rPPG signal aligned to input length.
	"""
	traces = _ensure_traces_shape(rgb_traces)
	# Normalize each channel by its mean to reduce illumination variations
	means = np.mean(traces, axis=0)  # (3,)
	means[means == 0] = 1.0
	norm = traces / means
	# Detrend per channel
	for c in range(3):
		norm[:, c] = detrend_signal(norm[:, c])
	# CHROM projections
	R = norm[:, 0]
	G = norm[:, 1]
	B = norm[:, 2]
	X = 3.0 * R - 2.0 * G
	Y = 1.5 * R + 1.0 * G - 1.5 * B
	std_x = np.std(X) + 1e-12
	std_y = np.std(Y) + 1e-12
	alpha = std_x / std_y
	signal = X - alpha * Y
	signal = normalize_signal(bandpass_filter_signal(signal, sample_rate_hz))
	return signal