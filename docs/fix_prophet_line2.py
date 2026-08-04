"""
fix_prophet_line2.py
Patches the broken Prophet line via raw string replacement in the JSON file.
"""
import json

path = r'C:\Users\karth\Projects\AI Powered\docs\profitsync_model_fixed.ipynb'

with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
fixed = False

for i, cell in enumerate(cells):
    if cell.get('cell_type') != 'code':
        continue
    src = cell.get('source', [])
    # source may be a list of strings or a single string
    if isinstance(src, list):
        full = ''.join(src)
    else:
        full = src

    if 'seasonality_mode' not in full:
        continue

    # The broken line (as it appears in the joined source):
    BROKEN = (
        "seasonality_mode='multiplicative'   "
        "# Fix 7: multiplicative better for retail demand"
        ", interval_width=0.95, changepoint_prior_scale=0.05, n_changepoints=n_changepoints)"
    )
    CLEAN = (
        "seasonality_mode='multiplicative',  "
        "interval_width=0.95, changepoint_prior_scale=0.05, n_changepoints=n_changepoints)"
        "\n            # Fix 7: multiplicative seasonality scales with trend (better for Indian retail)"
    )

    if BROKEN in full:
        full = full.replace(BROKEN, CLEAN)
        cell['source'] = [full]
        fixed = True
        print(f'  Fixed cell {i}')
    else:
        # Show lines with seasonality_mode for debug
        for j, line in enumerate(full.split('\n')):
            if 'seasonality_mode' in line:
                print(f'  Cell {i}, line {j}: {repr(line)}')

if not fixed:
    print('WARNING: broken string not found — check debug output above')

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Done.')

# Verify
with open(path, 'r', encoding='utf-8') as f:
    nb2 = json.load(f)
for i, cell in enumerate(nb2['cells']):
    if cell.get('cell_type') != 'code':
        continue
    src = ''.join(cell.get('source', []))
    if 'seasonality_mode' not in src:
        continue
    for line in src.split('\n'):
        if 'seasonality_mode' in line:
            print(f'VERIFY cell {i} seasonality line: {line.strip()[:120]}')
