#!/usr/bin/env python3
"""
保護因子 vs 危險因子分析
分析當事人在危機中使用的保護因子和面臨的危險因子
"""

import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 設定中文字體
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# 讀取資料
df = pd.read_csv('../conversation_final.csv')

# 過濾 HUMAN 訊息
df_human = df[df['speaker'] == 'HUMAN'].copy()
df_human = df_human.reset_index(drop=True)

print("=" * 80)
print("📊 保護因子 (Protective Factors) 分析")
print("=" * 80)

# 解析 protective_factors（逗號分隔）
all_pf = []
pf_by_msg = {}
for idx, row in df_human.iterrows():
    msg_id = int(row['message_id'])
    pf = str(row['protective_factors']).strip()
    if pf and pf != 'nan' and pf != '':
        factors = [f.strip() for f in pf.split(',') if f.strip()]
        all_pf.extend(factors)
        pf_by_msg[msg_id] = factors

print(f"\n總出現次數: {len(all_pf)}")
print(f"有保護因子的訊息: {len(pf_by_msg)}")

# 頻率分析
pf_counter = Counter(all_pf)

print(f"\n📈 Top 15 頻繁保護因子:")
for i, (factor, count) in enumerate(pf_counter.most_common(15), 1):
    print(f"  {i:2d}. {factor:40s} : {count:3d} 次")

print("\n" + "=" * 80)
print("⚠️  危險因子 (Risk Factors) 分析")
print("=" * 80)

# 解析 risk_factors
all_rf = []
rf_by_msg = {}
for idx, row in df_human.iterrows():
    msg_id = int(row['message_id'])
    rf = str(row['risk_factors']).strip()
    if rf and rf != 'nan' and rf != '':
        factors = [f.strip() for f in rf.split(',') if f.strip()]
        all_rf.extend(factors)
        rf_by_msg[msg_id] = factors

print(f"\n總出現次數: {len(all_rf)}")
print(f"有危險因子的訊息: {len(rf_by_msg)}")

# 頻率分析
rf_counter = Counter(all_rf)

print(f"\n📈 Top 15 頻繁危險因子:")
for i, (factor, count) in enumerate(rf_counter.most_common(15), 1):
    print(f"  {i:2d}. {factor:40s} : {count:3d} 次")

print("\n" + "=" * 80)
print("🔄 因子分析總結")
print("=" * 80)

print(f"\n保護因子統計:")
print(f"  - 總頻次: {len(all_pf)}")
print(f"  - 不同類型: {len(pf_counter)}")
print(f"  - 平均每條訊息: {len(all_pf) / len(df_human):.2f} 個")
print(f"  - 涵蓋訊息比例: {len(pf_by_msg) / len(df_human) * 100:.1f}%")

print(f"\n危險因子統計:")
print(f"  - 總頻次: {len(all_rf)}")
print(f"  - 不同類型: {len(rf_counter)}")
print(f"  - 平均每條訊息: {len(all_rf) / len(df_human):.2f} 個")
print(f"  - 涵蓋訊息比例: {len(rf_by_msg) / len(df_human) * 100:.1f}%")

print(f"\n平衡指數 (風險/保護):")
balance = len(all_rf) / len(all_pf) if len(all_pf) > 0 else float('inf')
print(f"  - 危險因子/保護因子 = {balance:.2f}")
if balance < 1:
    print(f"  - 解讀: 保護因子更多 ✅ (比例 1:{1/balance:.1f})")
else:
    print(f"  - 解讀: 危險因子更多 ⚠️ (比例 {balance:.1f}:1)")

# 找出同時有保護和危險因子的訊息
both = set(pf_by_msg.keys()) & set(rf_by_msg.keys())
print(f"\n同時出現保護+危險因子的訊息: {len(both)} 條")
print(f"  - 訊息編號: {sorted(both)}")

# 關鍵轉折點分析
print("\n" + "=" * 80)
print("🔑 關鍵轉折點因子分析")
print("=" * 80)

crisis_msgs = [55, 57, 61, 65]
for msg_id in crisis_msgs:
    row = df_human[df_human['message_id'] == msg_id]
    if len(row) > 0:
        row = row.iloc[0]
        cssrs = row['cssrs_score']
        pf = str(row['protective_factors']).strip()
        rf = str(row['risk_factors']).strip()
        print(f"\n訊息 #{msg_id} (C-SSRS = {cssrs}):")
        if pf and pf != 'nan':
            print(f"  保護: {pf}")
        else:
            print(f"  保護: (無)")
        if rf and rf != 'nan':
            print(f"  危險: {rf}")
        else:
            print(f"  危險: (無)")

# 計算每條訊息的因子數量
protective_counts = []
risk_counts = []

