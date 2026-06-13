"""
Hierarchical Bayesian model for multi-campaign conversion rate estimation.
Run locally to generate posterior trace + metadata.

Model:
    alpha, beta ~ Gamma(1, 1)           # hyperprior
    theta_k ~ Beta(alpha, beta)         # campaign-level conversion rate
    y_k ~ Binomial(N_k, theta_k)       # observed conversions

Output:
    model_trace.nc   — ArviZ InferenceData (posterior samples)
    model_meta.json  — campaign metadata (ids, N, y)
"""

import pymc as pm
import numpy as np
import arviz as az
import json

# --- Simulated data: K campaigns ---
np.random.seed(42)
K = 8
true_rates = np.random.beta(2, 5, size=K)
N = np.random.randint(100, 1000, size=K)
y = np.random.binomial(N, true_rates)

campaign_ids = [f"camp_{i}" for i in range(K)]

print(f"Campaigns: {K}")
for i in range(K):
    print(f"  {campaign_ids[i]}: {y[i]}/{N[i]} = {y[i]/N[i]:.3f} (true: {true_rates[i]:.3f})")

# --- Hierarchical Bayesian model ---
with pm.Model() as model:
    alpha = pm.Gamma("alpha", alpha=1, beta=1)
    beta = pm.Gamma("beta", alpha=1, beta=1)
    theta = pm.Beta("theta", alpha=alpha, beta=beta, shape=K)
    obs = pm.Binomial("obs", n=N, p=theta, observed=y)

    trace = pm.sample(2000, tune=1000, return_inferencedata=True)

# --- Save ---
trace.to_netcdf("model_trace.nc")

meta = {
    "K": K,
    "N": N.tolist(),
    "y": y.tolist(),
    "campaign_ids": campaign_ids,
    "model_version": "v1.0-hierarchical-beta-binomial",
}
with open("model_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("\n✅ Model trained. Saved: model_trace.nc, model_meta.json")
