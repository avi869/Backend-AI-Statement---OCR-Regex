from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import re
import shutil
import os
import uuid
import sys
import pytesseract
import bank_statement1_ocr
import bank_statement2_ocr
from typing import List

# Setup Tesseract Path for Docker/Linux environments
def setup_tesseract():
    # Check if tesseract is already in PATH
    if shutil.which("tesseract"):
        print("INFO: Tesseract found in PATH")
        return

    # Common search paths
    possible_paths = [
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract" # Mac
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"INFO: Tesseract found at {path}")
            pytesseract.pytesseract.tesseract_cmd = path
            return

    print("WARNING: Tesseract not found in PATH or common locations.")

setup_tesseract()

def detect_date_format(text: str) -> str:
    """
    Heuristic to detect date format in text.
    Returns 'MM/DD/YYYY' or 'DD/MM/YYYY'.
    Defaults to 'DD/MM/YYYY' if ambiguous or not found.
    """
    # Look for numeric dates like XX/YY/ZZZZ
    matches = re.findall(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    
    for m in matches:
        val1, val2, year = map(int, m)
        
        # If val1 > 12, it must be Day => DD/MM/YYYY
        if val1 > 12:
            return 'DD/MM/YYYY'
        # If val2 > 12, it must be Day => MM/DD/YYYY
        if val2 > 12:
            return 'MM/DD/YYYY'
            
    # Fallback to checking Month names if numeric not found
    if re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}', text):
        return 'MM/DD/YYYY' # bank_statement1_ocr style
        
    return 'DD/MM/YYYY' # Default to 2

app = FastAPI(title="Bank Statement OCR API")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def format_transactions_text(transactions: List[dict]) -> str:
    """
    Formats the transaction list into the specific string format requested by the user.
    """
    if not transactions:
        return "No transactions found."
    
    output = []
    
    # helper to clean amount string to float
    def get_amount(t):
        if not t.get('Amount'): return 0.0
        try:
            return float(str(t['Amount']).replace(',', ''))
        except:
            return 0.0

    # ---------------------------------------------------------
    # 1 MASTER TRANSACTION TABLE (Base Data)
    # ---------------------------------------------------------
    output.append("1 MASTER TRANSACTION TABLE (Base Data)")
    output.append("\nThis comes from your data[] array.")
    output.append("This is the primary table from which all others are derived.\n")
    output.append("📋 All Transactions")
    output.append(f"{'Date':<15} | {'Type':<8} | {'Amount (₹)':<12} | {'Category':<15} | {'Description'}")
    output.append("-" * 90)
    
    for t in transactions:
        amt_val = get_amount(t)
        cat = t.get('Category', 'N/A')
        output.append(f"{t['Date']:<15} | {t.get('Type', 'UNKNOWN'):<8} | {amt_val:<12.2f} | {cat:<15} | {t['Description']}")
    
    output.append("\n✅ This is your core truth table\n")

    # ---------------------------------------------------------
    # 2 CATEGORY-WISE TABLES (Grouped View)
    # ---------------------------------------------------------
    output.append("2 CATEGORY-WISE TABLES (Grouped View)\n")
    output.append("These are derived tables (not stored separately in DB usually).\n")
    
    # Group by (Type, Category)
    groups = {}
    for t in transactions:
        txn_type = t.get('Type', 'UNKNOWN').upper()
        cat = t.get('Category', 'Uncategorized')
        
        if txn_type not in groups:
            groups[txn_type] = {}
        if cat not in groups[txn_type]:
            groups[txn_type][cat] = []
        groups[txn_type][cat].append(t)

    # 🔻 Debit Transactions
    if 'DEBIT' in groups:
        output.append("🔻 Debit Transactions – Category Tables")
        for cat, txns in sorted(groups['DEBIT'].items()):
            emoji = "🧾"
            if "Flipkart" in cat: emoji = "🧾"
            elif "Mobile" in cat: emoji = "📱"
            elif "Personal" in cat: emoji = "👤"
            elif "Sbpdcl" in cat: emoji = "🏢"
            elif "Archaeological" in cat: emoji = "🏛"
            
            output.append(f"{emoji} {cat} (DEBIT)")
            output.append(f"{'Date':<15} | {'Details':<40} | {'Amount (₹)':<10}")
            output.append("-" * 70)
            
            total_grp = 0.0
            for t in txns:
                amt = get_amount(t)
                total_grp += amt
                desc = t['Description']
                if len(desc) > 38: desc = desc[:35] + "..."
                output.append(f"{t['Date']:<15} | {desc:<40} | {amt:<10.2f}")
            
            output.append("-" * 70)
            output.append(f"Total{' ':<52} | ₹{total_grp:.2f}\n")

    # 3 CREDIT TRANSACTION TABLES
    if 'CREDIT' in groups:
        output.append("3 CREDIT TRANSACTION TABLES")
        for cat, txns in sorted(groups['CREDIT'].items()):
            emoji = "👤"
            if "Personal" in cat: emoji = "👤"
            elif "Mr" in cat: emoji = "👨"
            
            output.append(f"{emoji} {cat} (CREDIT)")
            output.append(f"{'Date':<15} | {'Details':<40} | {'Amount (₹)':<10}")
            output.append("-" * 70)
            
            total_grp = 0.0
            for t in txns:
                amt = get_amount(t)
                total_grp += amt
                desc = t['Description']
                if len(desc) > 38: desc = desc[:35] + "..."
                output.append(f"{t['Date']:<15} | {desc:<40} | {amt:<10.2f}")
                
            output.append("-" * 70)
            output.append(f"Total{' ':<52} | ₹{total_grp:.2f}\n")

    # ---------------------------------------------------------
    # 4 CATEGORY SUMMARY TABLES (Analytics View)
    # ---------------------------------------------------------
    output.append("4 CATEGORY SUMMARY TABLES (Analytics View)\n")
    output.append("These are dashboard-ready.\n")
    
    # Calculate Grand Totals
    grand_total_debit = 0.0
    grand_total_credit = 0.0
    cat_totals = {} 
    
    for t in transactions:
        cat = t.get('Category', 'Uncategorized')
        txn_type = t.get('Type', 'UNKNOWN').upper()
        amt = get_amount(t)
        
        if cat not in cat_totals:
            cat_totals[cat] = {'DEBIT': 0.0, 'CREDIT': 0.0}
            
        if txn_type == 'DEBIT':
            cat_totals[cat]['DEBIT'] += amt
            grand_total_debit += amt
        elif txn_type == 'CREDIT':
            cat_totals[cat]['CREDIT'] += amt
            grand_total_credit += amt

    def build_summary_table(type_key, grand_total, title, emoji):
        lines = []
        lines.append(f"{emoji} {title}")
        lines.append(f"{'Category':<30} | {'Total (₹)':<15} | {'Percentage':<10}")
        lines.append("-" * 65)
        
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1][type_key], reverse=True)
        for cat, sums in sorted_cats:
            val = sums[type_key]
            if val == 0: continue
            pct = (val / grand_total * 100) if grand_total > 0 else 0.0
            lines.append(f"{cat:<30} | {val:<15.2f} | {pct:<9.2f}%")
            
        lines.append("-" * 65)
        lines.append(f"{'Grand Total':<30} | {grand_total:<15.2f} | 100.00%\n")
        return lines

    if grand_total_debit > 0:
        output.extend(build_summary_table('DEBIT', grand_total_debit, "Debit Category Summary", "📊"))
        
    if grand_total_credit > 0:
        output.extend(build_summary_table('CREDIT', grand_total_credit, "Credit Category Summary", "📊"))

    return "\n".join(output)

