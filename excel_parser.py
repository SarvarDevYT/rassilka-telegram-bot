import re
from pathlib import Path
from typing import Optional
import pandas as pd


def clean_phone_number(raw_val) -> Optional[str]:
    """
    Telefon raqamni tozalash va xalqaro formatga (+998...) keltirish.
    Noto'g'ri yoki yaroqsiz raqam bo'lsa None qaytaradi.
    """
    if raw_val is None or pd.isna(raw_val):
        return None

    # Raqam float bo'lib qolgan bo'lsa (masalan, Excelda 998901234567.0)
    if isinstance(raw_val, float):
        raw_val = int(raw_val)

    s = str(raw_val).strip()
    # Faqat raqamlar va '+' belgisini qoldirish
    cleaned = re.sub(r"[^\d+]", "", s)

    # '+' belgisi o'rtada kelib qolsa tozalash
    if cleaned.startswith("+"):
        digits = cleaned[1:]
    else:
        digits = cleaned

    if not digits.isdigit():
        return None

    # O'zbekiston raqamlari qoidalari:
    # 9 xonali: 901234567 -> +998901234567
    if len(digits) == 9:
        return f"+998{digits}"
    # 12 xonali va 998 bilan boshlansa
    elif len(digits) == 12 and digits.startswith("998"):
        return f"+{digits}"
    # Boshqa xalqaro raqamlar (10 dan 15 xonagacha)
    elif 10 <= len(digits) <= 15:
        return f"+{digits}"

    return None


def detect_columns(df: pd.DataFrame) -> tuple[Optional[str], Optional[str]]:
    """
    Excel jadvalidan telefon raqam va ism ustunlarini avtomatik aniqlash.
    """
    phone_col = None
    name_col = None

    phone_keywords = ["telefon", "phone", "tel", "nomer", "aloqa", "raqam", "mobile", "contact"]
    name_keywords = ["ism", "name", "fio", "mijoz", "full_name", "first_name"]

    # 1. Ustun nomlari bo'yicha qidirish
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if not phone_col and any(k in col_lower for k in phone_keywords):
            phone_col = col
        elif not name_col and any(k in col_lower for k in name_keywords):
            name_col = col

    # 2. Agar telefon ustuni topilmasa, qiymatlarga qarab aniqlash
    if not phone_col:
        for col in df.columns:
            sample_values = df[col].dropna().head(10)
            valid_count = sum(1 for val in sample_values if clean_phone_number(val) is not None)
            if valid_count >= max(1, len(sample_values) // 2):
                phone_col = col
                break

    return phone_col, name_col


def parse_excel_file(file_path: Path | str) -> dict:
    """
    Excel faylini (.xlsx, .xls) o'qib, telefon raqamlar va ismlarni chiqarib beradi.
    Deduplikatsiya (takrorlangan raqamlarni tozalash) mavjud.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fayl topilmadi: {path}")

    # Fayl kengaytmasini tekshirish
    if path.suffix.lower() not in [".xlsx", ".xls", ".csv"]:
        raise ValueError("Faqat .xlsx, .xls yoki .csv formatdagi fayllar qo'llab-quvvatlanadi.")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    if df.empty:
        raise ValueError("Excel fayl bo'sh!")

    phone_col, name_col = detect_columns(df)

    if not phone_col:
        available_cols = ", ".join([str(c) for c in df.columns])
        raise ValueError(
            f"Fayldan telefon raqam ustuni topilmadi. Mavjud ustunlar: {available_cols}.\n"
            f"Iltimos, telefon raqam ustuni sarlavhasini 'Telefon' yoki 'Phone' deb nomlang."
        )

    records = []
    seen_phones = set()
    invalid_rows = 0

    for idx, row in df.iterrows():
        raw_phone = row[phone_col]
        cleaned_phone = clean_phone_number(raw_phone)

        if not cleaned_phone:
            invalid_rows += 1
            continue

        if cleaned_phone in seen_phones:
            continue

        seen_phones.add(cleaned_phone)

        name = ""
        if name_col and not pd.isna(row[name_col]):
            name = str(row[name_col]).strip()

        records.append({
            "row_index": idx + 2,  # Excel qatori (header 1-qator bo'lgani uchun +2)
            "phone": cleaned_phone,
            "raw_phone": str(raw_phone),
            "name": name,
        })

    return {
        "total_rows": len(df),
        "valid_count": len(records),
        "invalid_count": invalid_rows,
        "phone_column": str(phone_col),
        "name_column": str(name_col) if name_col else None,
        "records": records,
    }
