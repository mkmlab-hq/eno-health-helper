import numpy as np


def detrend_signal(signal: np.ndarray) -> np.ndarray:
	if signal.ndim != 1:
		raise ValueError("detrend_signal expects a 1D signal")
	x = np.arange(signal.size, dtype=np.float64)
	y = signal.astype(np.float64)
	# Fit a line y = ax + b and subtract it
	a, b = np.polyfit(x, y, 1)
	return y - (a * x + b)


def _hann_window(n: int) -> np.ndarray:
	return 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(n) / max(n - 1, 1))


def _fft_bandpass(signal: np.ndarray, sample_rate_hz: float, low_hz: float, high_hz: float) -> np.ndarray:
	# Zero out frequencies outside [low_hz, high_hz] using FFT
	n = signal.size
	spec = np.fft.rfft(signal)
	freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)
	mask = (freqs >= low_hz) & (freqs <= high_hz)
	spec_filtered = spec * mask
	filtered = np.fft.irfft(spec_filtered, n=n)
	return filtered.real


def bandpass_filter_signal(signal: np.ndarray, sample_rate_hz: float, low_hz: float = 0.7, high_hz: float = 4.0, order: int = 3) -> np.ndarray:
	if signal.ndim != 1:
		raise ValueError("bandpass_filter_signal expects a 1D signal")
	if sample_rate_hz <= 0:
		raise ValueError("sample_rate_hz must be positive")
	# Use FFT-based simple bandpass to avoid SciPy dependency
	return _fft_bandpass(signal.astype(np.float64), sample_rate_hz, low_hz, high_hz)


def normalize_signal(signal: np.ndarray) -> np.ndarray:
	if signal.ndim != 1:
		raise ValueError("normalize_signal expects a 1D signal")
	mean = np.mean(signal)
	std = np.std(signal)
	return (signal - mean) / (std + 1e-12)


def compute_bpm_from_signal(signal: np.ndarray, sample_rate_hz: float, min_bpm: float = 40.0, max_bpm: float = 180.0) -> tuple[float, dict]:
	if signal.ndim != 1:
		raise ValueError("compute_bpm_from_signal expects a 1D signal")
	if len(signal) < 64:
		raise ValueError("Signal too short for BPM estimation")
	clean = normalize_signal(detrend_signal(signal))
	n = len(clean)
	win = _hann_window(n)
	spec = np.fft.rfft(clean * win)
	freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)
	power = np.abs(spec) ** 2
	min_hz = min_bpm / 60.0
	max_hz = max_bpm / 60.0
	band_mask = (freqs >= min_hz) & (freqs <= max_hz)
	if not np.any(band_mask):
		raise ValueError("No frequencies in specified BPM range")
	peak_idx = np.argmax(power[band_mask])
	band_freqs = freqs[band_mask]
	peak_hz = band_freqs[peak_idx]
	bpm = float(peak_hz * 60.0)
	# Confidence as peak prominence ratio
	band_power = power[band_mask]
	peak_power = band_power[peak_idx]
	residual = np.mean(np.sort(band_power)[::-1][5:]) if band_power.size > 5 else np.mean(band_power)
	confidence = float(peak_power / (residual + 1e-12))
	return bpm, {"peak_hz": float(peak_hz), "confidence": confidence}