
try:
    with open('output_test_debug.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('output_test_debug_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Converted successfully.")
except Exception as e:
    try:
        with open('output_test_debug.txt', 'r', encoding='mbcs') as f:
            content = f.read()
        with open('output_test_debug_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Converted successfully from mbcs.")
    except Exception as e2:
         print(f"Error: {e}, {e2}")
