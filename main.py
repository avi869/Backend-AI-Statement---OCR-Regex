from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import shutil
import os
import uuid
from typing import List

# Import our OCR logic
# Ensure bank_statement_ocr.py is in the same directory or python path
try:
    from bank_statement1_ocr import process_image, extract_text_from_pdf, parse_transactions
except ImportError:
    # Fallback if running from a different root context, though usually not needed if structure is flat
    from .bank_statement2_ocr import process_image, extract_text_from_pdf, parse_transactions

app = FastAPI(title="Bank Statement OCR API")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def format_transactions_text(transactions: List[dict]) -> str:
    """
    Formats the transaction list into the specific string format requested by the user.
    Generates:
    1. Separate tables for each Category (split by Debit/Credit if needed).
    2. Summary tables for Debit and Credit.
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

    # 1. Group by (Category, Type)
    # keys: (Category, Type) -> list of txns
    groups = {}
    
    # Verify we have category, if not (e.g. old OCR logic), fallback 'Uncategorized'
    for t in transactions:
        cat = t.get('Category', 'Uncategorized')
        txn_type = t.get('Type', 'UNKNOWN').upper()
        
        key = (cat, txn_type)
        if key not in groups:
            groups[key] = []
        groups[key].append(t)
        
    # Sort groups? Maybe by Category Name
    sorted_keys = sorted(groups.keys())
    
    # ---------------------------------------------------------
    # PART A: Detailed Tables per Category
    # ---------------------------------------------------------
    for cat, txn_type in sorted_keys:
        txns = groups[(cat, txn_type)]
        
        header_title = f"{cat} Transactions ({txn_type})"
        output.append(header_title)
        output.append("-" * len(header_title))
        
        # Table Header
        # Date | Details | Amount
        output.append(f"{'Date':<15} | {'Details':<40} | {'Amount':<10}")
        output.append("-" * 75)
        
        total_grp = 0.0
        
        for t in txns:
            amt_val = get_amount(t)
            total_grp += amt_val
            
            # Format: Oct 23, 2025 | Paid to Rakesh Kumar | 40
            # Truncate details if too long
            desc = t['Description']
            if len(desc) > 38:
                desc = desc[:35] + "..."
                
            output.append(f"{t['Date']:<15} | {desc:<40} | ₹{amt_val:<9.2f}")
            
        output.append("-" * 75)
        output.append(f"Total: ₹{total_grp:.2f}")
        output.append("\n") # Spacer between tables

    # ---------------------------------------------------------
    # PART B: Summary Tables
    # ---------------------------------------------------------
    
    # Calculate Grand Totals for Percentages
    grand_total_debit = 0.0
    grand_total_credit = 0.0
    
    # Category Totals map: cat -> debit_sum, credit_sum
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

    def build_summary_table(type_key, grand_total):
        lines = []
        lines.append(f"Category Summary ({type_key})")
        lines.append(f"{'Category':<30} | {'Total':<15} | {'Percentage':<10}")
        lines.append("-" * 65)
        
        # Sort by total amount desc
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1][type_key], reverse=True)
        
        for cat, sums in sorted_cats:
            val = sums[type_key]
            if val == 0: continue
            
            pct = (val / grand_total * 100) if grand_total > 0 else 0.0
            lines.append(f"{cat:<30} | ₹{val:<14.2f} | {pct:<9.2f}%")
            
        lines.append("-" * 65)
        lines.append(f"{'Grand Total':<30} | ₹{grand_total:<14.2f} | 100.00%")
        lines.append("\n")
        return lines

    if grand_total_debit > 0:
        output.extend(build_summary_table('DEBIT', grand_total_debit))
        
    if grand_total_credit > 0:
        output.extend(build_summary_table('CREDIT', grand_total_credit))

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
            extracted_text = extract_text_from_pdf(file_path)
        else:
            # User requested to remove value of image parsing
            # Only allow PDF
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Only PDF files are supported. Image processing is disabled.")

        # elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        #     extracted_text = process_image(file_path, debug_save=False)
        # else:
        #     # Attempt image processing as fallback or raise error
        #     extracted_text = process_image(file_path, debug_save=False)
        #     
        #     if not extracted_text:
        #         os.remove(file_path)
        #         raise HTTPException(status_code=400, detail="Unsupported file format or OCR failed.")

        # Clean up the file (optional, keeping it for debug could be useful but better to clean in prod)
        # os.remove(file_path) 
        
        if not extracted_text:
            raise HTTPException(status_code=422, detail="Could not extract text from the file.")
            
        # DEBUG: Save extracted text to file to analyze OCR quality
        with open("debug_extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)

        # Parse transactions
        transactions = parse_transactions(extracted_text)
        
        # Format output
        formatted_text = format_transactions_text(transactions)
        
        return {
            "status": "success",
            "filename": file.filename,
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
