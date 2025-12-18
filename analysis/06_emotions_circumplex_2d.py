#!/usr/bin/env python3
"""
Russell Circumplex 2D 散點圖
在二維情感空間中視覺化情緒分佈
X軸: Valence（效價/正負評價）
Y軸: Arousal（激發度/能量層級）
顏色: 按時間序列漸層（早→後）
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib.cm as cm

# 設定中文字體
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# 讀取資料
df = pd.read_csv('../conversation_final.csv')

# 過濾只有 HUMAN 訊息
df_human = df[df['speaker'] == 'HUMAN'].copy()
df_human = df_human.reset_index(drop=True)

# 準備資料
valence = pd.to_numeric(df_human['russell_valence'], errors='coerce').fillna(0).values
arousal = pd.to_numeric(df_human['russell_arousal'], errors='coerce').fillna(0).values
message_id = df_human['message_id'].values
cssrs = pd.to_numeric(df_human['cssrs_score'], errors='coerce').fillna(0).values

# 創建時間序列顏色漸層（0-1 之間）
time_gradient = np.linspace(0, 1, len(df_human))
colors = cm.RdYlGn(time_gradient)

# 創建圖表
fig, ax = plt.subplots(figsize=(14, 12))

# 繪製四象限背景
ax.axhline(y=0, color='gray', linestyle='-', linewidth=2, alpha=0.7)
ax.axvline(x=0, color='gray', linestyle='-', linewidth=2, alpha=0.7)

# 象限標籤和背景色
ax.text(1.5, 1.5, '興奮\n(Excited)', ha='center', va='center',
        fontsize=12, weight='bold', alpha=0.3, color='green')
ax.text(-1.5, 1.5, '焦慮\n(Anxious)', ha='center', va='center',
        fontsize=12, weight='bold', alpha=0.3, color='red')
ax.text(-1.5, -1.5, '沮喪\n(Depressed)', ha='center', va='center',
        fontsize=12, weight='bold', alpha=0.3, color='purple')
ax.text(1.5, -1.5, '放鬆\n(Relaxed)', ha='center', va='center',
        fontsize=12, weight='bold', alpha=0.3, color='blue')

# 背景填充
ax.fill_between([-2, 2], 0, 2, alpha=0.05, color='green')
ax.fill_between([-2, 0], 0, 2, alpha=0.05, color='red')
ax.fill_between([-2, 0], -2, 0, alpha=0.05, color='purple')
ax.fill_between([0, 2], -2, 0, alpha=0.05, color='blue')

# 繪製散點（按時間漸層著色）
scatter = ax.scatter(valence, arousal,
                     c=time_gradient,
                     cmap='RdYlGn',
                     s=100,
                     alpha=0.7,
                     edgecolors='black',
                     linewidth=1,
                     marker='o',
                     label='各訊息的情感狀態（時間漸層著色）')

# 繪製軌跡線（連接時間序列）
for i in range(len(df_human) - 1):
    ax.plot([valence[i], valence[i+1]],
            [arousal[i], arousal[i+1]],
            color='gray',
            alpha=0.3,
            linewidth=1,
            zorder=0)

# 標記高風險訊息（C-SSRS >= 3）
high_risk_idx = np.where(cssrs >= 3)[0]
if len(high_risk_idx) > 0:
    ax.scatter(valence[high_risk_idx], arousal[high_risk_idx],
              s=400,
              marker='*',
              color='red',
              edgecolors='darkred',
              linewidth=2,
              zorder=5,
              label='高風險訊息（C-SSRS ≥ 3）')

# 標籤高風險訊息編號
for idx in high_risk_idx:
    ax.annotate(f"#{int(message_id[idx])}",
               xy=(valence[idx], arousal[idx]),
               xytext=(10, 10),
               textcoords='offset points',
               fontsize=9,
               weight='bold',
               color='red',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

# 標籤起點和終點
ax.scatter(valence[0], arousal[0], s=200, marker='o', color='green',
          edgecolors='darkgreen', linewidth=2, zorder=6, label='起點')
ax.scatter(valence[-1], arousal[-1], s=200, marker='s', color='blue',
          edgecolors='darkblue', linewidth=2, zorder=6, label='終點')

ax.annotate(f"#1 開始", xy=(valence[0], arousal[0]), xytext=(10, -15),
           textcoords='offset points', fontsize=9, color='green', weight='bold')
ax.annotate(f"#{int(message_id[-1])} 結束", xy=(valence[-1], arousal[-1]),
           xytext=(10, 10), textcoords='offset points', fontsize=9,
           color='blue', weight='bold')

# 設定軸標籤和標題
ax.set_xlabel('Valence（效價/正負評價）', fontsize=13, weight='bold')
ax.set_ylabel('Arousal（激發度/能量層級）', fontsize=13, weight='bold')
ax.set_title('Russell Circumplex Model 二維情感空間\n（當事人訊息），時間序列漸層著色（紅→綠）\n\n右上=興奮 | 右下=放鬆 | 左上=焦慮 | 左下=沮喪',
             fontsize=12, weight='bold', pad=20)

# 設定軸範圍和刻度
ax.set_xlim(-2.3, 2.3)
ax.set_ylim(-2.3, 2.3)
ax.set_xticks([-2, -1, 0, 1, 2])
ax.set_yticks([-2, -1, 0, 1, 2])
ax.set_xticklabels(['極負\n(-2)', '負面\n(-1)', '中立\n(0)', '正面\n(+1)', '極正\n(+2)'])
ax.set_yticklabels(['極無力\n(-2)', '平靜\n(-1)', '中等\n(0)', '興奮\n(+1)', '極亢奮\n(+2)'])

# 網格
ax.grid(True, alpha=0.3, linestyle=':')

# 顏色條
cbar = plt.colorbar(scatter, ax=ax, label='時間進度（早→晚）')
cbar.set_ticks([0, 0.5, 1])
cbar.set_ticklabels(['訊息 #1\n（早）', '訊息 #45\n（中）', '訊息 #89\n（晚）'])

# Legend 放右上角，增加行間距
legend = ax.legend(loc='upper right', fontsize=10, framealpha=0.95,
                   labelspacing=0.8,      # 項目間距
                   handletextpad=1.2,     # 圖示和文字間距
                   handlelength=1.5)      # 圖示長度
legend.set_title('圖例說明', prop={'size': 11, 'weight': 'bold'})

# 等寬佈局
ax.set_aspect('equal', adjustable='box')
plt.tight_layout()

# 儲存圖表
output_path = 'emotions_circumplex_2d.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 圖表已儲存至: {output_path}")

# 統計資訊
print("\n" + "="*70)
print("📊 Russell Circumplex 2D 情感空間統計")
print("="*70)

print(f"\n四象限情感分佈:")
high_val_high_arous = ((valence > 0) & (arousal > 0)).sum()
high_val_low_arous = ((valence > 0) & (arousal <= 0)).sum()
low_val_high_arous = ((valence <= 0) & (arousal > 0)).sum()
low_val_low_arous = ((valence <= 0) & (arousal <= 0)).sum()

print(f"  右上（興奮/正面激動）: {high_val_high_arous} 條 訊息")
print(f"  右下（放鬆/正面平靜）: {high_val_low_arous} 條 訊息")
print(f"  左上（焦慮/負面激動）: {low_val_high_arous} 條 訊息")
print(f"  左下（沮喪/負面平靜）: {low_val_low_arous} 條 訊息")

print(f"\n位置軌跡:")
print(f"  開始位置 (#1): Valence={valence[0]:.0f}, Arousal={arousal[0]:.0f}")
print(f"  結束位置 (#{int(message_id[-1])}): Valence={valence[-1]:.0f}, Arousal={arousal[-1]:.0f}")

# 計算平均位移
valence_shift = valence[-1] - valence[0]
arousal_shift = arousal[-1] - arousal[0]
print(f"  整體變化: Valence {valence_shift:+.1f}, Arousal {arousal_shift:+.1f}")

if len(high_risk_idx) > 0:
    print(f"\n高風險訊息位置:")
    for idx in high_risk_idx:
        print(f"  #{int(message_id[idx])}: Valence={valence[idx]:.0f}, Arousal={arousal[idx]:.0f}")
