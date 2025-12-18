#!/usr/bin/env python3
"""
簡化版：按段落順序提取圖片
"""
from docx import Document
import os
from collections import OrderedDict

def extract_images_ordered(docx_path, output_dir="images_ordered"):
    """按段落順序提取圖片"""
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    doc = Document(docx_path)
    
    # 先建立 rId 到段落順序的映射
    rid_to_para = OrderedDict()
    
    for para_idx, para in enumerate(doc.paragraphs):
        for run in para.runs:
            # 檢查是否有圖片
            if run._element.xpath('.//pic:pic'):
                # 找到所有圖片的 embedding ID
                for drawing in run._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'):
                    for blip in drawing.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                        embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                        if embed and embed not in rid_to_para:
                            rid_to_para[embed] = para_idx
    
    # 按順序提取圖片
    image_count = 0
    for rid, para_idx in rid_to_para.items():
        try:
            image_part = doc.part.related_parts[rid]
            image_data = image_part.blob
            
            # 確定副檔名
            content_type = image_part.content_type
            if "png" in content_type:
                ext = ".png"
            elif "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "gif" in content_type:
                ext = ".gif"
            else:
                ext = ".bin"
            
            # 儲存
            filename = f"image_{image_count:03d}{ext}"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            print(f"提取: {filename} (paragraph {para_idx})")
            image_count += 1
            
        except Exception as e:
            print(f"警告: 無法提取 rId={rid}: {e}")
    
    print(f"\n✅ 總共提取 {image_count} 張圖片（按段落順序）")
    return image_count

if __name__ == "__main__":
    print("開始按段落順序提取圖片...\n")
    count = extract_images_ordered("Gemini_Suicide.docx")
    
    print("\n" + "="*70)
    print("對比:")
    print(f"  舊資料夾 (images/): 89 張")
    print(f"  新資料夾 (images_ordered/): {count} 張")
    
    print("\n重要:")
    print("  按段落順序第 7 張 (image_006.*) = Paragraph 102 = YouTube 縮圖")
    print("  需要在解析時排除這張圖片")
