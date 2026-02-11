import pandas as pd
import ast
import numpy as np

# Đọc file CSV
df = pd.read_csv('data/all_data5.csv')

print(f"Tổng số test cases: {len(df)}\n")

# =============== SỬA LỖI: Xử lý cột equal một cách an toàn ===============
# Ép kiểu về string trước khi dùng .str
df['equal_r1_r2'] = df['equal_r1_r2'].astype(str).str.strip().str.upper() == 'TRUE'
df['equal_r1_r3'] = df['equal_r1_r3'].astype(str).str.strip().str.upper() == 'TRUE'
df['equal_r2_r3'] = df['equal_r2_r3'].astype(str).str.strip().str.upper() == 'TRUE'

# =============== Parse cột time ===============
df['times'] = df['time'].apply(ast.literal_eval)
df['time_r1'] = df['times'].apply(lambda x: x[0])
df['time_r2'] = df['times'].apply(lambda x: x[1])
df['time_r3'] = df['times'].apply(lambda x: x[2])

# =============== Parse độ dài kết quả ===============
def parse_length(s):
    try:
        # s là string như "[[1, 2], [3]]" hoặc "[]"
        return len(ast.literal_eval(s))
    except Exception as e:
        print(f"Lỗi parse length: {s} -> {e}")
        return 0

df['len_r1'] = df['find_counterfactual_set'].apply(parse_length)
df['len_r2'] = df['select_optimal_pairs'].apply(parse_length)
df['len_r3'] = df['improved_counterfactual'].apply(parse_length)

# =============== 1. Thống kê mức độ đồng ý giữa các phương pháp ===============
print("=== THỐNG KÊ MỨC ĐỘ ĐỒNG Ý ===")
total = len(df)

all_agree = df[df['equal_r1_r2'] & df['equal_r1_r3'] & df['equal_r2_r3']].shape[0]
only_r1_r2 = df[df['equal_r1_r2'] & ~df['equal_r1_r3']].shape[0]
only_r1_r3 = df[df['equal_r1_r3'] & ~df['equal_r1_r2']].shape[0]
only_r2_r3 = df[df['equal_r2_r3'] & ~df['equal_r1_r2']].shape[0]
no_agree = total - all_agree - only_r1_r2 - only_r1_r3 - only_r2_r3

agree_summary = pd.DataFrame({
    'Mô tả': [
        'Tất cả 3 phương pháp đồng ý',
        'Chỉ r1 và r2 đồng ý',
        'Chỉ r1 và r3 đồng ý',
        'Chỉ r2 và r3 đồng ý',
        'Không cặp nào đồng ý'
    ],
    'Số lượng': [all_agree, only_r1_r2, only_r1_r3, only_r2_r3, no_agree],
    'Tỷ lệ (%)': [
        100 * all_agree / total,
        100 * only_r1_r2 / total,
        100 * only_r1_r3 / total,
        100 * only_r2_r3 / total,
        100 * no_agree / total
    ]
})
print(agree_summary.round(2))
print()

# =============== 2. Thống kê thời gian thực thi tổng thể ===============
print("=== THỐNG KÊ THỜI GIAN THỰC THI (tổng thể) ===")
time_summary = pd.DataFrame({
    'Phương pháp': ['find_counterfactual_set (r1)', 'select_optimal_pairs (r2)', 'improved_counterfactual (r3)'],
    'Thời gian trung bình (s)': [df['time_r1'].mean(), df['time_r2'].mean(), df['time_r3'].mean()],
    'Thời gian median (s)': [df['time_r1'].median(), df['time_r2'].median(), df['time_r3'].median()],
    'Thời gian max (s)': [df['time_r1'].max(), df['time_r2'].max(), df['time_r3'].max()],
    'Thời gian min (s)': [df['time_r1'].min(), df['time_r2'].min(), df['time_r3'].min()]
})
print(time_summary.round(6))
print()

# =============== 3. Thống kê theo nhóm kích thước n ===============
print("=== THỐNG KÊ THEO NHÓM KÍCH THƯỚC n ===")
group_n = df.groupby('n').agg({
    'time_r1': ['mean', 'max'],
    'time_r2': ['mean', 'max'],
    'time_r3': ['mean', 'max'],
    'equal_r1_r2': 'mean',   # tỷ lệ đồng ý
    'equal_r1_r3': 'mean',
    'equal_r2_r3': 'mean',
    'len_r1': 'mean',
    'len_r2': 'mean',
    'len_r3': 'mean'
}).round(6)

group_n.columns = [
    'time_r1_mean', 'time_r1_max',
    'time_r2_mean', 'time_r2_max',
    'time_r3_mean', 'time_r3_max',
    'agree_r1_r2 (%)', 'agree_r1_r3 (%)', 'agree_r2_r3 (%)',
    'avg_len_r1', 'avg_len_r2', 'avg_len_r3'
]
group_n['agree_r1_r2 (%)'] *= 100
group_n['agree_r1_r3 (%)'] *= 100
group_n['agree_r2_r3 (%)'] *= 100
group_n = group_n.reset_index()
print(group_n)
print()

# =============== 4. Thống kê độ dài tập hợp tìm được ===============
print("=== THỐNG KÊ ĐỘ DÀI TẬP HỢP TRẢ VỀ (số phần tử tìm được) ===")
length_summary = pd.DataFrame({
    'Phương pháp': ['r1', 'r2', 'r3'],
    'Độ dài trung bình': [df['len_r1'].mean(), df['len_r2'].mean(), df['len_r3'].mean()],
    'Độ dài median': [df['len_r1'].median(), df['len_r2'].median(), df['len_r3'].median()],
    'Số trường hợp tìm được (>0)': [
        (df['len_r1'] > 0).sum(),
        (df['len_r2'] > 0).sum(),
        (df['len_r3'] > 0).sum()
    ],
    'Tỷ lệ tìm được (%)': [
        100 * (df['len_r1'] > 0).sum() / total,
        100 * (df['len_r2'] > 0).sum() / total,
        100 * (df['len_r3'] > 0).sum() / total
    ]
})
print(length_summary.round(2))