"""
fix_prophet_line.py
Patches the broken Prophet constructor line in profitsync_model_fixed.ipynb.
The inline comment accidentally commented out the trailing arguments.
"""
import json

path = r'C:\Users\karth\Projects\AI Powered\docs\profitsync_model_fixed.ipynb'

with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
fixed_count = 0

for i, cell in enumerate(cells):
    if cell.get('cell_type') != 'code':
        continue
    src = ''.join(cell.get('source', []))
    if 'seasonality_mode' not in src:
        continue

    lines = src.split('\n')
    new_lines = []
    for line in lines:
        if "seasonality_mode='multiplicative'" in line and '# Fix 7' in line and 'interval_width' in line:
            # This is the broken single-line Prophet call with the comment mid-line.
            # Extract the leading whitespace
            indent = len(line) - len(line.lstrip())
            ws = ' ' * indent
            # Rebuild as two lines: comment above, clean Prophet call below
            new_lines.append(ws + '# Fix 7: multiplicative seasonality scales with trend (better for retail)')
            new_lines.append(
                ws + "m = Prophet("
                "growth='linear', "
                "yearly_seasonality=True, "
                "weekly_seasonality=True, "
                "daily_seasonality=False, "
                "seasonality_mode='multiplicative', "
                "interval_width=0.95, "
                "changepoint_prior_scale=0.05, "
                "n_changepoints=n_changepoints)"
            )
            fixed_count += 1
            print(f'  Fixed Prophet line in cell {i}')
        else:
            new_lines.append(line)

    cells[i]['source'] = ['\n'.join(new_lines)]

print(f'Total fixes applied: {fixed_count}')

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Saved fixed notebook.')

# Quick verify
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'Fix 7' in content and 'interval_width' in content:
    # Check if comment and interval_width are no longer on same line
    for line in content.split('\n'):
        if '# Fix 7' in line and 'interval_width' in line:
            print('ERROR: still on same line:', line[:100])
            break
    else:
        print('VERIFY OK: comment and interval_width are on separate lines.')
else:
    print('WARNING: could not verify fix.')
