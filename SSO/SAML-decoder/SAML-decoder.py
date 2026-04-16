import base64
import zlib
import urllib.parse

saml_request_encoded = input("Enter the SAMLRequest (URL-encoded and Base64-encoded): ")

# Fix common copy-paste issues
saml_request_encoded = saml_request_encoded.strip()
saml_request_encoded = saml_request_encoded.replace(" ", "+")  # spaces often replace + signs

# Step 1: URL decode
saml_url_decoded = urllib.parse.unquote(saml_request_encoded)

# Step 2: Base64 decode - add padding if missing
padding_needed = len(saml_url_decoded) % 4
if padding_needed:
    saml_url_decoded += "=" * (4 - padding_needed)

saml_b64_decoded = base64.b64decode(saml_url_decoded)
print(f"[*] Base64 decoded length: {len(saml_b64_decoded)} bytes")
print(f"[*] First bytes (hex): {saml_b64_decoded[:10].hex()}")

# Step 3: Try all decompression methods
try:
    saml_xml = zlib.decompress(saml_b64_decoded, -15)
    print("[+] Decoded with raw deflate")
except zlib.error as e1:
    print(f"[-] Raw deflate failed: {e1}")
    try:
        saml_xml = zlib.decompress(saml_b64_decoded)
        print("[+] Decoded with zlib")
    except zlib.error as e2:
        print(f"[-] Zlib failed: {e2}")
        saml_xml = saml_b64_decoded
        print("[+] No compression, using raw bytes")

print("\n--- SAML XML ---")
print(saml_xml.decode('utf-8'))