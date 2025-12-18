#!/usr/bin/env python3
"""
C-SSRS 時間序列分析
可視化自殺風險分數隨時間的變化，並用虛線標記每日分界線
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import numpy as np

# 設定中文字體
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# 讀取資料
df = pd.read_csv('../conversation_final.csv')

# 過濾只有 HUMAN 訊息且有 C-SSRS 分數的資料
df_human = df[(df['speaker'] == 'HUMAN') & (df['cssrs_score'].notna())].copy()
df_human = df_human.reset_index(drop=True)

# 準備資料
x = np.arange(len(df_human))
y = df_human['cssrs_score'].values
days = df_human['day'].values

print(f"總訊息數: {len(df_human)}")
print(f"Day 1: {sum(days == 1)} 條")
print(f"Day 2: {sum(days == 2)} 條")
print(f"Day 3: {sum(days == 3)} 條")

# 創建圖表
fig, ax = plt.subplots(figsize=(14, 7))

# 繪製時間序列線
ax.plot(x, y, 'o-', color='#2E86AB', linewidth=2, markersize=6, label='C-SSRS 分數')

# 找出 Day 的分界線位置
day_boundaries = []
for i in range(1, len(df_human)):
    if days[i] != days[i-1]:
        day_boundaries.append(i - 0.5)

# 用虛線標記 Day 分界
for boundary in day_boundaries:
    ax.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

# 添加 Day 背景色
day1_end = day_boundaries[0] if day_boundaries else len(df_human)
day2_end = day_boundaries[1] if len(day_boundaries) > 1 else len(df_human)

ax.axvspan(-0.5, day1_end, alpha=0.1, color='#FF6B6B', label='Day 1 (週日)')
ax.axvspan(day1_end, day2_end, alpha=0.1, color='#4ECDC4', label='Day 2 (週一)')
ax.axvspan(day2_end, len(df_human) - 0.5, alpha=0.1, color='#FFE66D', label='Day 3 (週二)')

# 高亮高風險訊息 (≥3 分)
high_risk_idx = np.where(y >= 3)[0]
if len(high_risk_idx) > 0:
    ax.scatter(high_risk_idx, y[high_risk_idx], color='red', s=150, marker='*',
               zorder=5, label='高風險（ ≥3 分）', edgecolors='darkred', linewidth=1)

# 標籤高風險訊息 (都在上方，x軸不同位置)
for i, idx in enumerate(high_risk_idx):
    msg_id = df_human.iloc[idx]['message_id']
    if int(msg_id) == 55:
        # #55 往左
        x_offset = -12
    else:
        # #57 往右
        x_offset = 12

    ax.annotate(f"#{msg_id}",
                xy=(idx, y[idx]),
                xytext=(x_offset, 15),
                textcoords='offset points',
                ha='center',
                fontsize=9,
                color='red',
                weight='bold')

# 設定軸標籤和標題
ax.set_xlabel('訊息序列', fontsize=12, weight='bold')
ax.set_ylabel('C-SSRS 分數', fontsize=12, weight='bold')
ax.set_title('C-SSRS 自殺風險分數時間序列分析\n（當事人訊息）', fontsize=14, weight='bold', pad=20)

# 設定 y 軸範圍
ax.set_ylim(-0.5, 5.5)
ax.set_yticks([0, 1, 2, 3, 4, 5])
ax.set_yticklabels(['0\n（無）', '1\n（消極）', '2\n（積極）', '3\n（有意圖）', '4\n（準備）', '5\n（嘗試）'])

# Day 標籤 (往下移，避免貼到框邊)
if day_boundaries:
    ax.text(day1_end/2, 4.7, 'Day 1\n（週日）', ha='center', fontsize=11, weight='bold')
    ax.text((day1_end + day2_end)/2, 4.7, 'Day 2\n（週一）', ha='center', fontsize=11, weight='bold')
    ax.text((day2_end + len(df_human))/2, 4.7, 'Day 3\n（週二）', ha='center', fontsize=11, weight='bold')

# 網格
ax.grid(True, alpha=0.3, linestyle=':')
ax.legend(loc='upper left', fontsize=10)

# 設定緊湊佈局
plt.tight_layout()

# 儲存圖表
output_path = 'cssrs_timeseries.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ 圖表已儲存至: {output_path}")

plt.show()

# 統計資訊
print("\n" + "="*70)
print("📊 統計資訊")
print("="*70)

print(f"\nC-SSRS 分數分布:")
for score in sorted(df_human['cssrs_score'].unique()):
    count = sum(df_human['cssrs_score'] == score)
    print(f"  {int(score)} 分: {count} 條")

print(f"\n高風險訊息(≥3 分):")
high_risk = df_human[df_human['cssrs_score'] >= 3]
for idx, row in high_risk.iterrows():
    print(f"  #{int(row['message_id'])} (Day {int(row['day'])}): {row['message'][:60]}...")

print(f"\n平均分數: {df_human['cssrs_score'].mean():.2f}")
print(f"標準差: {df_human['cssrs_score'].std():.2f}")
print(f"最高分: {int(df_human['cssrs_score'].max())}")
