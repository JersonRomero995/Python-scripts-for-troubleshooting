import base64
import zlib
import urllib.parse

# Paste your SAMLRequest value here (URL-decoded first if needed)
saml_request_encoded = "YOUR_SAML_REQUEST_VALUE_HERE"

# Step 1: URL decode (if needed)
saml_url_decoded = urllib.parse.unquote(saml_request_encoded)

# Step 2: Base64 decode
saml_b64_decoded = base64.b64decode(saml_url_decoded)

# Step 3: Inflate (decompress)
saml_xml = zlib.decompress(saml_b64_decoded, -15)  # -15 = raw deflate

print(saml_xml.decode('utf-8'))

