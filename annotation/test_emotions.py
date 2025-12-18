#!/usr/bin/env python3
"""測試三種情緒標註 - 隨機選取一筆 HUMAN 訊息"""

import csv
import json
import random
import requests
from annotate_emotions import get_ekman_prompt, get_dass21_prompt, get_russell_prompt

OLLAMA_API = 'http://localhost:11434/api/generate'
MODEL = 'gpt-oss:20b'

def call_ollama(prompt):
    try:
        print("  正在呼叫 LLM...")
        response = requests.post(
            OLLAMA_API, 
            json={'model': MODEL, 'prompt': prompt, 'stream': False, 'temperature': 0.0}, 
            timeout=120
        )
        return response.json()['response'].strip()
    except Exception as e:
        return f'Error: {e}'

# 讀取所有 HUMAN 訊息並隨機選一筆
with open('../conversation.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    human_rows = [r for r in reader if r['說話者'] == 'HUMAN']
    row = random.choice(human_rows)
    message = row['訊息內容']
    speaker = row['說話者']
    msg_id = row['序號']

print(f'訊息序號: {msg_id}')

print(f'測試訊息: {message[:80]}...')
print(f'說話者: {speaker}')
print('='*60)

# Test 1: Ekman
print('\n📊 測試 1: Ekman 6 Basic Emotions')
result = call_ollama(get_ekman_prompt(message, speaker))
print(f'回應:\n{result}')

# Test 2: DASS-21
print('\n📊 測試 2: DASS-21')
result = call_ollama(get_dass21_prompt(message))
print(f'回應:\n{result}')

# Test 3: Russell
print('\n📊 測試 3: Russell Circumplex')
result = call_ollama(get_russell_prompt(message, speaker))
print(f'回應:\n{result}')

print('\n✅ 測試完成!')
