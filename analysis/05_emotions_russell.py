#!/usr/bin/env python3
"""
Russell Circumplex Model 時間序列分析
二維情感空間：Valence（效價）vs Arousal（激發度）
分成上下兩張子圖
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
valence = pd.to_numeric(df_human['russell_valence'], errors='coerce').fillna(0).values
arousal = pd.to_numeric(df_human['russell_arousal'], errors='coerce').fillna(0).values

# 找出 Day 的分界線位置
days = df_human['day'].values
day_boundaries = []
for i in range(1, len(df_human)):
    if days[i] != days[i-1]:
        day_boundaries.append(i - 0.5)

day1_end = day_boundaries[0] if day_boundaries else len(df_human)
day2_end = day_boundaries[1] if len(day_boundaries) > 1 else len(df_human)

# 創建兩個子圖
fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

# ===== Valence 圖 =====
ax_valence = axes[0]

# 繪製 Valence（實線）
ax_valence.plot(x, valence,
                label='Valence（效價/正負評價）',
                color='#3498DB',
                linewidth=3,
                marker='o',
                markersize=5,
                linestyle='-',
                alpha=0.9)

# 網格背景（區分正負）
ax_valence.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.7)
ax_valence.fill_between(x, -2.5, 0, alpha=0.05, color='#E74C3C')
ax_valence.fill_between(x, 0, 2.5, alpha=0.05, color='#2ECC71')

# Day 分界
for boundary in day_boundaries:
    ax_valence.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

ax_valence.axvspan(-0.5, day1_end, alpha=0.02, color='#FF6B6B')
ax_valence.axvspan(day1_end, day2_end, alpha=0.02, color='#4ECDC4')
ax_valence.axvspan(day2_end, len(df_human) - 0.5, alpha=0.02, color='#FFE66D')

ax_valence.set_ylabel('Valence\n（效價/正負評價）', fontsize=11, weight='bold')
ax_valence.set_ylim(-2.3, 2.3)
ax_valence.set_yticks([-2, -1, 0, 1, 2])
ax_valence.set_yticklabels(['極負\n(-2)', '負面\n(-1)', '中立\n(0)', '正面\n(+1)', '極正\n(+2)'])
ax_valence.grid(True, alpha=0.3, linestyle=':', axis='y')
ax_valence.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=11, framealpha=0.95)

# ===== Arousal 圖 =====
ax_arousal = axes[1]

# 繪製 Arousal（虛線）
ax_arousal.plot(x, arousal,
                label='Arousal（激發度/能量層級）',
                color='#E74C3C',
                linewidth=3,
                marker='s',
                markersize=5,
                linestyle='--',
                alpha=0.9)

# 網格背景（區分高低能量）
ax_arousal.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.7)
ax_arousal.fill_between(x, -2.5, 0, alpha=0.05, color='#9B59B6')
ax_arousal.fill_between(x, 0, 2.5, alpha=0.05, color='#F39C12')

# Day 分界
for boundary in day_boundaries:
    ax_arousal.axvline(x=boundary, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

ax_arousal.axvspan(-0.5, day1_end, alpha=0.02, color='#FF6B6B')
ax_arousal.axvspan(day1_end, day2_end, alpha=0.02, color='#4ECDC4')
ax_arousal.axvspan(day2_end, len(df_human) - 0.5, alpha=0.02, color='#FFE66D')

ax_arousal.set_ylabel('Arousal\n（激發度/能量層級）', fontsize=11, weight='bold')
ax_arousal.set_ylim(-2.3, 2.3)
ax_arousal.set_yticks([-2, -1, 0, 1, 2])
ax_arousal.set_yticklabels(['極無力\n(-2)', '平靜\n(-1)', '中等\n(0)', '興奮\n(+1)', '極亢奮\n(+2)'])
ax_arousal.grid(True, alpha=0.3, linestyle=':', axis='y')
ax_arousal.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=11, framealpha=0.95)

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
    ax_top = axes[0]
    y_max = 2.15  # 往上調整
    ax_top.text(day1_end/2, y_max, 'Day 1\n（週日）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax_top.text((day1_end + day2_end)/2, y_max, 'Day 2\n（週一）', ha='center', fontsize=11, weight='bold', alpha=0.7)
    ax_top.text((day2_end + len(df_human))/2, y_max, 'Day 3\n（週二）', ha='center', fontsize=11, weight='bold', alpha=0.7)

# 公共標籤
fig.text(0.5, 0.02, '訊息序列', ha='center', fontsize=12, weight='bold')
fig.suptitle('Russell Circumplex Model 時間序列分析\n（當事人訊息 / 高風險時刻 #55 #57）',
             fontsize=14, weight='bold', y=0.995)

# 設定緊湊佈局
plt.tight_layout()

# 儲存圖表
output_path = 'emotions_russell.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 圖表已儲存至: {output_path}")

# 統計資訊
print("\n" + "="*70)
print("📊 Russell Circumplex 統計（當事人訊息）")
print("="*70)

print(f"\nValence（效價/正負評價）:")
print(f"  平均值: {valence.mean():.2f}")
print(f"  最大值: {valence.max():.0f}")
print(f"  最小值: {valence.min():.0f}")
print(f"  標準差: {valence.std():.2f}")

print(f"\nArousal（激發度/能量層級）:")
print(f"  平均值: {arousal.mean():.2f}")
print(f"  最大值: {arousal.max():.0f}")
print(f"  最小值: {arousal.min():.0f}")
print(f"  標準差: {arousal.std():.2f}")

# 象限分類
print(f"\n四象限情感分佈:")
high_val_high_arous = ((valence > 0) & (arousal > 0)).sum()
high_val_low_arous = ((valence > 0) & (arousal <= 0)).sum()
low_val_high_arous = ((valence <= 0) & (arousal > 0)).sum()
low_val_low_arous = ((valence <= 0) & (arousal <= 0)).sum()

print(f"  右上（興奮/正面激動）: {high_val_high_arous} 條")
print(f"  右下（放鬆/正面平靜）: {high_val_low_arous} 條")
print(f"  左上（焦慮/負面激動）: {low_val_high_arous} 條")
print(f"  左下（沮喪/負面平靜）: {low_val_low_arous} 條")

# Correlation (手動計算)
corr = np.corrcoef(valence, arousal)[0, 1]
print(f"\nValence 與 Arousal 相關性:")
print(f"  相關係數: {corr:.3f}")
if abs(corr) > 0.5:
    print(f"  解讀: 中強相關")
elif abs(corr) > 0.3:
    print(f"  解讀: 弱相關")
else:
    print(f"  解讀: 無明顯相關")
