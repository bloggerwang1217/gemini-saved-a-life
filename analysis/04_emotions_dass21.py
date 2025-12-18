#!/usr/bin/env python3
"""
DASS-21 三維度情緒分析（焦慮、抑鬱、壓力）
僅分析當事人訊息
用三張子圖分別呈現各維度
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# 設定中文字體
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# 讀取資料
df = pd.read_csv('../conversation_final.csv')

# 過濾只有 HUMAN 訊息
df_human = df[df['speaker'] == 'HUMAN'].copy()
df_human = df_human.reset_index(drop=True)

# 準備資料
x = np.arange(len(df_human))
dimensions = [
    ('dass_anxiety', '焦慮（Anxiety）', '#E74C3C'),
    ('dass_depression', '抑鬱（Depression）', '#3498DB'),
    ('dass_stress', '壓力（Stress）', '#F39C12')
]

# 提取資料
dimension_data = {}
for col, label, color in dimensions:
    dimension_data[col] = {
        'label': label,
        'color': color,
        'values': pd.to_numeric(df_human[col], errors='coerce').fillna(0).values
    }

# 找出 Day 的分界線位置
days = df_human['day'].values
day_boundaries = []
for i in range(1, len(df_human)):
    if days[i] != days[i-1]:
        day_boundaries.append(i - 0.5)

day1_end = day_boundaries[0] if day_boundaries else len(df_human)
day2_end = day_boundaries[1] if len(day_boundaries) > 1 else len(df_human)

# 創建三個子圖
fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)

severity_colors = {
    0: '#2ECC71',      # 無症狀 - 綠
    1: '#F1C40F',      # 輕微 - 黃
    2: '#E67E22',      # 中等 - 橙
    3: '#E74C3C',      # 嚴重 - 紅
    4: '#C0392B'       # 極其嚴重 - 深紅
}

# 繪製各維度
for idx, (col, label, color) in enumerate(dimensions):
    ax = axes[idx]
    values = dimension_data[col]['values']

    # 繪製嚴重度背景（垂直分區）
    for i in range(len(x) - 1):
        val = int(values[i])
        bg_color = severity_colors.get(val, '#95A5A6')
        ax.axvspan(i - 0.5, i + 0.5, alpha=0.2, color=bg_color, zorder=0)

    # 繪製線
    ax.plot(x, values,
            label=label,
            color=color,
            linewidth=3,
            marker='o',
            markersize=6,
            alpha=0.9,
            zorder=3)

    # 用虛線標記 Day 分界
    for boundary in day_boundaries:
        ax.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)

    # Day 背景色
    ax.axvspan(-0.5, day1_end, alpha=0.02, color='#FF6B6B', zorder=-1)
    ax.axvspan(day1_end, day2_end, alpha=0.02, color='#4ECDC4', zorder=-1)
    ax.axvspan(day2_end, len(df_human) - 0.5, alpha=0.02, color='#FFE66D', zorder=-1)

    # 設定軸標籤
    ax.set_ylabel(f'{label}\n嚴重度', fontsize=11, weight='bold')
    ax.set_ylim(-0.3, 4.3)
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_yticklabels(['0', '1', '2', '3', '4'])

    # 網格
    ax.grid(True, alpha=0.3, linestyle=':', axis='y')

    # Legend 放右邊中間
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=11, framealpha=0.95)

# 標記高風險訊息 #55, #57
high_risk_msgs = [55, 57]
for idx, row in df_human.iterrows():
    if int(row['message_id']) in high_risk_msgs:
        msg_id = int(row['message_id'])
        # 分開標籤位置
        x_offset = -8 if msg_id == 55 else 8

        for ax in axes:
            ax.scatter(idx, ax.get_ylim()[1] * 0.95, color='red', s=200, marker='*',
                      zorder=5, edgecolors='darkred', linewidth=1.5)
            ax.annotate(f"#{msg_id}", xy=(idx, ax.get_ylim()[1] * 0.95),
                       xytext=(x_offset, 18), textcoords='offset points', ha='center',
                       fontsize=9, color='red', weight='bold')

# Day 標籤（在上方圖表）
if day_boundaries:
    ax_top = axes[0]
    y_max = 4.4  # 往上調整
    ax_top.text(day1_end/2, y_max, 'Day 1\n（週日）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax_top.text((day1_end + day2_end)/2, y_max, 'Day 2\n（週一）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax_top.text((day2_end + len(df_human))/2, y_max, 'Day 3\n（週二）', ha='center', fontsize=11, weight='bold', alpha=0.7)

# 公共標籤
fig.text(0.5, 0.02, '訊息序列', ha='center', fontsize=12, weight='bold')
fig.suptitle('DASS-21 三維度情緒分析 時間序列\n（當事人訊息 / 高風險時刻 #55 #57）', fontsize=14, weight='bold', y=0.995)

# 設定緊湊佈局
plt.tight_layout()

# 儲存圖表
output_path = 'emotions_dass21.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 圖表已儲存至: {output_path}")

# 統計資訊
print("\n" + "="*70)
print("📊 DASS-21 三維度統計（當事人訊息）")
print("="*70)

for col, label, color in dimensions:
    values = dimension_data[col]['values']
    print(f"\n{label}:")
    print(f"  平均值: {values.mean():.2f}")
    print(f"  最大值: {values.max():.0f}")
    print(f"  最小值: {values.min():.0f}")
    print(f"  標準差: {values.std():.2f}")

    # 分級統計
    severe_count = (values >= 3).sum()
    moderate_count = ((values >= 2) & (values < 3)).sum()
    mild_count = ((values >= 1) & (values < 2)).sum()
    none_count = (values < 1).sum()

    print(f"  分級：無({none_count}) | 輕微({mild_count}) | 中等({moderate_count}) | 嚴重({severe_count})")
