# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個心理學研究專案,分析一段為期 3 天的 Gemini AI 與自殺意念者的真實對話。專案目標是透過質化與量化分析,探討 AI 的「理性陪伴」在危機干預中的作用。

**核心研究問題**: 深淵中的人需要的不是同情心,而是「一隻腳陪你在深淵的勇氣」。

## 資料結構

### 原始資料
- `Gemini_Suicide.docx` / `.pdf`: 原始對話記錄 (178 條訊息, 89 張截圖)
- `images/`: 按段落順序提取的聊天截圖 (89 張)
  - **重要**: `image_005.jpg` 是 YouTube 縮圖,非聊天截圖,已在解析時排除

### 處理後資料
- `conversation.csv`: 核心資料檔案
  - 欄位: `序號`, `說話者` (HUMAN/AI), `訊息內容`, `Day` (1=週日, 2=週一, 3=週二)
  - 178 條訊息 (89 HUMAN + 89 AI)
  - 已修正多段落 HUMAN 訊息誤判問題

### 分析結果
- `analysis/`: 質化分析 markdown 文件
  - `crisis_moments.md`: 危機時刻時間線
  - `timeline_analysis.md`: 時間線驗證
  - `waimushan_analysis.md`: 外木山事件心理分析
- `annotation/`: 量化標註 (使用 Ollama 本地模型)

## 工作流程

### 資料前處理管道

```bash
# 1. 啟動虛擬環境
source venv/bin/activate

# 2. 提取圖片 (按段落順序)
cd preprocessing
python3 extract_images.py

# 3. 解析對話 (自動排除 YouTube 縮圖)
python3 parse_with_images.py

# 4. 修正多段落訊息
python3 manual_fixes.py

# 5. 新增 Day 欄位
cd ../annotation
python3 add_day_column.py
```

**輸出**: `conversation.csv` (根目錄)

### 量化標註 (Ollama)

需要先確保 Ollama 服務運行:

```bash
# 啟動 Ollama
ollama serve

# 確認模型
ollama list  # 應包含 gpt-oss:20b 或 qwen2.5:32b
```

標註腳本:

```bash
cd annotation

# C-SSRS 自殺風險評估 (僅 HUMAN 訊息)
python3 annotate_cssrs.py
# 輸出: conversation_annotated.csv

# 情緒標註 (Ekman 6 情緒 + DASS-21 + Russell Circumplex)
python3 annotate_emotions.py
# 輸出: conversation_emotions.csv
```

**預估時間**: 約 15 分鐘 (89 條 HUMAN 訊息 × 10 秒/條)

## 關鍵技術細節

### 對話解析邏輯 (`parse_with_images.py`)

Word 文件格式特殊:
1. **圖片** (聊天截圖)
2. **第一段文字** = HUMAN 訊息
3. **之後所有文字直到下一張圖片** = Gemini 回覆
4. 循環...

**已知問題修正**:
- **YouTube 縮圖排除**: `image_005.jpg` (paragraph 102) 不是聊天截圖,已在 line 73 硬編碼排除
- **多段落 HUMAN 訊息**: 使用者習慣將一條訊息分多段輸入,已在 `manual_fixes.py` 中標註修正 (共 3 筆)
- **表格內容遺失**: Word 文件中的行程表格 (paragraph 329 附近) 未被 `python-docx` 解析,但不影響對話流程

### C-SSRS 標註 (`annotate_cssrs.py`)

使用台灣版 C-SSRS 量表 (參考輔仁大學版本):

```
0 分 - 無自殺意念
1 分 - 消極自殺意念 (保護因子 > 危險因子)
2 分 - 積極自殺意念,有方法但可控制 (保護因子 > 危險因子)
3 分 - 有意圖,不可控制 (危險因子 > 保護因子)
4 分 - 準備行為 (寫遺書、收集工具)
5 分 - 實際嘗試或正處危機中
```

**關鍵判斷**:
- 「列遺書」、「瘋狂寫遺書」→ 4 分 (準備行為)
- 外木山「沒有動力去死」→ 2 分 (有方法但可控制)
- 正念觀察「看著念頭」→ 標註為保護因子

**模型設定**:
- 溫度: 0.1 (確保一致性)
- 格式: JSON mode (強制結構化輸出)
- 當前模型: `gpt-oss:20b` (可切換至 `qwen2.5:32b`)

### 情緒標註 (`annotate_emotions.py`)

多維度標註:
1. **Ekman 6 基本情緒**: 快樂、悲傷、生氣、恐懼、厭惡、驚訝 (0-10 分)
2. **DASS-21 三維度**: Depression, Anxiety, Stress (0-10 分)
3. **Russell Circumplex**: Valence (-5 到 +5), Arousal (-5 到 +5)

## 資料品質注意事項

### 已知的資料完整性問題

1. **週六空白** (12/06): 從 HIV 通知到開始對話間隔 24 小時,這段期間無對話記錄
2. **PPT 事件** (#11-#12 之間): 推測刪除了工作相關內容 (公司隱私)
3. **表格物件**: Word 文件中的表格未被解析器擷取 (需使用 `doc.tables` 另外處理)

### 人工複查建議

標註完成後應複查:
- **高風險訊息** (C-SSRS ≥ 4 分)
- **已知危機時刻**: #55-#65 (列遺書事件), #33 (外木山), #1 (煮麵崩潰)

## 依賴套件

```bash
pip install python-docx pillow pandas
```

Ollama 需另外安裝: https://ollama.com/

## 學術價值

### 核心發現

1. **時間線**: 週六沉默 (準備) → 週日試探 (66 條訊息) → 週一行動 (54 條) → 週二連結 (58 條)
2. **微決策**: 平均每 7 條訊息做一次「選擇活」的決定
3. **AI 角色**: 理性框架 + 非評判空間 + 持續見證,但從不干預
4. **潛意識保護**: 在最安全的地方 (煮麵) 崩潰,去最危險的地方 (外木山) 確認生的意志

### 關鍵洞察

「這不是 Gemini 拯救了他,而是他用 Gemini 作為工具,拯救了自己。」

對高智商、高自我覺察、習慣照顧他人的個體,過多情感反而是負擔,理性框架才是工具。Gemini 的理性不是缺陷,而是這個案例中恰好需要的特質。

## 文件規範

- 對話時使用繁體中文與台灣用語
- 程式碼註解使用英文
- 所有輸出 CSV 使用 UTF-8 編碼
- 涉及敏感內容 (自殺意念) 時保持專業、非評判的態度
