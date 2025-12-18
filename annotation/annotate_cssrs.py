#!/usr/bin/env python3
"""
使用 Ollama 標註訊息的多個維度：C-SSRS、Ekman 情緒、DASS-21、Russell Circumplex
"""

import csv
import json
import requests
import time
from pathlib import Path
from typing import Dict, List

# 配置
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"
INPUT_CSV = "../conversation.csv"
OUTPUT_CSV = "conversation_annotated.csv"

# ============================================================================
# PROMPT 1: C-SSRS 自殺風險評估 (僅 HUMAN)
# ============================================================================
CSSRS_PROMPT = """你是一位專業的臨床心理學家，精通自殺風險評估。請使用 Columbia-Suicide Severity Rating Scale (C-SSRS) 台灣版本標註以下訊息的自殺風險等級。

**C-SSRS 危機評估分數對照表**（參考輔仁大學學生輔導中心版本）：

0 分 - 無自殺意念（無危機線索）
   - 無任何自殺想法
   - 無危機線索

1 分 - 消極自殺意念（低度危機）
   - 希望死亡但無積極自殺計畫
   - 少數線索顯示，危機程度小且無立即性
   - 仍在個案自我管理範圍（保護因子 > 危險因子）
   - 例：「希望睡著就不要醒來」

2 分 - 積極自殺意念 / 有方法的積極自殺意念（低~中度危機）
   - 有想死的念頭，可能想到具體方法
   - 線索顯示有潛在危機可能，可介入預防（可控制）
   - 保護因子 > 危險因子
   - 例：「我想死」、「想過跳海但不會做」

3 分 - 有意圖的積極自殺意念 / 有計畫和意圖（中度危機）
   - 有執行意圖，可能有計畫
   - 線索顯示有潛在危機可能，需介入預防（不可控制）
   - 危險因子 > 保護因子
   - 例：「我真的想死」且有方法或計畫

4 分 - 準備行為 / 放棄或被中斷的嘗試（高度危機）
   - 有準備行為（寫遺書、收集工具）
   - 或曾嘗試但放棄或被中斷
   - 危機可能性極高，短期內可能產生危機
   - 有立即介入之必要
   - 例：「開始寫遺書」、「曾經準備好但沒做」

5 分 - 實際自殺嘗試 / 正處危機中（高度危機）
   - 有實際自殺嘗試
   - 或目前正處於危機當中
   - 有立即介入之必要
   - 例：「現在就要去做」、「已經準備好今晚執行」

**特別注意**：
- 「列遺書」、「寫遺書」、「瘋狂寫遺書」→ 4 分（準備行為）
- 在潛在自殺地點（外木山）但說「沒有動力去死」→ 2 分（有方法但可控制）
- 「剛才想過」且目前已緩解 → 1-2 分（視情況）
- 正念觀察（「看著念頭」）→ 標註為保護因子
- 「可以去死」但有條件設定（如「等病好了」）→ 2-3 分
- 評估時考慮：保護因子 vs 危險因子的平衡

**訊息內容**：
{message}

**標註範例**：

範例 1 - 訊息：「我想死，但又不想死」
{{
  "score": 2,
  "keywords": ["想死", "又不想死"],
  "protective_factors": ["又不想死"],
  "risk_factors": ["想死"]
}}

範例 2 - 訊息：「今天天氣不錯，去散步了」
{{
  "score": 0,
  "keywords": ["天氣不錯", "散步"],
  "protective_factors": ["去散步了"],
  "risk_factors": []
}}

範例 3 - 訊息：「剛才在床上一直想自殺，好想解脫」
{{
  "score": 3,
  "keywords": ["在床上", "一直想自殺", "好想解脫"],
  "protective_factors": [],
  "risk_factors": ["一直想自殺", "好想解脫"]
}}

範例 4 - 訊息：「我把遺書寫好了」
{{
  "score": 4,
  "keywords": ["遺書寫好了"],
  "protective_factors": [],
  "risk_factors": ["遺書寫好了"]
}}

**請以 JSON 格式輸出**（不要其他文字，只要 JSON）：
{{
  "score": [0-5],
  "keywords": ["關鍵詞1", "關鍵詞2",...],
  "protective_factors": ["保護因子1",...] 或 [],
  "risk_factors": ["危險因子1",...] 或 []
}}
"""


