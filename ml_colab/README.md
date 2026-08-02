# Google Colab ML Training Notebooks

This directory contains the Google Colab Jupyter Notebooks used for model development, exploratory data analysis, feature engineering experiments, model training, and performance evaluations.

## Project Structure Separation

To maintain clean separation between offline research and online production execution:
1. **`ml_colab/` (This folder)**: Dedicated entirely to offline training notebooks, dataset preparation scripts, and notebook documentation. Files in this folder are **never** imported or executed by the production backend.
2. **`ml/`**: Houses only the finalized, refactored, production-ready inference and preprocessing code.
3. **`backend/artifacts/`**: Contains the local model binary weights (`.pkl`/`.joblib`) and their corresponding metadata files (`metadata.json`).
4. **`backend/app/core/ml/`**: Manages runtime cache singletons, file verification, and model loader adapters.

---

## Notebook Files

* **`forecasting_training.ipynb`**: Demand forecasting model training (Prophet/XGBoost).
* **`pricing_training.ipynb`**: Price elasticity and pricing optimization models.
* **`anomaly_training.ipynb`**: Sales anomaly detection (Isolation Forest / standard deviation boundaries).
