#!/usr/bin/env python3
"""
為 conversation.csv 添加 Day 欄位
根據時間線分析標記每條訊息屬於哪一天
"""
import csv
import os

# 根據 timeline_analysis.md 確定的分界點
DAY_RANGES = {
    1: (1, 66),      # Day 1 = 週日 12/07: #1-#66
    2: (67, 120),    # Day 2 = 週一 12/08: #67-#120
    3: (121, 178),   # Day 3 = 週二 12/09: #121-#178
}

# 日期對照
DAY_INFO = {
    1: "2025/12/07 (週日)",
    2: "2025/12/08 (週一)", 
    3: "2025/12/09 (週二)",
}

def add_day_column(input_file='conversation.csv', output_file='conversation_with_day.csv'):
    """
    讀取 CSV，添加 Day 欄位
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        messages = list(reader)
    
    # 添加 Day 到標題
    new_header = header + ['Day']
    
    # 為每條訊息添加 Day
    new_messages = []
    for row in messages:
        seq = int(row[0])
        
        # 判斷屬於哪一天
        day = None
        for d, (start, end) in DAY_RANGES.items():
            if start <= seq <= end:
                day = d
                break
        
        if day is None:
            day = '?'  # 不應該發生
        
        new_row = row + [str(day)]
        new_messages.append(new_row)
    
    # 寫入新檔案
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(new_header)
        writer.writerows(new_messages)
    
    print(f"✅ 已添加 Day 欄位")
    print(f"   輸入: {input_file}")
    print(f"   輸出: {output_file}")
    
    # 統計
    day_counts = {}
    for row in new_messages:
        day = row[-1]
        day_counts[day] = day_counts.get(day, 0) + 1
    
    print(f"\n📊 各天訊息數統計:")
    for day in sorted([int(d) for d in day_counts.keys() if d != '?']):
        count = day_counts[str(day)]
        date_info = DAY_INFO[day]
        print(f"   Day {day} ({date_info}): {count} 條訊息")
    
    return output_file

def create_analysis_folder():
    """
    創建 analysis 資料夾並移動生成的分析文件
    """
    
    analysis_dir = 'analysis'
    if not os.path.exists(analysis_dir):
        os.makedirs(analysis_dir)
        print(f"\n📁 已創建資料夾: {analysis_dir}/")
    
    # 列出要移動的分析文件
    analysis_files = [
        'conversation_with_day.csv',
        'crisis_moments.md',
        'timeline_analysis.md',
    ]
    
    # 移動文件
    moved = []
    for filename in analysis_files:
        if os.path.exists(filename):
            target = os.path.join(analysis_dir, filename)
            # 如果目標存在，先刪除
            if os.path.exists(target):
                os.remove(target)
            os.rename(filename, target)
            moved.append(filename)
            print(f"   ✓ {filename} → {analysis_dir}/")
    
    return analysis_dir, moved

if __name__ == "__main__":
    print("="*70)
    print("添加 Day 欄位到 conversation.csv")
    print("="*70)
    print()
    
    # 添加 Day 欄位
    output_file = add_day_column()
    
    print("\n" + "="*70)
    print("整理分析文件到資料夾")
    print("="*70)
    print()
    
    # 創建並移動到 analysis 資料夾
    analysis_dir, moved_files = create_analysis_folder()
    
    print(f"\n✅ 完成！")
    print(f"\n📂 分析文件已整理至: {analysis_dir}/")
    print(f"   - conversation_with_day.csv (含 Day 欄位)")
    print(f"   - crisis_moments.md (危機時刻分析)")
    print(f"   - timeline_analysis.md (時間線分析)")
    
    print(f"\n💡 原始 conversation.csv 保持不變")
    print(f"   使用時請讀取: {analysis_dir}/conversation_with_day.csv")
