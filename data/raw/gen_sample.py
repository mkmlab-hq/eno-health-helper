import datetime as dt
import os

import numpy as np
import pandas as pd

np.random.seed(42)
start = dt.datetime(2024, 1, 1)
ts = [start + dt.timedelta(hours=i) for i in range(500)]
feat_a = np.random.normal(0, 1, 500).cumsum() / 50 + np.sin(np.arange(500) / 15)
feat_b = np.random.gamma(2, 1, 500)
feat_c = np.random.uniform(-1, 1, 500)
feat_d = np.random.normal(5, 2, 500)
feat_e = np.random.beta(2, 5, 500)
y = np.where(
    feat_a + 0.3 * feat_b + np.random.normal(0, 0.5, 500) > 1.5,
    "C1",
    np.where(feat_d > 6, "C2", "C3"),
)
df = pd.DataFrame(
    {
        "timestamp": ts,
        "feat_a": feat_a,
        "feat_b": feat_b,
        "feat_c": feat_c,
        "feat_d": feat_d,
        "feat_e": feat_e,
        "target": y,
    }
)
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/sample.csv", index=False)
print("SUCCESS")
