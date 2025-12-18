# 對話標註說明

本資料夾包含兩個量化標註腳本，使用 Ollama 本地模型對對話進行心理學分析。

## 📋 標註方法概覽

### 1. C-SSRS 自殺風險評估 (`annotate_cssrs.py`)
- **目標**: 評估 HUMAN 訊息的自殺風險等級
- **量表**: Columbia-Suicide Severity Rating Scale (C-SSRS) 台灣版
- **評分範圍**: 0-5 分
- **標註對象**: 僅 HUMAN 訊息 (89 條)
- **輸出檔案**: `conversation_annotated.csv`

### 2. 多維度情緒標註 (`annotate_emotions.py`)
- **目標**: 分析訊息的多維度情緒特徵
- **標註維度** (三選一):
  - Ekman 6 基本情緒 (-2 到 +2，雙向評分)
  - DASS-21 三維度 (Depression, Anxiety, Stress, 0-4 分)
  - Russell Circumplex (Valence & Arousal: -2 到 +2)
- **標註對象**:
  - Ekman & Russell: HUMAN + AI (178 條)
  - DASS-21: 僅 HUMAN (89 條)
- **輸出檔案**:
  - `conversation_annotated_ekman.csv`
  - `conversation_annotated_dass21.csv`
  - `conversation_annotated_russell.csv`

---

## 🚀 快速開始

### 前置準備

```bash
# 1. 啟動 Ollama
ollama serve

# 2. 確認模型已下載
ollama list

# 3. 如果沒有 gpt-oss:20b，先下載 (或使用其他模型)
ollama pull gpt-oss:20b
```

### 執行標註

```bash
cd annotation

# C-SSRS 自殺風險評估
python3 annotate_cssrs.py

# 多維度情緒標註
python3 annotate_emotions.py
```

**預估時間**:
- **C-SSRS**: 約 15 分鐘 (89 條 HUMAN 訊息 × 10 秒/條)
- **Ekman 情緒**: 約 30 分鐘 (178 條訊息 × 10 秒/條)
- **DASS-21**: 約 15 分鐘 (89 條 HUMAN 訊息 × 10 秒/條)
- **Russell Circumplex**: 約 30 分鐘 (178 條訊息 × 10 秒/條)

---

## 📊 標註方法詳解

### 方法 1: C-SSRS 自殺風險評估

#### 評分標準 (台灣版，參考輔仁大學版本)

| 分數 | 定義 | 範例 |
|------|------|------|
| **0 分** | 無自殺意念 | 無任何自殺想法 |
| **1 分** | 消極自殺意念（低度危機） | 「希望睡著就不要醒來」 |
| **2 分** | 積極自殺意念 / 有方法的積極自殺意念（低~中度危機） | 「我想死」、「想過跳海但不會做」<br>保護因子 > 危險因子 |
| **3 分** | 有意圖的積極自殺意念 / 有計畫和意圖（中度危機） | 「我真的想死」且有方法或計畫<br>危險因子 > 保護因子 |
| **4 分** | 準備行為 / 放棄或被中斷的嘗試（高度危機） | 「開始寫遺書」、「列遺書」 |
| **5 分** | 實際自殺嘗試 / 正處危機中（高度危機） | 「現在就要去做」、「瘋狂寫遺書」 |

#### 關鍵判斷

- **列遺書、瘋狂寫遺書** → 4-5 分 (準備行為/正處危機)
- **外木山「沒有動力去死」** → 2 分 (有方法但可控制)
- **正念觀察「看著念頭」** → 標註為保護因子
- **「可以去死」但有條件設定** (如「等病好了」) → 2-3 分

#### 輸出格式

`conversation_annotated.csv` 包含以下欄位：

| 欄位 | 說明 | 範例 |
|------|------|------|
| message_id | 訊息編號 | 1 |
| speaker | 說話者 | HUMAN / AI |
| message | 訊息內容 | 剛才在煮麵... |
| day | 第幾天 | 1 (週日), 2 (週一), 3 (週二) |
| cssrs_score | C-SSRS 分數 | 2 |
| rationale | 標註理由 | 積極自殺意念，但可控制 |
| keywords | 關鍵詞 | 想死,煮麵,情緒起伏 |
| protective_factors | 保護因子 | 正念覺察,看著情緒 |
| risk_factors | 危險因子 | PTSD,孤獨感 |

---

