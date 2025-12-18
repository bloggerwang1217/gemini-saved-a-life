#!/usr/bin/env python3
"""
合併 C-SSRS 標註和情緒標註的 CSV
"""

import pandas as pd
import sys


def merge_csvs(cssrs_csv: str, emotion_csv: str, output_csv: str = "conversation_final.csv"):
    """
    合併兩個 CSV 檔案
    cssrs_csv: conversation_annotated.csv (有 C-SSRS 標註)
    emotion_csv: conversation_emotions_merged.csv (有情緒標註)
    """
    print(f"讀取 C-SSRS 標註: {cssrs_csv}")
    df_cssrs = pd.read_csv(cssrs_csv)
    print(f"  → {len(df_cssrs)} 筆, 欄位: {list(df_cssrs.columns)}")
    
    print(f"\n讀取情緒標註: {emotion_csv}")
    df_emotion = pd.read_csv(emotion_csv)
    print(f"  → {len(df_emotion)} 筆, 欄位: {list(df_emotion.columns)}")
    
    # 只取情緒標註的新欄位（排除原始欄位）
    original_cols = ['序號', '說話者', '訊息內容', 'Day']
    emotion_only_cols = [c for c in df_emotion.columns if c not in original_cols]
    print(f"\n情緒標註欄位: {emotion_only_cols}")
    
    # 用 index 合併（假設兩個 CSV 的行順序一致）
    if len(df_cssrs) != len(df_emotion):
        print(f"⚠️ 警告：兩個檔案行數不一致！({len(df_cssrs)} vs {len(df_emotion)})")
    
    # 直接將情緒欄位加到 C-SSRS dataframe
    for col in emotion_only_cols:
        df_cssrs[col] = df_emotion[col].values
    
    print(f"\n合併完成: {len(df_cssrs)} 筆")
    print(f"最終欄位: {list(df_cssrs.columns)}")
    
    # 儲存
    df_cssrs.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\n✅ 已儲存至: {output_csv}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方式:")
        print("  python merge_csvs.py <cssrs_csv> <emotion_csv> [output_csv]")
        print()
        print("範例:")
        print("  python merge_csvs.py ../conversation_annotated.csv conversation_annotated_all.csv")
        sys.exit(1)
    
    cssrs_csv = sys.argv[1]
    emotion_csv = sys.argv[2]
    output_csv = sys.argv[3] if len(sys.argv) > 3 else "conversation_final.csv"
    
    merge_csvs(cssrs_csv, emotion_csv, output_csv)