for idx, row in df_human.iterrows():
    # 保護因子
    pf = str(row['protective_factors']).strip()
    if pf and pf != 'nan' and pf != '':
        pf_count = len([f.strip() for f in pf.split(',') if f.strip()])
    else:
        pf_count = 0
    protective_counts.append(pf_count)

    # 危險因子
    rf = str(row['risk_factors']).strip()
    if rf and rf != 'nan' and rf != '':
        rf_count = len([f.strip() for f in rf.split(',') if f.strip()])
    else:
        rf_count = 0
    risk_counts.append(rf_count)

# 創建時間序列圖表
fig, ax = plt.subplots(figsize=(15, 7))

x = np.arange(len(df_human))
days = df_human['day'].values

# 計算因子累積值
risk_cumsum = np.array(protective_counts) + np.array(risk_counts)

# 識別高風險區間（#55-#57 及周圍）
high_risk_msgs = {55, 57}
high_risk_indices = set()
for idx, row in df_human.iterrows():
    if int(row['message_id']) in high_risk_msgs:
        high_risk_indices.add(idx)

# 繪製保護因子（綠色填充）
ax.fill_between(x, 0, protective_counts, alpha=0.6, color='#2ECC71', label='保護因子')
ax.plot(x, protective_counts, color='#27AE60', linewidth=2, marker='o', markersize=5)

# 繪製危險因子（根據是否高風險分別用紅色或黑線）
risk_label_added = False
for i in range(len(x) - 1):
    # 填充區域始終用淡色
    if i in high_risk_indices or (i + 1) in high_risk_indices:
        label = '危險因子' if not risk_label_added else None
        ax.fill_between([x[i], x[i+1]], protective_counts[i:i+2], risk_cumsum[i:i+2],
                        alpha=0.6, color='#E74C3C', label=label)
        risk_label_added = True
    else:
        ax.fill_between([x[i], x[i+1]], protective_counts[i:i+2], risk_cumsum[i:i+2],
                        alpha=0.3, color='#E74C3C')

# 線條：高風險用紅色，其他用黑線
for i in range(len(x)):
    if i in high_risk_indices:
        color = '#C0392B'  # 深紅
    else:
        color = '#34495E'  # 深灰

ax.plot(x, risk_cumsum, color='#95A5A6', linewidth=1.5, alpha=0.7, linestyle='-')

# 高風險區間標記已移除（只用填充區域區別）

# 找出 Day 的分界線位置
day_boundaries = []
for i in range(1, len(df_human)):
    if days[i] != days[i-1]:
        day_boundaries.append(i - 0.5)

# 用虛線標記 Day 分界
for boundary in day_boundaries:
    ax.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

# Day 背景色
day1_end = day_boundaries[0] if day_boundaries else len(df_human)
day2_end = day_boundaries[1] if len(day_boundaries) > 1 else len(df_human)

ax.axvspan(-0.5, day1_end, alpha=0.05, color='#FF6B6B')
ax.axvspan(day1_end, day2_end, alpha=0.05, color='#4ECDC4')
ax.axvspan(day2_end, len(df_human) - 0.5, alpha=0.05, color='#FFE66D')

# Day 標籤
if day_boundaries:
    y_max = max(risk_cumsum) * 0.95
    ax.text(day1_end/2, y_max, 'Day 1\n（週日）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax.text((day1_end + day2_end)/2, y_max, 'Day 2\n（週一）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax.text((day2_end + len(df_human))/2, y_max, 'Day 3\n（週二）', ha='center', fontsize=11, weight='bold', alpha=0.7)

# 標記高風險訊息
high_risk_df = df_human[df_human['cssrs_score'] >= 3]
for idx, row in high_risk_df.iterrows():
    msg_id = int(row['message_id'])
    total = protective_counts[idx] + risk_counts[idx]
    ax.scatter(idx, total, color='red', s=200, marker='*', zorder=5, edgecolors='darkred', linewidth=1)

    # #55 往左，#57 往右
    if msg_id == 55:
        x_offset = -9
    elif msg_id == 57:
        x_offset = 12
    else:
        x_offset = 0

    ax.annotate(f"#{msg_id}", xy=(idx, total), xytext=(x_offset, 10),
                textcoords='offset points', ha='center', fontsize=9,
                color='red', weight='bold')

# 設定軸標籤和標題
ax.set_xlabel('訊息序列', fontsize=12, weight='bold')
ax.set_ylabel('因子數量', fontsize=12, weight='bold')
ax.set_title('保護因子 vs 危險因子 時間序列分析 \n（高風險時刻 #55 #57）', fontsize=14, weight='bold', pad=20)

# 網格
ax.grid(True, alpha=0.3, linestyle=':')
ax.legend(loc='upper right', fontsize=11, framealpha=0.95)

# 設定 y 軸
ax.set_ylim(0, max(risk_cumsum) * 1.1)

plt.tight_layout()

# 儲存圖表
output_path = 'protective_risk_factors.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ 圖表已儲存至: {output_path}")

plt.show()