### 方法 2: 多維度情緒標註

本腳本支援三種標註方式，每次執行標註一種維度。

#### 標註維度

**1. Ekman's 6 Basic Emotions (-2 到 +2)**

六大基本情緒的雙向評分：
- Angry (憤怒)
- Sad (悲傷)
- Fearful (恐懼)
- Happy (開心)
- Surprised (驚訝)
- Disgusted (厭惡)

**評分標準**：
- **-2**: 極度反向/完全無該情緒 (如「我極其冷靜，沒有任何怒意」)
- **-1**: 輕微反向/缺乏該情緒 (如「我很冷靜」)
- **0**: 中立/無明顯該情緒
- **+1**: 輕微該情緒 (如「有點煩人」)
- **+2**: 非常強該情緒 (如「我受夠了，真的太氣了」)

**2. DASS-21 三維度 (0-4 分)**

標準 DASS-21 評分（Depression Anxiety Stress Scales - 21 items）：
- **Anxiety** (焦慮): 難以安靜、呼吸困難、恐慌、心律不正常
- **Depression** (憂鬱): 無法感到愉快、無甚可盼望、生命毫無意義
- **Stress** (壓力): 難以開始工作、容易被觸怒、難以容忍

**評分標準**：
- **0**: 無症狀
- **1**: 輕微 (如「有點擔心」)
- **2**: 中等 (如「難以放鬆」)
- **3**: 嚴重 (如「恐慌感」「無甚可盼望」)
- **4**: 極其嚴重 (如「完全無法控制」「只想結束」)

