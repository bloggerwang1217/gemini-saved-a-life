#!/usr/bin/env python3
"""
Parse conversation using image positions as boundaries
Pattern: Image -> HUMAN text (first para) -> GEMINI text (until next image)
"""
from docx import Document
from docx.oxml import parse_xml
import csv

def extract_document_structure(docx_path):
    """
    Extract both paragraphs and image positions
    Returns list of (type, content, index) where type is 'text' or 'image'
    """
    doc = Document(docx_path)
    
    # Get all block-level elements in order
    elements = []
    
    for i, para in enumerate(doc.paragraphs):
        # Check if paragraph contains image
        has_image = False
        for run in para.runs:
            if run._element.xpath('.//pic:pic'):
                has_image = True
                break
        
        if has_image:
            elements.append(('image', f'[IMAGE_{len([e for e in elements if e[0]=="image"])}]', i))
        
        # Add text paragraph
        text = para.text.strip()
        if text:
            elements.append(('text', text, i))
    
    return elements

def find_conversation_bounds(elements):
    """Find where conversation starts and ends"""
    start = 0
    end = len(elements)
    
    for i, (typ, content, idx) in enumerate(elements):
        if typ == 'text' and '和 Gemini 的對話' in content:
            start = i + 1
            break
    
    for i, (typ, content, idx) in enumerate(elements):
        if typ == 'text' and ('個案編號' in content or 'Phase 1' in content):
            end = i
            break
    
    return start, end

def parse_by_images(elements, start, end):
    """
    Parse conversation using image boundaries
    Pattern: IMAGE -> first text = HUMAN -> remaining texts = GEMINI
    
    Note: Excludes non-chat images (e.g., YouTube thumbnails)
    """
    messages = []
    i = start
    image_counter = 0  # Track image number for filtering
    
    while i < end:
        typ, content, idx = elements[i]
        
        # Find next image
        if typ == 'image':
            # Check if this is a non-chat image to exclude
            # Image 005 (6th image, 0-indexed as 5) is YouTube thumbnail at paragraph 102
            if image_counter == 5:
                # Skip this image - it's not a chat screenshot
                i += 1
                image_counter += 1
                continue
            
            image_counter += 1
            
            # After image, collect texts until next image
            i += 1
            human_text = None
            gemini_parts = []
            
            while i < end:
                curr_typ, curr_content, curr_idx = elements[i]
                
                if curr_typ == 'image':
                    # Hit next image, stop collecting
                    break
                elif curr_typ == 'text':
                    if human_text is None:
                        # First text after image = HUMAN
                        human_text = curr_content
                    else:
                        # Subsequent texts = GEMINI
                        gemini_parts.append(curr_content)
                i += 1
            
            # Save messages
            if human_text:
                messages.append(('HUMAN', human_text))
            if gemini_parts:
                gemini_text = '\n'.join(gemini_parts)
                messages.append(('AI', gemini_text))
        
        else:
            # Text before first image - might be initial context
            i += 1
    
    return messages

def save_csv(messages, filename="conversation.csv"):
    """Save to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['序號', '說話者', '訊息內容'])
        
        for i, (speaker, msg) in enumerate(messages, 1):
            writer.writerow([i, speaker, msg])
    
    print(f"✓ Saved to {filename}")
    human_count = sum(1 for s, _ in messages if s == 'HUMAN')
    ai_count = sum(1 for s, _ in messages if s == 'AI')
    print(f"  Total messages: {len(messages)}")
    print(f"  HUMAN: {human_count}, AI: {ai_count}")
    
    return messages

if __name__ == "__main__":
    print("Extracting document structure...")
    elements = extract_document_structure("Gemini_Suicide.docx")
    
    print(f"Total elements: {len(elements)}")
    img_count = sum(1 for typ, _, _ in elements if typ == 'image')
    text_count = sum(1 for typ, _, _ in elements if typ == 'text')
    print(f"  Images: {img_count}, Text blocks: {text_count}\n")
    
    # Show first few elements
    print("First 20 elements:")
    for i, (typ, content, idx) in enumerate(elements[:20]):
        if typ == 'image':
            print(f"{i}: {typ.upper()}")
        else:
            preview = content[:60] + "..." if len(content) > 60 else content
            print(f"{i}: {typ} - {preview}")
    
    print("\n" + "="*70)
    
    # Find conversation
    start, end = find_conversation_bounds(elements)
    print(f"\nConversation: elements {start} to {end}")
    
    # Parse by images
    messages = parse_by_images(elements, start, end)
    print(f"Parsed into {len(messages)} messages\n")
    
    # Show first 6 messages
    print("First 6 messages:")
    for i, (speaker, msg) in enumerate(messages[:6], 1):
        preview = msg[:80].replace('\n', ' ') + "..." if len(msg) > 80 else msg
        print(f"{i}. [{speaker}] {preview}")
    
    print("\n" + "="*70)
    save_csv(messages)
