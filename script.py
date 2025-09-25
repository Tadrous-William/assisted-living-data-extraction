import re
import pandas as pd
from PyPDF2 import PdfReader

# ===== File paths =====
pdf_path = "Assisted-Living-List.pdf"   # input PDF
out_xlsx = "assisted_living_list_extracted.xlsx"
out_csv = "assisted_living_list_extracted.csv"

# ===== Helper functions =====
def normalize_whitespace(s):
    return re.sub(r'\s+', ' ', s).strip()

# common street abbreviations mapping
abbr_map = {
    r'\bRoad\b': 'Rd', r'\bStreet\b': 'St', r'\bAvenue\b': 'Ave',
    r'\bDrive\b': 'Dr', r'\bLane\b': 'Ln', r'\bCourt\b': 'Ct',
    r'\bPlace\b': 'Pl', r'\bBoulevard\b': 'Blvd', r'\bCircle\b': 'Cir',
    r'\bTerrace\b': 'Ter', r'\bWay\b': 'Way'
}
def abbreviate_address(addr):
    a = addr
    for k, v in abbr_map.items():
        a = re.sub(k, v, a, flags=re.IGNORECASE)
    return a

# ===== Read PDF =====
reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    t = page.extract_text()
    if t:
        text += t + "\n"

lines = [ln.strip() for ln in text.splitlines()]
entries = []

i, n = 0, len(lines)
while i < n:
    line = lines[i]

    # Skip headers like "Bristol____"
    if re.match(r'^[A-Za-z ]+_{2,}$', line):
        i += 1
        continue

    # Detect an address line (starts with number or has street keywords)
    if re.match(r'^\d+\b', line) or re.search(r'\b(Ave|Avenue|Road|Rd|St|Street|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Blvd|Boulevard|Way|Trail)\b', line, re.I):
        # Get company name from previous non-empty lines
        j = i - 1
        name_parts = []
        while j >= 0 and lines[j]:
            prev = lines[j]
            if prev.startswith(("Ph:", "Fax:", "Adm", "Web:", "Beds:")):
                break
            if re.search(r',\s*[A-Z]{2}\s*\d{5}', prev):
                break
            name_parts.insert(0, prev)
            j -= 1
        company_name = normalize_whitespace(" ".join(name_parts))

        # Address and City/State/Zip
        address_line = normalize_whitespace(line)
        city_state_zip = lines[i+1] if i+1 < n else ""

        # Collect block until "Beds:" line
        k = i + 1
        block_lines = []
        while k < n and not lines[k].startswith("Beds:") and lines[k]:
            block_lines.append(lines[k])
            k += 1
        if k < n and lines[k].startswith("Beds:"):
            block_lines.append(lines[k])
            k += 1
        block_text = "\n".join([address_line] + block_lines)

        # Extract fields with regex
        phone = re.search(r'Ph:\s*([\d\-\(\)\s]+)', block_text)
        fax = re.search(r'Fax:\s*([\d\-\(\)\s]+)', block_text)
        adm = re.search(r'Adm[:\s]*([A-Za-z\-\.\' ]+)', block_text)
        web = re.search(r'Web:\s*([^\s,]+)', block_text)
        email = re.search(r'[\w\.-]+@[\w\.-]+\.\w{2,}', block_text)

        phone = phone.group(1).strip() if phone else ""
        fax = fax.group(1).strip() if fax else ""
        admin_full = adm.group(1).strip() if adm else ""
        website = web.group(1).strip() if web else ""
        if website and not website.startswith("http"):
            website = "https://" + website
        email = email.group(0) if email else ""

        # Split admin into first / last name
        parts = admin_full.split()
        first_name = parts[0] if parts else ""
        last_name = parts[-1] if len(parts) > 1 else ""

        # City, State, Zip
        city, state, zipcode = "", "", ""
        m_csz = re.search(r'^(.*?),\s*([A-Z]{2})\s*(\d{5})', city_state_zip)
        if m_csz:
            city, state, zipcode = m_csz.groups()

        # Normalize address
        address_std = abbreviate_address(address_line)

        entries.append({
            "Company Name": company_name,
            "First Name": first_name,
            "Last Name": last_name,
            "Address": address_std,
            "City": city,
            "State": state,
            "Zipcode": zipcode,
            "Phone Number": phone,
            "Website": website,
            "Email Address": email,
            "Fax": fax,
            "Raw Admin": admin_full
        })

        i = k
        continue

    i += 1

# ===== Save results =====
df = pd.DataFrame(entries)
df.to_excel(out_xlsx, index=False)
df.to_csv(out_csv, index=False)

print("Data saved to:", out_xlsx, "and", out_csv)