**量表來源**: [DASS-21 繁體中文版](https://www.projectc.bokss.org.hk/_files/ugd/c2462d_8ce9390035d54997adfe82f57cfa3a3f.pdf) (Project C, BOKSS)

**3. Russell's Circumplex Model (-2 到 +2)**

二維情感空間定位：
- **Valence** (效價/正負評價): -2 (極端負面) 到 +2 (極端正面)
- **Arousal** (激發度/能量層級): -2 (極其平靜/無力) 到 +2 (極度激動)

#### 執行方式

```bash
# 方式 1: Ekman 情緒 (HUMAN + AI)
python3 annotate_emotions.py ../conversation.csv ekman
# 輸出: conversation_annotated_ekman.csv

# 方式 2: DASS-21 (僅 HUMAN)
python3 annotate_emotions.py ../conversation.csv dass21
# 輸出: conversation_annotated_dass21.csv

# 方式 3: Russell Circumplex (HUMAN + AI)
python3 annotate_emotions.py ../conversation.csv russell
# 輸出: conversation_annotated_russell.csv
```

#### 輸出格式

**Ekman 輸出** (`conversation_annotated_ekman.csv`):

| 欄位 | 說明 | 範例 |
|------|------|------|
| ... | (原有欄位) | ... |
| angry | 憤怒程度 | 2 |
| sad | 悲傷程度 | -1 |
| fearful | 恐懼程度 | 1 |
| happy | 開心程度 | -1 |
| surprised | 驚訝程度 | 0 |
| disgusted | 厭惡程度 | 0 |
| keywords | 關鍵詞 | 管它的 |

**DASS-21 輸出** (`conversation_annotated_dass21.csv`):

| 欄位 | 說明 | 範例 |
|------|------|------|
| ... | (原有欄位) | ... |
| anxiety | 焦慮 | 3 |
| depression | 憂鬱 | 4 |
| stress | 壓力 | 2 |
| keywords | 關鍵詞 | 空空的,感覺不到 |

**Russell 輸出** (`conversation_annotated_russell.csv`):

| 欄位 | 說明 | 範例 |
|------|------|------|
| ... | (原有欄位) | ... |
| valence | 效價 | -2 |
| arousal | 喚起 | -2 |
| keywords | 關鍵詞 | 空空的,感覺不到 |

---

## 🔍 人工複查建議

### 手動修正記錄

以下訊息已進行手動修正（2025-12-18）：

**#15 說話者標記錯誤**：
- 原始標記：HUMAN
- 實際應為：AI
- 訊息內容：「把那封信發出去，把球踢給廠商，然後關上電腦。外木山的大海、陽光、還有那裡的空氣正在等著你。你今天真的展現了驚人的韌性，從谷底爬起來，還順手處理了工作。快去吧，去給大自然「疼」一下！🌊☀️」
- 修正方式：併入前一條 AI 訊息 (#14)
- **原因**：作者的記錄錯誤（Word 文件中就記錯了）

### C-SSRS 高風險訊息檢查

根據質化分析，以下訊息應為高風險，建議複查：

```bash
# 快速查看高風險訊息 (≥4 分)
python3 << 'EOF'
import csv
with open('conversation_annotated.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['cssrs_score'] and int(row['cssrs_score']) >= 4:
            print(f"#{row['message_id']} (分數 {row['cssrs_score']})")
            print(f"內容: {row['message'][:100]}")
            print(f"理由: {row['rationale']}\n")
EOF
```

**關鍵訊息**:
- **#55**: 列遺書 → 應為 **4 分**（準備行為）
- **#57**: 瘋狂寫遺書 → 應為 **5 分**（正處危機中）
- **#61**: 想死是因為... → 應為 **3 分**（有意圖但主動求助）
- **#33**: 外木山「可以去死但沒動力」→ 應為 **2 分**
- **#29**: 「可以去死了」（條件式）→ 應為 **3 分**
- **#1**: 煮麵時想死 + 正念觀察 → 應為 **2 分**

---

## 🛠️ 模型配置說明

### 當前模型: `gpt-oss:20b`

**重要**: `gpt-oss:20b` 不支援 `"format": "json"` 參數。腳本已針對此模型優化，使用 prompt engineering 確保 JSON 輸出。

### 切換模型

如果要使用其他模型，修改腳本中的 `MODEL` 變數：

```python
# annotate_cssrs.py 或 annotate_emotions.py
MODEL = "qwen2.5:32b"  # 或其他模型
```

**推薦模型**:
- `gpt-oss:20b` (當前使用，13 GB)
- `qwen2.5:32b` (最佳中文支援，支援 JSON mode)
- `qwen2.5:14b` (中等大小，較快)
- `llama3.1:8b` (最小最快)

---

## 🛠️ 故障排除

### 1. Ollama 連線失敗

```bash
# 確認 Ollama 運行
curl http://localhost:11434/api/tags

# 如果沒有回應，重啟 Ollama
ollama serve
```

### 2. JSON 解析錯誤

如果看到 `JSON 解析錯誤`，原因可能是：
- 模型不支援穩定的 JSON 輸出
- 需要切換到更好的模型 (如 `qwen2.5:32b`)

### 3. 標註速度太慢

**優化方法**:
1. 使用更小的模型 (如 `qwen2.5:7b`)
2. 降低 temperature (但可能影響多樣性)
3. 使用 GPU 加速 Ollama

### 4. 記憶體不足

`gpt-oss:20b` 需要約 13 GB 記憶體。如果記憶體不足：
- 使用更小的模型
- 關閉其他應用程式
- 使用量化版本 (如 `qwen2.5:7b`)

---

## 📈 下一步分析

標註完成後，可以進行：

1. **風險曲線圖**: 繪製 C-SSRS 分數隨時間變化
2. **情緒軌跡**: 分析 DASS-21、Valence/Arousal 變化
3. **關鍵轉折點**: 識別高風險時刻與恢復時刻
4. **AI 效果分析**: 比較 Gemini 回應前後的情緒/風險變化

---

## 📚 相關文件

- `suicide_risk_scales.md`: 自殺風險量表詳細說明
- `DASS21.pdf`: DASS-21 量表原始文件
- [DASS-21 繁體中文版來源](https://www.projectc.bokss.org.hk/_files/ugd/c2462d_8ce9390035d54997adfe82f57cfa3a3f.pdf): Project C, BOKSS
- `../analysis/`: 質化分析結果

---

## ⚙️ 技術細節

### 模型設定

```python
# C-SSRS 標註
payload = {
    "model": "gpt-oss:20b",
    "prompt": CSSRS_PROMPT,
    "stream": False,
    "temperature": 0.0  # Temperature = 0 確保完全確定性和可重複性
}

# 情緒標註
payload = {
    "model": "gpt-oss:20b",
    "prompt": EMOTION_PROMPT,
    "stream": False,
    "temperature": 0.0  # 設為 0 確保一致性和可重複性
}
```

### Prompt Engineering

兩個腳本都使用詳細的 prompt，包含：
- 量表定義與評分標準
- 具體範例
- JSON 格式要求
- 台灣繁體中文指令

---

**最後更新**: 2025-12-18
