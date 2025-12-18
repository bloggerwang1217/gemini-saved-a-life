#!/usr/bin/env python3
"""
手動修正：多段落 HUMAN 訊息
將 AI 訊息的第一段（誤判的 HUMAN 續段）移回 HUMAN 訊息

已知問題：
- #15 說話者標記錯誤（HUMAN → AI）：已於 2025-12-18 手動修正
  內容：「把那封信發出去...你今天真的展現了驚人的韌性...」
  修正方式：併入前一條 AI 訊息 (#14)
  原因：作者的記錄錯誤（Word 文件中就記錯了）
"""
import csv

# 需要修正的訊息：(HUMAN訊息編號, AI訊息編號)
# AI 訊息的第一段（第一個換行前）應該屬於 HUMAN
FIXES = [
    (9, 10),    # YouTube 連結：#10 的第一段應併入 #9
    (51, 52),   # 洗澡訊息：#52 的第一段應併入 #51
    (77, 78),   # 醫院門口：#78 的第一段應併入 #77
    (117, 118), # 空空的：#118 的第一段應併入 #117
]

def fix_conversation_csv(input_file='conversation.csv', output_file='conversation_fixed.csv'):
    """
    修正邏輯：
    1. 找到 AI 訊息（#52, #78, #118）
    2. 取出第一段（第一個換行前的內容）
    3. 將第一段附加到前面的 HUMAN 訊息
    4. AI 訊息保留剩餘部分
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        header = reader[0]
        messages = list(reader[1:])
    
    fixes_applied = []
    
    # 建立以序號為 key 的字典方便查找
    msg_dict = {int(seq): [seq, speaker, msg] for seq, speaker, msg in messages}
    
    for human_seq, ai_seq in FIXES:
        if ai_seq not in msg_dict or human_seq not in msg_dict:
            print(f"⚠️  警告: 找不到 #{human_seq} 或 #{ai_seq}")
            continue
        
        ai_msg = msg_dict[ai_seq]
        human_msg = msg_dict[human_seq]
        
        # 檢查類型
        if human_msg[1] != 'HUMAN':
            print(f"⚠️  警告: #{human_seq} 不是 HUMAN 訊息")
            continue
        if ai_msg[1] != 'AI':
            print(f"⚠️  警告: #{ai_seq} 不是 AI 訊息")
            continue
        
        # 分割 AI 訊息
        ai_content = ai_msg[2]
        if '\n' in ai_content:
            first_para = ai_content.split('\n', 1)[0]
            rest = ai_content.split('\n', 1)[1]
        else:
            # 沒有換行，整條都是 HUMAN 的
            first_para = ai_content
            rest = ''
        
        # 將第一段加到 HUMAN
        human_msg[2] = human_msg[2] + '\n' + first_para
        
        # 更新 AI 訊息
        if rest.strip():
            ai_msg[2] = rest
            fixes_applied.append(f"#{ai_seq}: 第一段移至 #{human_seq}")
        else:
            # AI 沒有剩餘內容，標記刪除
            ai_msg[2] = ''  # 清空內容，稍後過濾
            fixes_applied.append(f"#{ai_seq}: 整段移至 #{human_seq} (訊息將被刪除)")
    
    # 重建訊息列表，過濾掉空內容的訊息
    fixed_messages = []
    for seq in sorted(msg_dict.keys()):
        msg_data = msg_dict[seq]
        if msg_data[2].strip():  # 只保留有內容的
            fixed_messages.append(msg_data)
    
    # 重新編號
    renumbered = []
    for new_seq, (old_seq, speaker, content) in enumerate(fixed_messages, 1):
        renumbered.append([str(new_seq), speaker, content])
    
    # 寫入
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(renumbered)
    
    print(f"✅ 修正完成！")
    print(f"   輸入: {input_file}")
    print(f"   輸出: {output_file}")
    print(f"\n修正項目:")
    for fix in fixes_applied:
        print(f"   {fix}")
    
    # 統計
    human_count = sum(1 for _, s, _ in renumbered if s == 'HUMAN')
    ai_count = sum(1 for _, s, _ in renumbered if s == 'AI')
    print(f"\n修正後統計:")
    print(f"   HUMAN: {human_count} 條")
    print(f"   AI: {ai_count} 條")
    print(f"   總計: {len(renumbered)} 條")
    
    return output_file

if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("多段落 HUMAN 訊息修正工具")
    print("="*70)
    print("\n已知需要修正的訊息:")
    for human_seq, ai_seq in FIXES:
        print(f"  #{ai_seq} (AI) 的第一段 → 移至 #{human_seq} (HUMAN)")
    
    print("\n" + "="*70)
    
    # 確認
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        output = fix_conversation_csv('conversation.csv', 'conversation_fixed.csv')
        print(f"\n💾 已生成修正版: {output}")
        print("\n下一步:")
        print("  1. 檢查 conversation_fixed.csv")
        print("  2. 確認無誤後: mv conversation_fixed.csv conversation.csv")
    else:
        print("\n預覽模式（不會修改檔案）")
        print("\n執行修正請使用: python3 manual_fixes.py --apply")
