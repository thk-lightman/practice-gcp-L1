"""
Batch prediction script for Cloud Run Jobs.
Loads trace, generates predictions for all campaigns, outputs to stdout (or GCS in production).

Usage:
  Local:  python batch_predict.py
  Cloud:  gcloud run jobs execute batch-predict
"""

import arviz as az
import numpy as np
import json
import sys
from datetime import datetime, UTC

# Load model
trace = az.from_netcdf("model_trace.nc")
with open("model_meta.json") as f:
    meta = json.load(f)

posterior_theta = trace.posterior["theta"].values.reshape(-1, meta["K"])

# Generate batch predictions
results = {
    "generated_at": datetime.now(UTC).isoformat(),
    "model_version": meta["model_version"],
    "campaigns": [],
}

for i, cid in enumerate(meta["campaign_ids"]):
    samples = posterior_theta[:, i]
    results["campaigns"].append({
        "campaign_id": cid,
        "point_estimate": round(float(np.mean(samples)), 4),
        "credible_interval_95": [
            round(float(np.percentile(samples, 2.5)), 4),
            round(float(np.percentile(samples, 97.5)), 4),
        ],
        "std": round(float(np.std(samples)), 4),
        "n_observations": meta["N"][i],
        "observed_conversions": meta["y"][i],
        "prob_above_20pct": round(float(np.mean(samples > 0.2)), 4),
    })

# Output
print(json.dumps(results, indent=2))
print(f"\n✅ Batch prediction complete: {len(results['campaigns'])} campaigns", file=sys.stderr)
