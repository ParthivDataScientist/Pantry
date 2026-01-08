import base64

key_b64 = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEkb+FD1Qx4P6ZMzbm6gH8s69Xj/SXVynOtn+XUddccbncsLhzeyxZRTYvT9IW9Y1XFnB0I7f/hRbISn8FslM7bQ=="

try:
    key_bytes = base64.b64decode(key_b64)
    print(f"Total length: {len(key_bytes)}")
    
    # Check for raw key (65 bytes starting with 0x04)
    if len(key_bytes) == 65 and key_bytes[0] == 0x04:
        print("Is raw key: Yes")
    else:
        print(f"Is raw key: No (First byte: {hex(key_bytes[0])})")
        
    # Check for ASN.1 SubjectPublicKeyInfo
    # Header for P-256 usually ends with ... 03 42 00 04 ... 
    # 03 is BitString, 42 is length (66 bytes), 00 is unused bits, 04 is uncompressed point.
    if b'\x03\x42\x00\x04' in key_bytes:
        print("Found ASN.1 header pattern")
        # Extract
        idx = key_bytes.find(b'\x03\x42\x00')
        raw_key = key_bytes[idx+3:]
        print(f"Extracted length: {len(raw_key)}")
        print(f"Extracted Starts with 0x04: {raw_key[0] == 0x04}")
        print(f"Extracted Base64: {base64.urlsafe_b64encode(raw_key).decode()}")

except Exception as e:
    print(e)
