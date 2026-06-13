"""
FastAPI server for Bayesian conversion rate inference.
Loads pre-trained posterior trace and serves predictions with credible intervals.
"""

import os
from fastapi import FastAPI, HTTPException
import arviz as az
import numpy as np
import json

app = FastAPI(title="Bayesian Conversion Rate API", version="1.0.0")

# --- Load model at startup ---
trace = az.from_netcdf("model_trace.nc")
with open("model_meta.json") as f:
    meta = json.load(f)

posterior_theta = trace.posterior["theta"].values.reshape(-1, meta["K"])


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "model_version": meta["model_version"],
        "n_campaigns": meta["K"],
        "revision": os.environ.get("K_REVISION", "local"),
    }


@app.get("/predict/{campaign_id}")
def predict(campaign_id: str):
    """Single campaign conversion rate estimate with credible interval."""
    if campaign_id not in meta["campaign_ids"]:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found")

    idx = meta["campaign_ids"].index(campaign_id)
    samples = posterior_theta[:, idx]

    return {
        "campaign_id": campaign_id,
        "point_estimate": round(float(np.mean(samples)), 4),
        "credible_interval_95": [
            round(float(np.percentile(samples, 2.5)), 4),
            round(float(np.percentile(samples, 97.5)), 4),
        ],
        "std": round(float(np.std(samples)), 4),
        "n_observations": meta["N"][idx],
        "observed_conversions": meta["y"][idx],
        "model_version": meta["model_version"],
    }


@app.get("/predict")
def predict_all():
    """All campaigns conversion rate comparison."""
    results = []
    for i, cid in enumerate(meta["campaign_ids"]):
        samples = posterior_theta[:, i]
        results.append({
            "campaign_id": cid,
            "point_estimate": round(float(np.mean(samples)), 4),
            "credible_interval_95": [
                round(float(np.percentile(samples, 2.5)), 4),
                round(float(np.percentile(samples, 97.5)), 4),
            ],
        })
    return {
        "campaigns": results,
        "model_version": meta["model_version"],
    }
