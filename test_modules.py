import openpyxl
from excel_parser import parse_excel_file
from report_generator import generate_excel_report
from pathlib import Path

def test_modules():
    test_file = Path("test_data.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mijozlar"
    
    # Headers
    ws.append(["№", "Mijoz Ismi", "Telefon"])
    # Sample rows
    ws.append([1, "Ali Valiyev", "+998 90 123-45-67"])
    ws.append([2, "Nodir Karimov", "998935556677"])
    ws.append([3, "Sarvar", "919876543"])
    ws.append([4, "Mavjud Emas", "abc-not-a-phone"])
    ws.append([5, "Takroriy Ali", "+998901234567"])  # duplicate
    
    wb.save(test_file)
    print("Test Excel yaratildi.")

    parsed = parse_excel_file(test_file)
    print(f"Jami qatorlar: {parsed['total_rows']}")
    print(f"Toza raqamlar: {parsed['valid_count']}")
    print(f"Yaroqsiz: {parsed['invalid_count']}")
    print(f"Topilgan ustunlar: tel='{parsed['phone_column']}', ism='{parsed['name_column']}'")
    assert parsed['valid_count'] == 3, f"Kutilgan 3 ta, lekin {parsed['valid_count']} chiqdi"
    
    # Test report generator
    sample_results = [
        {"phone": "+998901234567", "name": "Ali Valiyev", "status": "SENT", "details": "Yetkazildi"},
        {"phone": "+998935556677", "name": "Nodir", "status": "NO_TELEGRAM", "details": "Telegram yo'q"},
    ]
    report_path = generate_excel_report(sample_results)
    print(f"Hisobot yaratildi: {report_path}")
    assert report_path.exists(), "Hisobot fayli yaratilmadi!"
    
    # Clean up test file
    test_file.unlink(missing_ok=True)
    print("[MUVAFFAQIN! Barcha parser va hisobot testlari to'liq o'tdi!]")

if __name__ == "__main__":
    test_modules()
