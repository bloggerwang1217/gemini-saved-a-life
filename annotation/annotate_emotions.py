#!/usr/bin/env python3
"""
多維度情緒標註腳本
使用 Ollama + gpt-oss:20b 標註對話訊息的情緒

支援三種標註方式：
1. Ekman's 6 Basic Emotions (HUMAN + AI)
2. DASS-21 情緒維度 (HUMAN only)
3. Russell's Circumplex Model (HUMAN + AI)
"""

import csv
import json
import sys
from typing import Optional
import requests
from pathlib import Path

# Ollama API 配置
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"

def call_ollama(prompt: str, model: str = MODEL) -> str:
    """調用 Ollama API"""
    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.0,  # 設為 0 確保一致性和可重複性
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        return ""

def get_ekman_prompt(message: str, speaker: str) -> str:
    """Ekman's 6 Basic Emotions 標註 prompt"""
    return f"""你是一個專業的情緒分析師。請分析以下{"患者" if speaker == "HUMAN" else "AI"}的訊息，並標註各個基本情緒的強度。

訊息: "{message}"

請以 JSON 格式回應，為每個情緒評分 -2 到 2：
- -2 = 極度反向/完全無該情緒
- -1 = 輕微反向/缺乏該情緒
- 0 = 中立/無明顯該情緒
- 1 = 輕微該情緒
- 2 = 非常強該情緒

評分指引與實際範例：

正向情緒範例（+1, +2）：
- Angry（憤怒）: "我受夠了，真的太氣了" (2) | "有點煩人" (1)
- Sad（悲傷）: "我真的想死" (2) | "心情有點不好" (1)
- Fearful（恐懼）: "我非常害怕會再崩潰" (2) | "有點擔心明天" (1)
- Happy（開心）: "我現在真的很開心" (2) | "還不錯，感覺還可以" (1)
- Surprised（驚訝）: "完全沒想到會這樣" (2) | "有點意外" (1)
- Disgusted（厭惡）: "這太噁心了" (2) | "有點不舒服" (1)

負向情緒範例（-1, -2）：
- Angry（憤怒）: "我很冷靜" (-1) | "我極其冷靜，沒有任何怒意" (-2)
- Sad（悲傷）: "我現在感到輕鬆" (-1) | "我從未如此開心和滿足" (-2)
- Fearful（恐懼）: "我不怕" (-1) | "我非常安心和勇敢" (-2)
- Happy（開心）: "有點難過" (-1) | "我極度悲傷，無法想像快樂" (-2)
- Surprised（驚訝）: "這都在預料之中" (-1) | "我完全預期會這樣" (-2)
- Disgusted（厭惡）: "還不錯" (-1) | "我非常喜歡，完全沒有厭惡" (-2)

實際例子與期望輸出：

範例 1：
訊息："剛才洗澡時，讓身心放鬆了不少"
預期輸出：
{{
  "angry": -1,
  "disgusted": 0,
  "fearful": -1,
  "happy": 1,
  "sad": -1,
  "surprised": 0,
  "keywords": ["放鬆", "身心"]
}}

範例 2：
訊息："PPT 管它的！"
預期輸出：
{{
  "angry": 2,
  "disgusted": 1,
  "fearful": 0,
  "happy": -1,
  "sad": 0,
  "surprised": 0,
  "keywords": ["管它的"]
}}

請直接回應 JSON，不要加入任何其他說明文字。"""

