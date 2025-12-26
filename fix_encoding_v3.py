
try:
    with open('output_test_v3.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('output_test_v3_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Converted successfully.")
except Exception as e:
    # Fallback if it wasn't utf-16 (e.g. if python just wrote ascii/utf8)
    try:
        with open('output_test_v3.txt', 'r', encoding='mbcs') as f: # Windows default?
            content = f.read()
        with open('output_test_v3_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Converted successfully from mbcs.")
    except Exception as e2:
         print(f"Error: {e}, {e2}")