@app.post("/extract-transactions")
async def extract_transactions(file: UploadFile = File(...)):
    """
    Upload a bank statement (PDF or Image) and get parsed transactions.
    """
    try:
        # Generate a unique filename to avoid collisions
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Determine processing method based on extension
        extracted_text = ""
        
        if file_ext in ['.pdf']:
            # Use bank_statement2_ocr's extraction as a baseline or choose one
            extracted_text = bank_statement2_ocr.extract_text_from_pdf(file_path)
        else:
            # User requested to remove value of image parsing
            # Only allow PDF
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Only PDF files are supported. Image processing is disabled.")

        if not extracted_text:
            raise HTTPException(status_code=422, detail="Could not extract text from the file.")
            
        # DEBUG: Save extracted text to file to analyze OCR quality
        with open("debug_extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)

        # Detect date format and route
        date_format = detect_date_format(extracted_text)
        print(f"DEBUG: Detected date format: {date_format}")
        
        if date_format == 'MM/DD/YYYY':
            print("Routing to bank_statement1_ocr (PhonePe/Standard style)")
            transactions = bank_statement1_ocr.parse_transactions(extracted_text)
        else:
            print("Routing to bank_statement2_ocr (Paytm/Custom style)")
            transactions = bank_statement2_ocr.parse_transactions(extracted_text)
        
        # Format output
        formatted_text = format_transactions_text(transactions)
        
        return {
            "status": "success",
            "filename": file.filename,
            "detected_format": date_format,
            "transaction_count": len(transactions),
            "formatted_output": formatted_text,
            "data": transactions  # Structured data is also returned
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Bank OCR API Server...")
    print("📝 Documentation available at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