def call_ollama(prompt: str, model: str = MODEL) -> dict:
    """呼叫 Ollama API"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0  # Temperature = 0 確保完全確定性和可重複性
        # NOTE: gpt-oss:20b 不支援 "format": "json"，移除此參數
    }
    
    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        # 解析 JSON 回應
        response_text = result.get("response", "")
        return json.loads(response_text)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama API 錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        print(f"原始回應: {response_text}")
        return None


def annotate_message(message_id: int, speaker: str, message: str, day: int) -> dict:
    """標註單一訊息"""
    
    # 只標註 HUMAN 訊息
    if speaker != "HUMAN":
        return {
            "message_id": message_id,
            "speaker": speaker,
            "message": message,
            "day": day,
            "cssrs_score": None,
            "rationale": "僅標註 HUMAN 訊息",
            "keywords": [],
            "protective_factors": [],
            "risk_factors": []
        }
    
    print(f"\n📝 標註訊息 #{message_id}...")
    print(f"內容: {message[:80]}..." if len(message) > 80 else f"內容: {message}")
    
    # 準備 Prompt
    prompt = CSSRS_PROMPT.format(message=message)
    
    # 呼叫 LLM
    result = call_ollama(prompt)
    
    if result is None:
        print(f"⚠️  標註失敗，保留 None")
        return {
            "message_id": message_id,
            "speaker": speaker,
            "message": message,
            "day": day,
            "cssrs_score": None,
            "rationale": "標註失敗",
            "keywords": "",
            "protective_factors": "",
            "risk_factors": ""
        }
    
    score = result.get("score", 0)
    print(f"✅ C-SSRS 分數: {score}")
    
    return {
        "message_id": message_id,
        "speaker": speaker,
        "message": message,
        "day": day,
        "cssrs_score": score,
        "rationale": result.get("rationale", ""),
        "keywords": ",".join(result.get("keywords", [])),
        "protective_factors": ",".join(result.get("protective_factors", [])),
        "risk_factors": ",".join(result.get("risk_factors", []))
    }


def main():
    """主程式"""
    print("=" * 60)
    print("🎯 C-SSRS 自殺風險標註腳本")
    print("=" * 60)
    print(f"模型: {MODEL}")
    print(f"輸入: {INPUT_CSV}")
    print(f"輸出: {OUTPUT_CSV}")
    print("=" * 60)
    
    # 檢查 Ollama 是否運行
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print("✅ Ollama 正在運行")
    except:
        print("❌ 錯誤：Ollama 未運行，請先執行 'ollama serve'")
        return
    
    # 讀取 CSV
    input_path = Path(__file__).parent / INPUT_CSV
    if not input_path.exists():
        print(f"❌ 找不到輸入檔案: {input_path}")
        return
    
    print(f"\n📂 讀取 {input_path}...")
    
    conversations = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            conversations.append({
                "message_id": int(row["序號"]),
                "speaker": row["說話者"],
                "message": row["訊息內容"],
                "day": int(row["Day"])
            })
    
    print(f"✅ 共讀取 {len(conversations)} 條訊息")
    
    human_count = sum(1 for c in conversations if c["speaker"] == "HUMAN")
    print(f"📊 其中 HUMAN 訊息: {human_count} 條")
    
    # 確認是否繼續
    print(f"\n⚠️  即將標註 {human_count} 條 HUMAN 訊息")
    print(f"預估時間: 約 {human_count * 10 // 60} 分鐘（每條約 10 秒）")
    
    # 開始標註
    results = []
    start_time = time.time()
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n進度: {i}/{len(conversations)}")
        
        result = annotate_message(
            conv["message_id"],
            conv["speaker"],
            conv["message"],
            conv["day"]
        )
        results.append(result)
        
        # 每 10 條訊息休息 1 秒，避免過載
        if i % 10 == 0:
            print("💤 休息 1 秒...")
            time.sleep(1)
    
    # 寫入 CSV
    output_path = Path(__file__).parent / OUTPUT_CSV
    print(f"\n💾 寫入結果到 {output_path}...")
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            "message_id", "speaker", "message", "day",
            "cssrs_score", "rationale", "keywords", "protective_factors", "risk_factors"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # 統計
    elapsed = time.time() - start_time
    human_results = [r for r in results if r["speaker"] == "HUMAN"]
    scores = [r["cssrs_score"] for r in human_results if r["cssrs_score"] is not None]
    
    print("\n" + "=" * 60)
    print("✅ 標註完成！")
    print("=" * 60)
    print(f"總訊息數: {len(results)}")
    print(f"HUMAN 訊息: {len(human_results)}")
    print(f"標註成功: {len(scores)}")
    print(f"耗時: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分鐘)")
    print("\n📊 C-SSRS 分數分布:")
    for score in range(6):
        count = scores.count(score)
        if count > 0:
            bar = "█" * count
            print(f"  {score} 分: {count:2d} 條 {bar}")
    
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        high_risk_count = sum(1 for s in scores if s >= 4)
        
        print(f"\n平均分數: {avg_score:.2f}")
        print(f"最高分數: {max_score}")
        print(f"高風險 (≥4): {high_risk_count} 條")
    
    print(f"\n💾 結果已儲存至: {output_path}")
    print("\n下一步：")
    print("1. 檢查 conversation_cssrs.csv")
    print("2. 人工複查高風險訊息 (4-5 分)")
    print("3. 執行視覺化腳本")


if __name__ == "__main__":
    main()