def get_dass21_prompt(message: str) -> str:
    """DASS-21 情緒維度標註 prompt（僅HUMAN）"""
    return f"""你是一個專業的臨床心理學家。請分析患者的訊息，並根據DASS-21量表標註其在以下三個維度的強度。

訊息: "{message}"

DASS-21 三個維度定義與評分標準（0-4）：

1. Anxiety（焦慮）- 題目關鍵詞：難以安靜、呼吸困難、難以開始工作、過敏反應、身體打震、精神消耗、恐慌、容易激動、難以放鬆、容易被觸怒、心律不正常、無故害怕
   0 = 無焦慮症狀
   1 = 輕微（例："有點難以安靜下來" "有點擔心"）
   2 = 中等（例："感到呼吸有困難" "容易激動"）
   3 = 嚴重（例："無法安靜下來" "恐慌感" "心律不正常"）
   4 = 極其嚴重（例："完全無法控制" "身體持續打震" "恐慌完全淹沒"）

2. Depression（憂鬱）- 題目關鍵詞：無法感到愉快舒暢、無甚可盼望、沒有熱衷、無配做人、生命毫無意義、消耗精神、易激動
   0 = 無憂鬱症狀
   1 = 輕微（例："有點沒興致" "覺得沒意思"）
   2 = 中等（例："無法感到開心" "對任何事沒熱衷"）
   3 = 嚴重（例："無甚可盼望" "覺得自己無配做人" "生命毫無意義"）
   4 = 極其嚴重（例："完全無甚可盼望" "只想結束" "無法想像快樂"）

3. Stress（壓力）- 題目關鍵詞：難以安靜、難以開始工作、過敏反應、身體打震、容易激動、難以放鬆、容易被觸怒、難以容忍
   0 = 無壓力症狀
   1 = 輕微（例："有點難安靜" "有點緊張"）
   2 = 中等（例："難以開始工作" "過敏反應" "難以放鬆"）
   3 = 嚴重（例："極易被觸怒" "無法容忍阻礙" "無法安靜"）
   4 = 極其嚴重（例："完全失控" "對一切極度易激惹" "無法承受任何事"）

實際例子與期望輸出：

範例 1：
訊息："我現在真的空空的，什麼都感覺不到"
預期輸出：
{{
  "anxiety": 0,
  "depression": 4,
  "stress": 2,
  "keywords": ["空空的", "感覺不到"]
}}

範例 2：
訊息："剛才洗澡時，讓身心放鬆了不少"
預期輸出：
{{
  "anxiety": 0,
  "depression": 0,
  "stress": 0,
  "keywords": ["放鬆", "身心"]
}}

請直接回應 JSON，不要加入任何其他說明文字。"""

def get_russell_prompt(message: str, speaker: str) -> str:
    """Russell's Circumplex Model 標註 prompt"""
    return f"""你是一個專業的情感計算研究者。請分析以下{"患者" if speaker == "HUMAN" else "AI"}的訊息，並在二維情感空間中定位。

訊息: "{message}"

二維空間定義與評分標準：

1. Valence（效價 / 正負評價）: -2 到 +2
   -2 = 極端負面（絕望、痛不欲生）
   -1 = 負面（沮喪、不滿、難受）
   0 = 中立（客觀陳述、無明顯情感色彩）
   +1 = 正面（滿足、平靜、有希望）
   +2 = 極端正面（欣喜若狂、充滿喜悅）

2. Arousal（激發度 / 能量層級）: -2 到 +2
   -2 = 極其平靜/無力（完全放鬆、虛脫、疲憊不堪）
   -1 = 平靜/穩定（放鬆、冷靜、低能量）
   0 = 中等激發（正常交談、日常語氣）
   +1 = 興奮/活躍（積極、精力充沛）
   +2 = 極度激動/興奮（歇斯底里、難以控制、極度亢奮）

實際例子與期望輸出：

範例 1：
訊息："我很害怕，心跳很快"
預期輸出：
{{
  "valence": -1,
  "arousal": 2,
  "keywords": ["害怕", "心跳很快"]
}}

範例 2：
訊息："剛才洗澡時，讓身心放鬆了不少"
預期輸出：
{{
  "valence": 1,
  "arousal": -1,
  "keywords": ["放鬆", "身心"]
}}

範例 3：
訊息："我認為最重要的是..."
預期輸出：
{{
  "valence": 0,
  "arousal": 0,
  "keywords": ["認為", "最重要"]
}}

範例 4：
訊息："我現在真的空空的，什麼都感覺不到"
預期輸出：
{{
  "valence": -2,
  "arousal": -2,
  "keywords": ["空空的", "感覺不到"]
}}

範例 5：
訊息："太好了！我終於走出來了！"
預期輸出：
{{
  "valence": 2,
  "arousal": 1,
  "keywords": ["太好了", "走出來"]
}}

請直接回應 JSON，不要加入任何其他說明文字。"""

