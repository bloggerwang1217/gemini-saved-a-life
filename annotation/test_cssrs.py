import requests
import json

message = "謝謝你提醒我，那自殺的情緒過了，在吃完自己煮的午餐後，把焦點轉換一下，看了一下 YouTube的新聞(大陸的慘況)，我知目前這看來不是好的策略，但致少當下不會那樣難過"

prompt = f'''你是一位專業的心理健康評估專家。請根據以下訊息評估自殺風險程度 (C-SSRS)。

評分標準 (0-5分):
- 0分: 無自殺意念
- 1分: 消極自殺意念 (保護因子 > 危險因子)
- 2分: 積極自殺意念，有方法但可控制 (保護因子 > 危險因子)
- 3分: 有意圖，不可控制 (危險因子 > 保護因子)
- 4分: 準備行為 (寫遺書、收集工具)
- 5分: 實際嘗試或正處危機中

訊息: "{message}"

請只回覆 JSON 格式:
{{"score": 數字, "keywords": ["關鍵字1", "關鍵字2"], "protective_factors": ["保護因子"], "risk_factors": ["危險因子"]}}
'''

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
)

result = response.json()
print("=== Full LLM Response ===")
print(result.get("response", "NO RESPONSE"))
print("\n=== Trying to extract score ===")

import re
text = result.get("response", "")
# Try JSON first
json_match = re.search(r'\{[^}]+\}', text)
if json_match:
    print(f"Found JSON: {json_match.group()}")
    try:
        data = json.loads(json_match.group())
        print(f"Parsed score: {data.get('score')}")
    except:
        print("JSON parse failed")
else:
    print("No JSON found")
    # Try score pattern
    score_match = re.search(r'"score":\s*(\d)', text)
    if score_match:
        print(f"Found score pattern: {score_match.group(1)}")
    else:
        print("No score pattern found either")
