import pandas as pd
import ast
import glob
import os
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# ----- 1. Đọc và gộp các file -----
all_files = glob.glob("csv_output_45/all_data*_10.csv")
df_list = []
for fp in all_files:
    tmp = pd.read_csv(fp, dtype=str)
    tmp['source_file'] = os.path.basename(fp)
    df_list.append(tmp)
df = pd.concat(df_list, ignore_index=True)

# ----- 2. Ép kiểu và loại bỏ NaN ở 'ord' -----
df['ord'] = pd.to_numeric(df['ord'], errors='coerce')
df = df.dropna(subset=['ord'])
df['ord'] = df['ord'].astype(int)

# ----- 3. Gán nhóm range theo ord (logic sinh data) -----
def bin_range_by_ord(k):
    if k < 25:
        return '5-10'
    elif k < 50:
        return '10-20'
    else:
        return '20-25'

df['range'] = df['ord'].apply(bin_range_by_ord)

# ----- 4. Chuẩn bị cột lỗi -----
df['error_flag'] = (df['equal_r1_r2'] == 'FALSE')

# ----- 5. Bảng 1: Mean_Error, Std_Error, CV (%) -----
rates = (
    df
    .groupby(['range','ord'], as_index=False)['error_flag']
    .mean()
    .assign(error_rate=lambda d: d['error_flag'] * 100)
)

stats1 = (
    rates
    .groupby('range')['error_rate']
    .agg(Mean_Error=lambda x: x.mean(),
         Std_Error=lambda x: x.std())
    .reset_index()
)
stats1['CV (%)'] = stats1['Std_Error'] / stats1['Mean_Error'] * 100

print("Bảng 1:")
print(stats1.to_string(index=False))

# ----- 6. Phân tích khác biệt giữa các nhóm: Tukey HSD -----
print("\nTukey HSD test giữa các nhóm error_rate:")
tukey = pairwise_tukeyhsd(
    endog=rates['error_rate'],
    groups=rates['range'],
    alpha=0.05
)
print(tukey.summary())

# ----- 7. Tính CV false ratio chi tiết -----
cv_table = (
    rates
    .groupby('range')['error_rate']
    .agg(Mean_Error='mean', Std_Error='std')
    .assign(CV=lambda d: d['Std_Error'] / d['Mean_Error'])
    .reset_index()
)
print("\nCV false ratio theo nhóm (thang 0-1):")
print(cv_table.to_string(index=False, float_format="%.4f"))

# ----- 8. Bảng 2: Empty set, Longer set, Mean/Range diff -----
df_err = df[df['error_flag']].copy()

# Parse độ dài tập r1 và r2
df_err['len_r1'] = df_err['find_counterfactual_set'].apply(lambda s: len(ast.literal_eval(s)))
df_err['len_r2'] = df_err['select_optimal_pairs'].apply(lambda s: len(ast.literal_eval(s)))

# Tính các chỉ số
tmp = []
for rng, sub in df_err.groupby('range'):
    total = len(sub)
    empty_pct = (sub['len_r1'] == 0).sum() / total * 100
    longer_pct = (sub['len_r1'] > sub['len_r2']).sum() / total * 100

    diffs = sub['len_r2'] - sub['len_r1']
    mean_diff = diffs.mean()
    dmin, dmax = int(diffs.min()), int(diffs.max())

    tmp.append({
        'Range':             rng,
        'Empty set (%)':     empty_pct,
        'Longer set (%)':    longer_pct,
        'Mean length diff.': mean_diff,
        'Range diff.':       f"{dmin} → {dmax}"
    })

stats2 = pd.DataFrame(tmp)
print("\nBảng 2:")
print(stats2.to_string(index=False))
