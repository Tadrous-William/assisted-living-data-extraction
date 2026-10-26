# Assisted Living Data Extraction Project

## Overview
This project extracts structured data (facility names, addresses, phone numbers, websites, etc.) from an unstructured PDF containing assisted living facility records. The extracted data was cleaned, normalized, and enriched by adding missing website information.

## Files
- **Assisted-Living-List.pdf** – Original source file.
- **assisted_living_list_extracted.csv** – Final cleaned dataset (~40 records).
- **script.py** – Python script used for extraction & cleaning.
- **PDF Data Extraction and Cleaning.pdf** – Short report on the process.

## Features
- Automated PDF text extraction.
- Data cleaning (names, addresses, phone numbers).
- Enrichment by searching for missing websites.
- Export to clean CSV format.

## Tech Stack
- Python
- Pandas
- Regex
- PDFPlumber / PyPDF2

## Example Output
| Name                     | Address                  | Phone        | Website             |
|--------------------------|--------------------------|--------------|---------------------|
| Atria Bay Springs Village| 147 Bay Spring Ave       | 401 -246-2500 |https://atriaseniorliving.com   |

## Author
[Tadrous William](https://github.com/Tadrous-William) – Data Extraction & Cleaning
