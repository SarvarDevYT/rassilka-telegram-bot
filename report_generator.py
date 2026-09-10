from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd
from config import REPORTS_DIR


def generate_excel_report(results: list[dict[str, Any]], campaign_name: str = "Rassilka") -> Path:
    """
    Rassilka natijalaridan chiroyli Excel hisobot faylini yaratadi.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"report_{timestamp}.xlsx"
    report_path = REPORTS_DIR / report_filename

    rows = []
    for idx, item in enumerate(results, start=1):
        status_code = item.get("status", "UNKNOWN")

        if status_code == "SENT":
            status_text = "✅ Yuborildi"
            has_tg = "Bor"
        elif status_code == "NO_TELEGRAM":
            status_text = "❌ Yuborilmadi"
            has_tg = "Yo'q"
        elif status_code == "PRIVACY_RESTRICTED":
            status_text = "⚠️ Yuborilmadi (Maxfiylik)"
            has_tg = "Bor"
        elif status_code == "FLOOD_BLOCKED":
            status_text = "⛔ To'xtatildi (Telegram limit)"
            has_tg = "Noma'lum"
        else:
            status_text = f"❌ Xato ({status_code})"
            has_tg = "Noma'lum"

        rows.append({
            "№": idx,
            "Telefon raqam": item.get("phone", ""),
            "Mijoz ismi": item.get("name", ""),
            "Telegram bormi": has_tg,
            "Xabar holati": status_text,
            "Batafsil ma'lumot": item.get("details", ""),
            "Yuborilgan vaqt": item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        })

    df = pd.DataFrame(rows)

    # Excel faylga saqlash
    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Hisobot", index=False)

        # Ustun kengliklarini moslash
        worksheet = writer.sheets["Hisobot"]
        for col in worksheet.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    return report_path
