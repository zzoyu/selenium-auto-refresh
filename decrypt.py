import base64
import urllib.parse

def decrypt_to_secret(encoded_data):
    print("Decrypting OTP secret...")
    print(f"Original encoded data: {encoded_data}, Length: {len(encoded_data)}")
    
    # 먼저 URL 디코딩 수행
    url_decoded_data = urllib.parse.unquote(encoded_data)
    print(f"URL decoded data: {url_decoded_data}, Length: {len(url_decoded_data)}")
    
    # Base64 패딩을 올바르게 처리
    remainder = len(url_decoded_data) % 4
    if remainder != 0:  # 4의 배수가 아닌 경우에만 패딩 추가
        padding_needed = 4 - remainder
        url_decoded_data += "=" * padding_needed
        print(f"Added {padding_needed} padding characters")
    
    print(f"Final encoded data length: {len(url_decoded_data)}")
    
    try:
        decoded_bytes = base64.urlsafe_b64decode(url_decoded_data)
        print(f"Successfully decoded. Decoded bytes length: {len(decoded_bytes)}")
    except Exception as e:
        print(f"Base64 decoding failed: {e}")
        return None

    secret_data = None
    if decoded_bytes[0] == 0x0A: 
        pos = decoded_bytes.find(b'\n', 1) 
        if pos != -1 and pos + 1 < len(decoded_bytes):
            length = decoded_bytes[pos + 1]
            secret_data = decoded_bytes[pos + 2: pos + 2 + length]

    secret_base32 = None
    if secret_data:
        secret_base32 = base64.b32encode(secret_data).decode()

    return secret_base32
