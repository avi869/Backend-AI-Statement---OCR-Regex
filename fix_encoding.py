
try:
    with open('output_test_v2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('output_test_v2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Converted successfully.")
except Exception as e:
    print(f"Error: {e}")
