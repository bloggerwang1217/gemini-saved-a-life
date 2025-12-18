#!/usr/bin/env python3
"""
Ekman 6 基本情緒時間序列分析
上方：悲傷、開心
中間：恐懼、生氣
下方：驚訝、厭惡
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
emotions_top = {
    'ekman_sad': ('悲傷', '#3498DB', '-'),
    'ekman_happy': ('開心', '#2ECC71', '-')
}

emotions_middle = {
    'ekman_fearful': ('恐懼', '#9B59B6', '-'),
    'ekman_angry': ('生氣', '#E74C3C', '-')
}

emotions_bottom = {
    'ekman_surprised': ('驚訝', '#F39C12', '-'),
    'ekman_disgusted': ('厭惡', '#1ABC9C', '-')
}

# 提取情緒資料
emotion_data = {}
for col, (label, color, linestyle) in {**emotions_top, **emotions_middle, **emotions_bottom}.items():
    emotion_data[col] = {
        'label': label,
        'color': color,
        'linestyle': linestyle,
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

# ===== Top 圖（悲傷、開心）=====
ax_top = axes[0]

# 繪製情緒線
for col, (label, color, linestyle) in emotions_top.items():
    ax_top.plot(x, emotion_data[col]['values'],
                label=label,
                color=color,
                linestyle=linestyle,
                linewidth=2.5,
                marker='o',
                markersize=4,
                alpha=0.8)

# 網格背景
ax_top.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
ax_top.fill_between(x, -2.5, 0, alpha=0.05, color='red')
ax_top.fill_between(x, 0, 2.5, alpha=0.05, color='green')

# Day 分界
for boundary in day_boundaries:
    ax_top.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

ax_top.axvspan(-0.5, day1_end, alpha=0.02, color='#FF6B6B')
ax_top.axvspan(day1_end, day2_end, alpha=0.02, color='#4ECDC4')
ax_top.axvspan(day2_end, len(df_human) - 0.5, alpha=0.02, color='#FFE66D')

ax_top.set_ylabel('情緒強度', fontsize=11, weight='bold')
ax_top.set_ylim(-2.3, 2.3)
ax_top.set_yticks([-2, -1, 0, 1, 2])
ax_top.set_yticklabels(['極反\n(-2)', '輕反\n(-1)', '中立\n(0)', '輕微\n(+1)', '強\n(+2)'])
ax_top.grid(True, alpha=0.3, linestyle=':')
ax_top.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=11, framealpha=0.95)

# ===== Middle 圖（恐懼、生氣）=====
ax_middle = axes[1]

# 繪製情緒線
for col, (label, color, linestyle) in emotions_middle.items():
    ax_middle.plot(x, emotion_data[col]['values'],
                   label=label,
                   color=color,
                   linestyle=linestyle,
                   linewidth=2.5,
                   marker='o',
                   markersize=4,
                   alpha=0.8)

# 網格背景
ax_middle.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
ax_middle.fill_between(x, -2.5, 0, alpha=0.05, color='red')
ax_middle.fill_between(x, 0, 2.5, alpha=0.05, color='green')

# Day 分界
for boundary in day_boundaries:
    ax_middle.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

ax_middle.axvspan(-0.5, day1_end, alpha=0.02, color='#FF6B6B')
ax_middle.axvspan(day1_end, day2_end, alpha=0.02, color='#4ECDC4')
ax_middle.axvspan(day2_end, len(df_human) - 0.5, alpha=0.02, color='#FFE66D')

ax_middle.set_ylabel('情緒強度', fontsize=11, weight='bold')
ax_middle.set_ylim(-2.3, 2.3)
ax_middle.set_yticks([-2, -1, 0, 1, 2])
ax_middle.set_yticklabels(['極反\n(-2)', '輕反\n(-1)', '中立\n(0)', '輕微\n(+1)', '強\n(+2)'])
ax_middle.grid(True, alpha=0.3, linestyle=':')
ax_middle.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=11, framealpha=0.95)

# ===== Bottom 圖（驚訝、厭惡）=====
ax_bottom = axes[2]

# 繪製情緒線
for col, (label, color, linestyle) in emotions_bottom.items():
    ax_bottom.plot(x, emotion_data[col]['values'],
                   label=label,
                   color=color,
                   linestyle=linestyle,
                   linewidth=2.5,
                   marker='o',
                   markersize=4,
                   alpha=0.8)

# 網格背景
ax_bottom.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
ax_bottom.fill_between(x, -2.5, 0, alpha=0.05, color='red')
ax_bottom.fill_between(x, 0, 2.5, alpha=0.05, color='green')

# Day 分界
for boundary in day_boundaries:
    ax_bottom.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

ax_bottom.axvspan(-0.5, day1_end, alpha=0.02, color='#FF6B6B')
ax_bottom.axvspan(day1_end, day2_end, alpha=0.02, color='#4ECDC4')
ax_bottom.axvspan(day2_end, len(df_human) - 0.5, alpha=0.02, color='#FFE66D')

ax_bottom.set_xlabel('訊息序列', fontsize=11, weight='bold')
ax_bottom.set_ylabel('情緒強度', fontsize=11, weight='bold')
ax_bottom.set_ylim(-2.3, 2.3)
ax_bottom.set_yticks([-2, -1, 0, 1, 2])
ax_bottom.set_yticklabels(['極反\n(-2)', '輕反\n(-1)', '中立\n(0)', '輕微\n(+1)', '強\n(+2)'])
ax_bottom.grid(True, alpha=0.3, linestyle=':')
ax_bottom.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=11, framealpha=0.95)

# 標記高風險訊息 #55, #57
high_risk_msgs = [55, 57]
for idx, row in df_human.iterrows():
    if int(row['message_id']) in high_risk_msgs:
        msg_id = int(row['message_id'])
        x_offset = -8 if msg_id == 55 else 8

        for ax in axes:
            ax.scatter(idx, ax.get_ylim()[1] * 0.95, color='red', s=200, marker='*',
                      zorder=5, edgecolors='darkred', linewidth=1.5)
            ax.annotate(f"#{msg_id}", xy=(idx, ax.get_ylim()[1] * 0.95),
                       xytext=(x_offset, 18), textcoords='offset points', ha='center',
                       fontsize=9, color='red', weight='bold')

# Day 標籤（在上方圖表）
if day_boundaries:
    ax_top_day = axes[0]
    y_max = 2.35
    ax_top_day.text(day1_end/2, y_max, 'Day 1\n（週日）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax_top_day.text((day1_end + day2_end)/2, y_max, 'Day 2\n（週一）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax_top_day.text((day2_end + len(df_human))/2, y_max, 'Day 3\n（週二）', ha='center', fontsize=11, weight='bold', alpha=0.7)

# 標記唯一一次生氣的時刻 #11（sanity check）
for idx, row in df_human.iterrows():
    if int(row['message_id']) == 11:
        ax_middle = axes[1]
        ax_middle.scatter(idx, emotion_data['ekman_angry']['values'][idx],
                         color='black', s=300, marker='D', edgecolors='black',
                         linewidth=2, zorder=6, label='唯一生氣點 (#11)')
        ax_middle.annotate('管他的\n(唯一生氣)', xy=(idx, emotion_data['ekman_angry']['values'][idx]),
                          xytext=(0, -30), textcoords='offset points', ha='center',
                          fontsize=9, color='black', weight='bold',
                          bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8),
                          arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

# 公共標籤
fig.suptitle('Ekman 6 基本情緒 時間序列分析\n（當事人訊息 / 高風險時刻 #55 #57）',
             fontsize=14, weight='bold', y=0.995)

# 設定緊湊佈局
plt.tight_layout()

# 儲存圖表
output_path = 'emotions_ekman.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 圖表已儲存至: {output_path}")

# 統計資訊
print("\n" + "="*70)
print("📊 Ekman 6 基本情緒統計")
print("="*70)

all_emotions = {**emotions_top, **emotions_middle, **emotions_bottom}
for col, (label, color, linestyle) in all_emotions.items():
    values = emotion_data[col]['values']
    print(f"\n{label}:")
    print(f"  平均值: {values.mean():.2f}")
    print(f"  最大值: {values.max():.0f}")
    print(f"  最小值: {values.min():.0f}")
    print(f"  標準差: {values.std():.2f}")
