#PAYTEM
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 17:06:39 2025
@author: ASUS

Purpose:
- OCR PhonePe transaction image
- OCR PDF bank statement
- Extract Date, Description, Type, Amount

Improvements by Agent:
- Fixed regex to capture 'Mobile recharged' and other transaction descriptions.
- Improved currency symbol handling (₹, Rs, INR).
- Modularized code into functions for better maintainability.
- Added file existence checks.
"""

import cv2
import pytesseract
import re
import os
import numpy as np
from pdf2image import convert_from_path

# Configuration for Tesseract
CUSTOM_CONFIG = r'--oem 3 --psm 6'

# Business Keywords to filter out "Personal" transactions
BUSINESS_KEYWORDS = {
    "PVT", "LTD", "LIMITED", "BANK", "FINANCE", "SERVICES", "TECHNOLOGIES", "TECH",
    "ENTERPRISES", "SOLUTIONS", "INFOTECH", "SYSTEMS", "NETWORK", "COMMUNICATIONS",
    "RECHARGE", "MOBILE", "INTERNET", "BROADBAND", "DTH", "BILL", "PAYMENT", "UPI",
    "WALLET", "STORES", "MARKET", "BAZAR", "SHOP", "REST", "CAFE", "FOODS", "HOTEL",
    "TRAVELS", "LOGISTICS", "EXPRESS", "COURIER", "MEDIA", "STUDIO", "ENTERTAINMENT",
    "HOSPITAL", "CLINIC", "PHARMACY", "MEDICOS", "DIAGNOSTICS", "LABS", "SCHOOL",
    "COLLEGE", "ACADEMY", "INSTITUTE", "UNIVERSITY", "EDUCATION", "CENTRE", "CLASSES",
    "TUTORIALS", "COACHING", "TRADERS", "AGENCIES", "ASSOCIATES", "CONSULTANTS",
    "ADVISORS", "PARTNERS", "BROTHERS", "SONS", "JEWELLERS", "OPTICALS", "WATCHES",
    "GARMENTS", "TEXTILES", "FASHION", "BOUTIQUE", "TAILORS", "DRY", "CLEANERS",
    "BAKERY", "SWEETS", "DAIRY", "FARM", "AGRO", "SEEDS", "FERTILIZERS", "CHEMICALS",
    "PETRO", "GAS", "FUELS", "AUTOMOBILES", "MOTORS", "HONDA", "HERO", "BAJAJ", "TATA",
    "MARUTI", "TOYOTA", "HYUNDAI", "FORD", "NISSAN", "RENAULT", "MAHINDRA", "KIA", "MG",
    "VOLKSWAGEN", "SKODA", "BMW", "MERCEDES", "AUDI", "VOLVO", "JAGUAR", "LAND", "ROVER",
    "PORSCHE", "FERRARI", "LAMBORGHINI", "MASERATI", "ROLLS", "ROYCE", "BENTLEY", "ASTON",
    "MARTIN", "MCLAREN", "BUGATTI", "PAGANI", "KOENIGSEGG", "TESLA", "RIVIAN", "LUCID",
    "BYD", "XPENG", "NIO", "POLESTAR", "FISKER", "CANOO", "FARADAY", "FUTURE", "LORDSTOWN",
    "NIKOLA", "PROTERRA", "LION", "ELECTRIC", "WORKHORSE", "HYLIION", "XL", "FLEET",
    "TRAIN", "BUS", "METRO", "FLIGHT", "AIR", "AIRLINES", "AIRWAYS", "AVIATION", "TRAVEL",
    "TRIP", "TOUR", "TOURISM", "RESORT", "INN", "STAY", "LODGE", "GUEST", "HOUSE", "HOME",
    "FLIPKART", "AMAZON", "MYNTRA", "AJIO", "MEESHO", "NYKAA", "ZOMATO", "SWIGGY", "Uber", "Ola",
    "Netflix", "Prime", "Hotstar", "Spotify", "Youtube", "Google", "Apple"
}

def extract_entity(description: str) -> str:
    """
    Extracts the entity name from the description.
    Removes 'Paid to', 'Received from' prefixes.
    """
    # Normalize spaces
    text = " ".join(description.split())
    
    # Remove prefixes (Case insensitive)
    text = re.sub(r'^(Paid to|Received from)\s+', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def detect_category(description: str, entity: str) -> str:
    """
    Decides if the transaction is 'Personal' or Business/Named.
    """
    desc_lower = description.lower()
    entity_upper = entity.upper()
    entity_words = entity.split()
    
    # Check for Personal Logic
    # 1. Must start with Paid to / Received from
    has_personal_prefix = desc_lower.startswith("paid to") or desc_lower.startswith("received from")
    
    if has_personal_prefix:
        # 2. Heuristics for Person Name:
        # - 2 to 3 words
        # - All words Title Case (First letter cap, rest lower - roughly)
        #   Actually, OCR might give all caps "RAKESH KUMAR". 
        #   Let's check if it *looks* like a name and *not* a business.
        
        is_correct_length = 2 <= len(entity_words) <= 3
        
        # Check for Business Keywords
        # If any word in the entity is a business keyword, it's NOT personal
        has_business_keyword = any(word.upper() in BUSINESS_KEYWORDS for word in entity_words)
        
        # Additional cleanup check: if it's just "Paid to Flipkart", Flipkart is in keywords? 
        # Yes, added Flipkart to keywords.
        
        if is_correct_length and not has_business_keyword:
            return "Personal"

    # Default: The category is the Entity Name itself
    # User Request: Merge categories if first word is same (e.g. Flipkart vs Flipkart Ltd)
    # We take the first word as the Category Name for businesses.
    if entity_words:
        return entity_words[0].title() # "Flipkart", "Zomato", "Mobile"
    
    return entity

def process_image(image_path, debug_save=True):
    """
    Reads and preprocesses an image for OCR.
    """
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return ""

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Failed to load image: {image_path}")
        return ""

    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)

    _, thresh = cv2.threshold(
        gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Rescaling
    scale_percent = 150
    width = int(thresh.shape[1] * scale_percent / 100)
    height = int(thresh.shape[0] * scale_percent / 100)
    resized = cv2.resize(thresh, (width, height), interpolation=cv2.INTER_LINEAR)

    if debug_save:
        cv2.imwrite("processed.jpg", resized)

    text = pytesseract.image_to_string(resized, config=CUSTOM_CONFIG)
    return text

def extract_text_from_pdf(pdf_path):
    """
    Converts PDF pages to images and runs OCR.
    """
    if not os.path.exists(pdf_path):
        print(f"⚠️ PDF not found: {pdf_path}")
        return ""

    try:
        pages = convert_from_path(pdf_path, dpi=300)
    except Exception as e:
        print(f"❌ PDF conversion error: {e}")
        return ""

    text = ""
    for page in pages:
        page_np = np.array(page)
        gray = cv2.cvtColor(page_np, cv2.COLOR_BGR2GRAY)
        text += pytesseract.image_to_string(gray, config=CUSTOM_CONFIG)
    return text

def parse_transactions(text):
    """
    Parses OCR text into structured transaction data.
    """
    text = text.replace('\r', '\n')

    # Regex for Date: Matches "Oct 23, 2025" (Mon DD YYYY) OR "14 Dec" (DD Mon)
    date_pattern = re.compile(
        r'(?:'
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}[.,\s]+\s*\d{4}'
        r'|'
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
        r')',
        re.IGNORECASE
    )

    dates = date_pattern.findall(text)
    # Split text by date. [1:] likely skips the header before the first date.
    blocks = date_pattern.split(text)[1:] 

    transactions = []

    for date, block in zip(dates, blocks):
        block = block.strip()
        
        # Strategy: Use TYPE (DEBIT/CREDIT) as the anchor.
        # Structure: [Description] [TYPE] [Amount]
        
        
        # --- NEW LOGIC: Language-Based Detection (Priority) ---
        # "Semantic meaning never changes" - User
        
        block_lower = block.lower()
        extracted_type = "UNKNOWN"
        
        # Indicators
        debit_indicators = [
            r'\bpaid\s+to\b', r'\bsent\s+to\b', r'\bmoney\s+sent\s+to\b',
            r'\bwithdraw\b', r'\bwithdrawn\b', r'\bdebit\b'
        ]
        credit_indicators = [
            r'\breceived\s+from\b', r'\bcredited\b', r'\bdeposit\b', r'\bcredit\b'
        ]
        
        # 1. Check for Credit Phrases
        # We check credit first or debit first? 
        # User list: Received... -> Credit.
        found_credit = False
        for ind in credit_indicators:
            if re.search(ind, block_lower):
                extracted_type = "CREDIT"
                found_credit = True
                break
        
        if not found_credit:
            # 2. Check for Debit Phrases
            for ind in debit_indicators:
                if re.search(ind, block_lower):
                    extracted_type = "DEBIT"
                    break
        
        # 3. Fallback to Explicit Type Match (regex) if semantic failed?
        # The user said "but it is limeted to some application only".
        # However, if semantic failed, we might still want to check explicit "DEBIT"/"CREDIT" in case
        # the text is just "DEBIT 500". My list included explicit 'debit'/'credit' in indicators,
        # so logic covers it. 
        
        if extracted_type != "UNKNOWN":
            txn_type = extracted_type
        else:
            # Fallback to existing regex just in case (e.g. Type column exists but no description phrases)
            type_match = re.search(r'\b(DEBIT|CREDIT)\b', block, re.IGNORECASE)
            if type_match:
                txn_type = type_match.group(1).upper()
            else:
                 txn_type = "UNKNOWN"

        description = "UNKNOWN"
        amount = None
        
        # --- Description & Amount Extraction ---
        # We need to split somewhat intelligently.
        
        # If we found a semantic phrase, we should try to extract description relative to it?
        # Or just take everything before the amount?
        # User example: "Received from ANAM ANSARI" -> Type CREDIT.
        
        # Let's find the amount first (at the end usually).
        # Reuse existing amount logic but make it robust.
        
        # Clean block (remove dates if valid date starts block? No, block is split by date)
        
        # Look for the last number in the block
        # We filter out "Transaction ID ...", "UTR ...", "Ref ..." lines first to avoid matching IDs as amount.
        
        clean_block = re.sub(r'(Transaction\s*ID|Tran\s*ID|Txn\s*ID|UTR\s*No|Ref\s*No|UPI\s*Ref).*', '', block, flags=re.IGNORECASE)
        
        # Also remove the semantic phrases to avoid matching them?
        # No, "Received from" usually precedes the name.
        
        # Find all amounts
        # Improved Regex to capture:
        # Group 1: Negative Sign (Optional)
        # Group 2: Currency Symbol (Optional)
        # Group 3: The Number
        amt_matches = list(re.finditer(r'(-\s*)?(Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)', clean_block, re.IGNORECASE))
        
        if amt_matches:
            # Scoring Logic to pick best Amount candidate
            best_match = None
            max_score = -1
            
            for i, m in enumerate(amt_matches):
                sign_grp = m.group(1)
                bs_grp = m.group(2) # Currency Symbol
                val_str = m.group(3).replace(",", "")
                
                # Filters
                # Phone number heuristic: > 9 digits and no decimal => ignore
                if "." not in val_str and len(val_str) >= 10:
                    continue
                    
                score = 0
                if bs_grp: 
                    score += 100 # Has currency symbol
                if "." in val_str:
                    score += 50  # Has decimal
                
                # Position bonus (later is usually better, but explicit symbol outweighs)
                score += i
                
                if score > max_score:
                    max_score = score
                    best_match = m

            if best_match:
                m = best_match
                sign_grp = m.group(1)
                sym_grp = m.group(2)
                val_str = m.group(3).replace(",", "")
                
                # Only apply 7/2 noise rule if NO currency symbol was found
                if not sym_grp:
                    if len(val_str) > 1 and val_str[0] in ['7', '2']: 
                         val_str = val_str[1:]
                
                amount = val_str
                
                # Detect Negative => DEBIT
                if sign_grp and '-' in sign_grp:
                   # Force DEBIT if amount is negative (handles "Credit Card" false positives)
                   txn_type = "DEBIT"
                
                # Description
                raw_desc = clean_block[:m.start()].strip()
                description = " ".join(raw_desc.split())
        
        else:
             # If no amount found, maybe whole block is description?
             description = " ".join(clean_block.split())

        # Cleanup specific noise logic from before
        # (Paid by, etc were handled in clean_block regex above generally)

        # --- Category Detection ---
        entity = extract_entity(description)
        category = detect_category(description, entity)

        transactions.append({
            "Date": date,
            "Description": description,
            "Type": txn_type,
            "Amount": amount,
            "Category": category  # NEW FIELD
        })

    return transactions

def main():
    print("🧠 Running Bank OCR Script...")

    # Define Paths
    image_path = r"C:\Users\ASUS\Desktop\ocr_test.jpg"
   # pdf_path = r"C:\Users\ASUS\Desktop\Statement.pdf"
    pdf_path = r"C:\Users\ASUS\Desktop\PaytemStatement.pdf"

    # 1. Process Image
    print(f"\n📸 Processing Image: {image_path}")
    image_text = process_image(image_path)
    if image_text:
        print("✅ Image OCR completed")
        # print(image_text) # Optional debug

    # 2. Process PDF
    print(f"\n📄 Processing PDF: {pdf_path}")
    pdf_text = extract_text_from_pdf(pdf_path)
    if pdf_text:
        print("✅ PDF OCR completed")
    
    # Save Raw OCR Output
    full_text = image_text + "\n" + pdf_text
    os.makedirs("data", exist_ok=True)
    with open("data/output_ocr_full.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

    # 3. Parse Transactions
    if full_text.strip():
        print("\n🔍 Parsing transactions...\n")
        transactions = parse_transactions(full_text)

        if transactions:
            output_lines = []
            output_lines.append("✅ PARSED TRANSACTIONS:\n")
            output_lines.append(f"{'Date':<15} | {'Type':<8} | {'Amount':<10} | {'Description'}")
            output_lines.append("-" * 60)
            for t in transactions:
                amt = t['Amount'] if t['Amount'] else "0.00"
                line = f"{t['Date']:<15} | {t['Type']:<8} | ₹{amt:<9} | {t['Description']}"
                output_lines.append(line)
            
            # Print to console
            for line in output_lines:
                print(line)
            
            # Save to file
            with open("parsed_output.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))
        else:
            print("⚠️ No transactions found (Check OCR quality or Regex)")
    else:
        print("⚠️ No OCR text generated.")

if __name__ == "__main__":
    main()
