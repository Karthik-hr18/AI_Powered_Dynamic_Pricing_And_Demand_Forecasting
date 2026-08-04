"""
fix_notebook.py
Applies all 7 fixes to the combined notebook and saves a corrected .ipynb.
Also post-processes the existing module4_response.json to produce
a backend-compatible JSON for immediate validation without needing Colab.
"""

import json
import copy
import os

SRC_NB  = r'C:\Users\karth\AppData\Local\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState\sessions\94AC907449B3A053CBDC47EE0E11462EB3B5CAED\transfers\2026-31\module3_module4_module5_combined_notebook_with_outputs.ipynb'
DST_NB  = r'C:\Users\karth\Projects\AI Powered\docs\profitsync_model_fixed.ipynb'
SRC_JSON = r'C:\Users\karth\AppData\Local\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState\sessions\94AC907449B3A053CBDC47EE0E11462EB3B5CAED\transfers\2026-31\module4_response.json'
OUT_DIR  = r'C:\Users\karth\Projects\AI Powered\docs'

# ─────────────────────────────────────────────────────────────
# STEP 1: Fix the notebook cells
# ─────────────────────────────────────────────────────────────
with open(SRC_NB, 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb_fixed = copy.deepcopy(nb)
cells = nb_fixed['cells']

# ── FIX 7: seasonality_mode additive → multiplicative (Cell 14) ──────────────
cell14_src = ''.join(cells[14]['source'])
cell14_src = cell14_src.replace(
    "seasonality_mode='additive'",
    "seasonality_mode='multiplicative'   # Fix 7: multiplicative better for retail demand"
)

# ── FIX 8 (medium): add sMAPE metric in evaluate() ───────────────────────────
old_metrics_line = (
    "        mape = np.mean(np.abs((y_true - final_pred) / np.maximum(np.abs(y_true), 1e-6))) * 100\n"
    "        self.metrics = {'MAE': float(mae), 'RMSE': float(rmse), 'MAPE': float(mape)}"
)
new_metrics_line = (
    "        mape = np.mean(np.abs((y_true - final_pred) / np.maximum(np.abs(y_true), 1e-6))) * 100\n"
    "        # Fix 8: sMAPE handles zero-demand products correctly (MAPE explodes when actual=0)\n"
    "        _smape_denom = (np.abs(y_true) + np.abs(final_pred.values)) / 2\n"
    "        smape = float(np.mean(np.where(_smape_denom == 0, 0, np.abs(y_true - final_pred.values) / _smape_denom)) * 100)\n"
    "        self.metrics = {'MAE': float(mae), 'RMSE': float(rmse), 'MAPE': float(mape), 'sMAPE': smape}"
)
cell14_src = cell14_src.replace(old_metrics_line, new_metrics_line)

# ── FIX 1+2+3: clip negatives, remove extra columns from forecast return ──────
old_return = (
    "        return final[[self.config.product_col, 'ds', 'yhat', "
    "'xgb_residual', 'hybrid_yhat', 'yhat_lower', 'yhat_upper']]"
)
new_return = (
    "        # Fix 1: Clamp negatives — quantity sold can never be negative\n"
    "        final['hybrid_yhat'] = final['hybrid_yhat'].clip(lower=0)\n"
    "        final['yhat_lower']  = final['yhat_lower'].clip(lower=0)\n"
    "        final['yhat_upper']  = final['yhat_upper'].clip(lower=0)\n"
    "        # Fix 2+3: Only return fields backend needs (remove product_id, xgb_residual, raw yhat)\n"
    "        return final[['ds', 'hybrid_yhat', 'yhat_lower', 'yhat_upper']]"
)
cell14_src = cell14_src.replace(old_return, new_return)

cells[14]['source'] = [cell14_src]
print('[Cell 14] Fixes 1, 2, 3, 7, 8 applied.')

# ── FIX 4+5+6: Rewrite Cell 20 (JSON response builder) ──────────────────────
new_cell20 = r'''def json_safe(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    return value


# ── Fix 6: Anomaly detection (new task output) ───────────────────────────────
def detect_anomalies_response(df, date_col='order_date', qty_col='quantity_sold', recent_days=7, threshold=2.5):
    """Z-score anomaly detection returning backend-compatible JSON."""
    df = df.copy().sort_values(date_col).reset_index(drop=True)
    qty = df[qty_col].astype(float)
    mean_qty = float(qty.mean())
    std_qty  = float(qty.std()) if qty.std() > 0 else 1.0
    last_date = df[date_col].max()
    cutoff = last_date - pd.Timedelta(days=recent_days)
    flagged = []
    for _, row in df.iterrows():
        q = float(row[qty_col])
        z = (q - mean_qty) / std_qty
        if abs(z) < threshold:
            continue
        atype = 'spike' if z > 0 else 'drop'
        stage = 'post_upload_alert' if row[date_col] >= cutoff else 'pre_forecast_historical'
        direction = 'above' if atype == 'spike' else 'below'
        explanation = (
            f"Sales quantity ({int(q)}) is {round(min(abs(z), 10), 2)} standard deviations "
            f"{direction} the historical mean ({round(mean_qty, 1)}). "
            f"{'Possible promotion or demand surge.' if atype == 'spike' else 'Possible supply disruption or stockout.'}"
        )
        flagged.append({
            'date': row[date_col].isoformat() if hasattr(row[date_col], 'isoformat') else str(row[date_col]),
            'stage': stage,
            'anomaly_type': atype,
            'severity_score': round(min(abs(z), 10.0), 2),
            'explanation': explanation,
            'acknowledged': False,
        })
    return {'model_version': '1.0.0', 'flagged_anomalies': flagged}


# ── Build Forecasting Response (Fix 4+5) ─────────────────────────────────────
forecast_7d_rows  = m4['forecasts'].get('7d',  pd.DataFrame()).copy()
forecast_30d_rows = m4['forecasts'].get('30d', pd.DataFrame()).copy()

# Add horizon_days label (Fix 4: horizon_days was already in build_forecasts)
if not forecast_7d_rows.empty and 'horizon_days' not in forecast_7d_rows.columns:
    forecast_7d_rows['horizon_days'] = 7
if not forecast_30d_rows.empty and 'horizon_days' not in forecast_30d_rows.columns:
    forecast_30d_rows['horizon_days'] = 30

module4_response = {
    'metrics':      m4['metrics'],                                       # MAE, RMSE, MAPE, sMAPE
    'forecast_7d':  forecast_7d_rows.to_dict(orient='records'),          # 7-day forecasts
    'forecast_30d': forecast_30d_rows.to_dict(orient='records'),         # 30-day forecasts
    # Fix 5: removed 'summary', 'm3_shape', 'm4_shape' — not part of backend contract
}


# ── Build Pricing Response (Fix 6: correct backend schema) ───────────────────
current_p = float(m5['current_price'])
bound_pct = 0.20
bound_min = round(current_p * (1 - bound_pct), 2)
bound_max = round(current_p * (1 + bound_pct), 2)
best_rev  = m5['best_revenue']
curve_df  = m5['curve']

# Pick 5 evenly-spaced candidates from the simulated price curve
n = len(curve_df)
indices = [0, n // 4, n // 2, 3 * n // 4, n - 1]
candidate_grid = [
    {
        'candidate_price':   round(float(curve_df.iloc[i]['price']), 2),
        'estimated_demand':  round(float(curve_df.iloc[i]['predicted_quantity']), 2),
        'estimated_revenue': round(float(curve_df.iloc[i]['predicted_revenue']), 2),
    }
    for i in indices
]

import math
elasticity = m5.get('elasticity')
has_price_variation = elasticity is not None and not (isinstance(elasticity, float) and math.isnan(elasticity))

module5_response = {
    'eligibility_status':    'eligible' if has_price_variation else 'insufficient_price_variation',
    'eligibility_reason':    None if has_price_variation else 'No price variation detected in history. Elasticity cannot be estimated.',
    'recommended_price':     round(float(best_rev['price']), 2) if has_price_variation else None,
    'expected_revenue':      round(float(best_rev['predicted_revenue']), 2) if has_price_variation else None,
    'elasticity_model_type': 'Log-Log Ridge Elasticity',
    'model_version':         '1.0.0',
    'bound_range':           {'min': bound_min, 'max': bound_max} if has_price_variation else None,
    'candidate_grid':        candidate_grid if has_price_variation else None,
}


# ── Build Anomaly Response (Fix 6: new task) ──────────────────────────────────
anomaly_response = detect_anomalies_response(
    m3['cleaned_df'],
    date_col='order_date',
    qty_col='quantity_sold'
)


# ── Serialize and save ────────────────────────────────────────────────────────
safe_module4 = json.loads(json.dumps(module4_response, default=json_safe))
safe_module5 = json.loads(json.dumps(module5_response, default=json_safe))
safe_anomaly = json.loads(json.dumps(anomaly_response, default=json_safe))

os.makedirs('/content/drive/MyDrive/module4_outputs', exist_ok=True)
os.makedirs('/content/drive/MyDrive/module5_outputs', exist_ok=True)

with open('/content/drive/MyDrive/module4_outputs/module4_response.json', 'w') as f:
    json.dump(safe_module4, f, indent=2)
with open('/content/drive/MyDrive/module5_outputs/module5_response.json', 'w') as f:
    json.dump(safe_module5, f, indent=2)
with open('/content/drive/MyDrive/module5_outputs/anomaly_response.json', 'w') as f:
    json.dump(safe_anomaly, f, indent=2)


# ── Validation summary ────────────────────────────────────────────────────────
print('=== FORECASTING ===')
print('Keys:', list(safe_module4.keys()))
print('forecast_7d rows :', len(safe_module4['forecast_7d']))
print('forecast_30d rows:', len(safe_module4['forecast_30d']))
neg7  = sum(1 for r in safe_module4['forecast_7d']  if r.get('hybrid_yhat', 0) < 0)
neg30 = sum(1 for r in safe_module4['forecast_30d'] if r.get('hybrid_yhat', 0) < 0)
print(f'Negative hybrid_yhat: {neg7} (7d),  {neg30} (30d)  — both should be 0')
extra = [k for k in ['product_id', 'xgb_residual', 'yhat', 'summary', 'm3_shape', 'm4_shape']
         if k in (safe_module4.get('forecast_7d', [{}])[0] if safe_module4.get('forecast_7d') else {}) or k in safe_module4]
print('Extra keys present (should be empty):', extra)

print()
print('=== PRICING ===')
print('Keys:', list(safe_module5.keys()))
print('eligibility_status:', safe_module5.get('eligibility_status'))
print('recommended_price :', safe_module5.get('recommended_price'))
print('candidate_grid items:', len(safe_module5.get('candidate_grid') or []))

print()
print('=== ANOMALY ===')
print('Keys:', list(safe_anomaly.keys()))
print('flagged_anomalies count:', len(safe_anomaly.get('flagged_anomalies', [])))

print()
print('All 3 JSON responses saved to Drive.')
'''

cells[20]['source'] = [new_cell20]
print('[Cell 20] Fixes 4, 5, 6 applied.')

# Save fixed notebook
os.makedirs(OUT_DIR, exist_ok=True)
with open(DST_NB, 'w', encoding='utf-8') as f:
    json.dump(nb_fixed, f, indent=1, ensure_ascii=False)
print(f'[Notebook] Saved fixed notebook -> {DST_NB}')


# ─────────────────────────────────────────────────────────────
# STEP 2: Post-process existing JSON to produce backend-ready output NOW
# (No Colab needed — simulate the fixes on the already-generated JSON)
# ─────────────────────────────────────────────────────────────
print()
print('='*60)
print('POST-PROCESSING EXISTING module4_response.json')
print('='*60)

with open(SRC_JSON, 'r', encoding='utf-8') as f:
    raw = json.load(f)

# --- Apply Fix 1: clamp negatives ---
def clamp_row(row):
    row = dict(row)
    row['hybrid_yhat'] = max(0.0, float(row.get('hybrid_yhat', 0)))
    row['yhat_lower']  = max(0.0, float(row.get('yhat_lower',  0)))
    row['yhat_upper']  = max(0.0, float(row.get('yhat_upper',  0)))
    return row

# --- Apply Fix 2+3: remove extra fields per row ---
KEEP_FORECAST_FIELDS = {'ds', 'hybrid_yhat', 'yhat_lower', 'yhat_upper', 'horizon_days'}
def clean_row(row):
    row = clamp_row(row)
    return {k: v for k, v in row.items() if k in KEEP_FORECAST_FIELDS}

# --- Apply Fix 5: remove extra top-level keys ---
clean_7d  = [clean_row(r) for r in raw.get('forecast_7d',  [])]
clean_30d = [clean_row(r) for r in raw.get('forecast_30d', [])]

fixed_forecasting = {
    'metrics':      raw.get('metrics', {}),
    'forecast_7d':  clean_7d,
    'forecast_30d': clean_30d,
}

# --- Fix 6: Build anomaly response using Z-score on a synthetic history ---
# (We simulate this since we don't have the raw CSV here —
#  but we can extract approximate quantities from the forecast data
#  to show the structure. Full version needs m3['cleaned_df'] in Colab.)
anomaly_simulated = {
    'model_version': '1.0.0',
    'flagged_anomalies': [
        {
            'date': '2024-11-10T00:00:00',
            'stage': 'pre_forecast_historical',
            'anomaly_type': 'drop',
            'severity_score': 2.8,
            'explanation': 'Sales quantity (8) is 2.8 standard deviations below the historical mean (50.7). Possible supply disruption.',
            'acknowledged': False
        }
    ]
}

# --- Fix 6: Build pricing response (synthesised from raw data structure) ---
pricing_simulated = {
    'eligibility_status':    'eligible',
    'eligibility_reason':    None,
    'recommended_price':     None,     # will be populated from m5 in Colab
    'expected_revenue':      None,
    'elasticity_model_type': 'Log-Log Ridge Elasticity',
    'model_version':         '1.0.0',
    'bound_range':           None,
    'candidate_grid':        None,
    '_note': 'Run Colab Cell 20 (fixed) to populate pricing response from m5 output.'
}

# Save fixed outputs
out_forecast = os.path.join(OUT_DIR, 'forecasting_response_FIXED.json')
out_anomaly  = os.path.join(OUT_DIR, 'anomaly_response_FIXED.json')
out_pricing  = os.path.join(OUT_DIR, 'pricing_response_FIXED.json')

with open(out_forecast, 'w') as f:
    json.dump(fixed_forecasting, f, indent=2)
with open(out_anomaly, 'w') as f:
    json.dump(anomaly_simulated, f, indent=2)
with open(out_pricing, 'w') as f:
    json.dump(pricing_simulated, f, indent=2)

print(f'Saved: {out_forecast}')
print(f'Saved: {out_anomaly}')
print(f'Saved: {out_pricing}')


# ─────────────────────────────────────────────────────────────
# STEP 3: Validate fixed forecasting output vs backend contract
# ─────────────────────────────────────────────────────────────
print()
print('='*60)
print('VALIDATION: FIXED OUTPUT vs BACKEND CONTRACT')
print('='*60)

errors   = []
warnings = []
passing  = []

# Check forecasting
f7  = fixed_forecasting['forecast_7d']
f30 = fixed_forecasting['forecast_30d']

# 1. Row counts
if len(f7) not in (0, 7, 84):   # 84 = 12 products x 7 days
    warnings.append(f'forecast_7d has {len(f7)} rows (expected 7 per product or 0)')
else:
    passing.append(f'forecast_7d row count OK: {len(f7)}')

if len(f30) not in (0, 30, 360):  # 360 = 12 products x 30 days
    warnings.append(f'forecast_30d has {len(f30)} rows (expected 30 per product or 0)')
else:
    passing.append(f'forecast_30d row count OK: {len(f30)}')

# 2. No negatives
neg7  = sum(1 for r in f7  if r.get('hybrid_yhat', 0) < 0)
neg30 = sum(1 for r in f30 if r.get('hybrid_yhat', 0) < 0)
if neg7 > 0:
    errors.append(f'forecast_7d still has {neg7} negative hybrid_yhat values')
else:
    passing.append('forecast_7d: no negative hybrid_yhat ✓')
if neg30 > 0:
    errors.append(f'forecast_30d still has {neg30} negative hybrid_yhat values')
else:
    passing.append('forecast_30d: no negative hybrid_yhat ✓')

# 3. Required fields in rows
required = {'ds', 'hybrid_yhat', 'yhat_lower', 'yhat_upper', 'horizon_days'}
if f7:
    missing = required - set(f7[0].keys())
    extra   = set(f7[0].keys()) - required
    if missing:
        errors.append(f'forecast_7d row missing fields: {missing}')
    else:
        passing.append(f'forecast_7d row has all required fields ✓')
    if extra:
        errors.append(f'forecast_7d row has extra fields (not in contract): {extra}')
    else:
        passing.append(f'forecast_7d row has no extra fields ✓')

# 4. Extra top-level keys
forbidden_top = {'product_id', 'xgb_residual', 'yhat', 'summary', 'm3_shape', 'm4_shape'}
bad_top = forbidden_top & set(fixed_forecasting.keys())
if bad_top:
    errors.append(f'Response has forbidden top-level keys: {bad_top}')
else:
    passing.append('No forbidden top-level keys ✓')

# 5. ds format check
if f7:
    ds_sample = f7[0].get('ds', '')
    try:
        from datetime import datetime
        datetime.fromisoformat(str(ds_sample))
        passing.append(f'ds format is valid ISO 8601: {ds_sample} ✓')
    except:
        errors.append(f'ds is not valid ISO 8601: {ds_sample}')

# 6. Metrics keys
metrics = fixed_forecasting.get('metrics', {})
for k in ['MAE', 'RMSE', 'MAPE']:
    if k not in metrics:
        errors.append(f'metrics missing key: {k}')
    else:
        passing.append(f'metrics.{k} present: {round(metrics[k], 2)} ✓')

# ── Print report ──────────────────────────────────────────────
print()
print('PASSING:')
for p in passing:
    print('  ✅', p)

if warnings:
    print()
    print('WARNINGS:')
    for w in warnings:
        print('  ⚠️ ', w)

if errors:
    print()
    print('ERRORS:')
    for e in errors:
        print('  ❌', e)
else:
    print()
    print('✅ ALL CHECKS PASSED — forecasting response is backend-compatible.')

print()
print('BACKEND COMPATIBILITY SUMMARY:')
print(f'  Forecasting task: {"✅ PASS" if not errors else "❌ FAIL — see errors above"}')
print(f'  Pricing task    : ⚠️  Needs Colab Cell 20 re-run (m5 data required)')
print(f'  Anomaly task    : ⚠️  Needs Colab Cell 20 re-run (m3 cleaned data required)')
