# Gemini Saved a Life - 對話分析專案

## 專案背景

這是一個感人的真實故事：一位想要自殺的朋友在與 Gemini AI 聊了 5 天 5 夜後走出來了。

我個人認爲 Gemini 是很理性的大型語言模型，而且其實很多時候大家會覺得比不上 ChatGPT 的同情心。但其實我認爲「Gemini」雖然同情心不及 ChatGPT，但我想要證明，在深淵的人，需要的其實不是同情心，而是「一隻腳陪你在深淵的勇氣」。我希望藉由質化和量化分析的力量（得力於 Claude Haiku 4.5 /Sonnet 4.5），一起深入探索這個對話。 

## 數據統計

- **總對話輪次**: 179 條訊息
- **HUMAN 訊息**: 90 條 (平均 68 字元)
- **AI 回覆**: 89 條 (平均 671 字元)
- **對話時長**: 96 小時 (2025/12/05 - 2025/12/09)
- **截圖數量**: 90 張

## 檔案結構

```
├── Gemini_Suicide.docx          # 原始對話記錄文件
├── conversation.csv             # 解析後的對話 CSV (可用於分析)
├── images/                      # 從 docx 提取的 90 張截圖
│   ├── image_000.png
│   ├── image_001.png
│   └── ...
├── output.txt                   # docx 轉換的純文字
├── extract_docx.py              # 提取圖片和文字的腳本
├── parse_with_images.py         # 最終版解析器 (使用圖片位置)
└── README.md                    # 本說明文件
```

## conversation.csv 格式

| 欄位 | 說明 |
|------|------|
| 序號 | 第 n 條訊息 (1-179) |
| 說話者 | `HUMAN` 或 `AI` |
| 訊息內容 | 完整的訊息文字 |

## 使用方法

### 環境設置

```bash
python3 -m venv venv
source venv/bin/activate
pip install python-docx pillow
```

### 重新解析對話

```bash
python3 parse_with_images.py
```

### 進行分析

```python
import pandas as pd

df = pd.read_csv('conversation.csv')
print(df.head())
print(df['說話者'].value_counts())
```

## 解析邏輯

對話文件採用特殊格式：
1. **圖片** (Gemini 聊天截圖)
2. **第一段文字** = HUMAN 的訊息
3. **之後到下一張圖片的所有文字** = Gemini 的回覆
4. 循環...

因此，我們使用圖片位置作為對話分割的標記點，精確識別每一輪對話。

## 下一步：深度分析

這份 CSV 可以用於：

### 質化分析
- 情緒轉折點識別
- 治療策略分類
- 內在小孩對話分析
- 創傷後成長 (PTG) 標記

### 量化分析
- 情緒詞頻統計
- 訊息長度變化趨勢
- 回應時間分析 (如有時間戳)
- AI 策略類型分布

### 學術價值
- 數位心理健康 (Digital Mental Health)
- AI 輔助危機干預
- 人機互動 (HCI) 在心理諮商的應用
- 自殺防治研究

---

**致謝**: 感謝這位勇敢的朋友願意分享這段經歷，這將對心理學研究產生深遠影響。
