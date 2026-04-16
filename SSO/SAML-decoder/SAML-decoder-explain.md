1. Imports
```
import base64
import zlib
import urllib.parse
```
base64 — handles Base64 encoding/decoding. SAML uses Base64 to represent binary data as printable text.
zlib — handles compression/decompression. Some SPs compress the SAMLRequest before Base64 encoding it.
urllib.parse — handles URL encoding/decoding. When a SAMLRequest travels in a URL, special characters get encoded (e.g., = becomes %3D, + becomes %2B).

2. Input

```
saml_request_encoded = input("Enter the SAMLRequest ...")
```

Instead of hardcoding the value in the script, it asks you to paste it at runtime. Cleaner and reusable.

3. Copy-paste Cleanup

```
saml_request_encoded = saml_request_encoded.strip()
saml_request_encoded = saml_request_encoded.replace(" ", "+")
```

.strip() — removes any accidental leading/trailing whitespace or newlines from pasting.
.replace(" ", "+") — this is the important one. Base64 uses + as a valid character, but when a Base64 string travels inside a URL, + means space. So if you copy a SAMLRequest from a URL and paste it without URL-decoding first, all the + signs become spaces. This line fixes that before anything else runs.

4. Step 1 — URL Decode

```
saml_url_decoded = urllib.parse.unquote(saml_request_encoded)
```

Converts URL-encoded characters back to their original form. For example:

%3D → =
%2B → +
%2F → /

After this step, you have a clean Base64 string.

5. Step 2 — Fix Padding + Base64 Decode

```
padding_needed = len(saml_url_decoded) % 4
if padding_needed:
    saml_url_decoded += "=" * (4 - padding_needed)

saml_b64_decoded = base64.b64decode(saml_url_decoded)
```
Base64 works in blocks of 4 characters. If the string length isn't a multiple of 4, Python's decoder throws an error. The = signs at the end of a Base64 string are padding to make it fit — but they're often stripped during URL transport. This code adds them back if needed.
For example if the string length mod 4 gives remainder 2, it adds ==. If remainder is 3, it adds =.
After this you have raw bytes — either compressed or plain XML.

6. Diagnostics

```
print(f"[*] Base64 decoded length: {len(saml_b64_decoded)} bytes")
print(f"[*] First bytes (hex): {saml_b64_decoded[:10].hex()}")
```

These two lines are debugging helpers. The first hex bytes tell you what format the data is in:

789c... → zlib compressed (has zlib magic header)
789d... or similar deflate signatures → raw deflate
3c3f786d... → that's <?xm in ASCII, meaning plain uncompressed XML — no decompression needed

7. Step 3 — Decompression (Try/Except cascade)

```
try:
    saml_xml = zlib.decompress(saml_b64_decoded, -15)  # raw deflate
except zlib.error as e1:
    try:
        saml_xml = zlib.decompress(saml_b64_decoded)   # zlib with header
    except zlib.error as e2:
        saml_xml = saml_b64_decoded                     # no compression
```

This tries three strategies in order, because different SPs implement SAML differently:

Attempt                 Method                      When used
1st                     decompress(data, -15        Raw DEFLATE—most common for SAMLRequests in GET     bindings


2nd                     decompress(data)            DEFLATE with zlib header (RFC 1950)

3rd                     No decompression            POST bindings — data is just plain Base64 encoded XML


The -15 in the first attempt tells zlib to skip expecting a zlib header and treat the data as raw deflate stream directly.

8. Final Output

```
print(saml_xml.decode('utf-8'))
```

Converts the bytes to a readable UTF-8 string and prints the XML. At this point you'll see the full AuthnRequest with all its fields.

The overall flow visually:

Raw SAMLRequest (from URL or POST body)
        ↓
  strip + fix + signs
        ↓
   URL decode (%XX → chars)
        ↓
  fix Base64 padding (add =)
        ↓
   Base64 decode → bytes
        ↓
  try deflate / zlib / raw
        ↓
     XML string ✅