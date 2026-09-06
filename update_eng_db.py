import sqlite3
import os

db_path = 'ENG.db'
cebb_path = 'CEBB.db'
vpl_path = 'eng-asv_vpl/eng-asv_vpl.txt'

# 1. Connect to DBs
eng_conn = sqlite3.connect(db_path)
cebb_conn = sqlite3.connect(cebb_path)
eng_c = eng_conn.cursor()
cebb_c = cebb_conn.cursor()

# 2. Extract books from CEBB.db
cebb_c.execute("SELECT id, name, osis_code, sort_order, testament FROM books ORDER BY id")
books = cebb_c.fetchall()

# 3. Insert books into ENG.db
eng_c.execute("DELETE FROM books")
eng_c.executemany("INSERT INTO books (id, name, osis_code, sort_order, testament) VALUES (?, ?, ?, ?, ?)", books)

# 4. Clear existing verses in ENG.db
eng_c.execute("DELETE FROM verses")

# 5. Mapping of 3-letter codes to book_id
book_codes = [
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO", "ECC", "SOL", "ISA", "JER", "LAM", "EZE", "DAN", "HOS", "JOE", "AMO", "OBA", "JON", "MIC", "NAH", "HAB", "ZEP", "HAG", "ZEC", "MAL", "MAT", "MAR", "LUK", "JOH", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH", "PHI", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAM", "1PE", "2PE", "1JO", "2JO", "3JO", "JUD", "REV"
]
code_to_id = {code: i for i, code in enumerate(book_codes)}

# 6. Parse and insert verses
translation_code = "ENG"
verses_to_insert = []

with open(vpl_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue

        book_code = parts[0]
        chap_verse = parts[1]
        text = parts[2]

        cv_parts = chap_verse.split(":")
        if len(cv_parts) != 2:
            continue

        chapter = int(cv_parts[0])
        verse = int(cv_parts[1])

        book_id = code_to_id[book_code]

        verses_to_insert.append((book_id, chapter, text, translation_code, verse))

eng_c.executemany("INSERT INTO verses (book_id, chapter, text, translation_code, verse) VALUES (?, ?, ?, ?, ?)", verses_to_insert)

# Ensure translations table is intact (should already be ENG | ENG | English-ASV, but let's be safe)
eng_c.execute("INSERT OR IGNORE INTO translations (code, language, name) VALUES ('ENG', 'ENG', 'English-ASV')")

eng_conn.commit()
eng_conn.close()
cebb_conn.close()

print(f"Inserted {len(verses_to_insert)} verses into ENG.db")