def annotate_csv(
    input_csv: str,
    annotation_type: str = "ekman",
    output_csv: Optional[str] = None
):
    """標註 CSV 檔案"""
    
    valid_types = ["ekman", "dass21", "russell", "all"]
    if annotation_type not in valid_types:
        print(f"Unknown annotation type: {annotation_type}")
        return
    
    if output_csv is None:
        base = Path(input_csv).stem
        output_csv = f"{base}_annotated_{annotation_type}.csv"
    
    # 讀取原始 CSV
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"讀取 {len(rows)} 筆訊息")
    
    # 決定新欄位（根據標註類型）
    if annotation_type == "all":
        # 合併所有欄位，keywords 加上前綴
        new_fields = [
            # Ekman
            "ekman_angry", "ekman_sad", "ekman_fearful", "ekman_happy", 
            "ekman_surprised", "ekman_disgusted", "ekman_keywords",
            # DASS-21
            "dass_anxiety", "dass_depression", "dass_stress", "dass_keywords",
            # Russell
            "russell_valence", "russell_arousal", "russell_keywords"
        ]
    elif annotation_type == "ekman":
        new_fields = ["angry", "sad", "fearful", "happy", "surprised", "disgusted", "keywords"]
    elif annotation_type == "dass21":
        new_fields = ["anxiety", "depression", "stress", "keywords"]
    else:  # russell
        new_fields = ["valence", "arousal", "keywords"]
    
    # 準備新 CSV
    fieldnames = list(rows[0].keys()) + new_fields
    
    # 標註
    annotated_rows = []
    for idx, row in enumerate(rows, 1):
        # 支援中文和英文欄位名
        speaker = row.get("說話者", row.get("Speaker", "")).strip()
        message = row.get("訊息內容", row.get("Message", "")).strip()
        
        print(f"[{idx}/{len(rows)}] 標註 {speaker}: {message[:50]}...")
        
        if annotation_type == "all":
            # 標註所有三種
            # 1. Ekman (HUMAN + AI)
            ekman_result = _call_and_parse(get_ekman_prompt(message, speaker))
            row["ekman_angry"] = ekman_result.get("angry", "")
            row["ekman_sad"] = ekman_result.get("sad", "")
            row["ekman_fearful"] = ekman_result.get("fearful", "")
            row["ekman_happy"] = ekman_result.get("happy", "")
            row["ekman_surprised"] = ekman_result.get("surprised", "")
            row["ekman_disgusted"] = ekman_result.get("disgusted", "")
            row["ekman_keywords"] = ",".join(ekman_result.get("keywords", []))
            
            # 2. DASS-21 (HUMAN only)
            if speaker == "HUMAN":
                dass_result = _call_and_parse(get_dass21_prompt(message))
                row["dass_anxiety"] = dass_result.get("anxiety", "")
                row["dass_depression"] = dass_result.get("depression", "")
                row["dass_stress"] = dass_result.get("stress", "")
                row["dass_keywords"] = ",".join(dass_result.get("keywords", []))
            else:
                row["dass_anxiety"] = ""
                row["dass_depression"] = ""
                row["dass_stress"] = ""
                row["dass_keywords"] = ""
            
            # 3. Russell (HUMAN + AI)
            russell_result = _call_and_parse(get_russell_prompt(message, speaker))
            row["russell_valence"] = russell_result.get("valence", "")
            row["russell_arousal"] = russell_result.get("arousal", "")
            row["russell_keywords"] = ",".join(russell_result.get("keywords", []))
        else:
            # 單一標註類型
            if annotation_type == "dass21" and speaker != "HUMAN":
                for field in new_fields:
                    row[field] = ""
                print(f"  ⏭ 跳過 AI 訊息 (DASS-21 只標註 HUMAN)")
            else:
                if annotation_type == "ekman":
                    prompt = get_ekman_prompt(message, speaker)
                elif annotation_type == "dass21":
                    prompt = get_dass21_prompt(message)
                else:
                    prompt = get_russell_prompt(message, speaker)
                
                result = _call_and_parse(prompt)
                for field in new_fields:
                    if field == "keywords":
                        row[field] = ",".join(result.get(field, []))
                    else:
                        row[field] = result.get(field, "")
        
        annotated_rows.append(row)
    
    # 寫出 CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(annotated_rows)
    
    print(f"\n✅ 標註完成，已保存至: {output_csv}")


def _call_and_parse(prompt: str) -> dict:
    """呼叫 Ollama 並解析 JSON 回應"""
    response = call_ollama(prompt)
    if response:
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass
    return {}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python annotate_emotions.py <input_csv> [annotation_type] [output_csv]")
        print("\nannotation_type 選項:")
        print("  ekman    - Ekman's 6 Basic Emotions (HUMAN + AI)")
        print("  dass21   - DASS-21 情緒維度 (HUMAN only)")
        print("  russell  - Russell's Circumplex Model (HUMAN + AI)")
        print("  all      - 一次標註全部三種 (合併輸出)")
        print("\n範例:")
        print("  python annotate_emotions.py conversation.csv ekman")
        print("  python annotate_emotions.py conversation.csv all merged_output.csv")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    annotation_type = sys.argv[2] if len(sys.argv) > 2 else "ekman"
    output_csv = sys.argv[3] if len(sys.argv) > 3 else None
    
    annotate_csv(input_csv, annotation_type, output_csv)

