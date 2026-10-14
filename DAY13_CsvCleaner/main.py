import csv
from pathlib import Path
from decimal import Decimal , InvalidOperation

req_fields = ["name" , "category" , "amount"]

def get_path():
    in_path = Path(input("Enter input CSV Path: ").strip().strip('"'))
    out_path = Path(input("Enter output CSV Path : ").strip().strip('"'))
    return in_path,out_path

def normalization(row):
    name = (row.get("name") or "").strip().title()
    category= (row.get("category") or "").strip().title()
    raw_amount = (row.get("amount") or "").strip()

    reason = []
    if not name:
        reason.append("Name is missing.")
    if not category:
        reason.append("Category is missing.")
    try:
        amount = Decimal(raw_amount)
        if not amount.is_finite():
            reason.append("amount must be finite")
        elif amount < 0:
            reason.append("Amount should not be negative")
    except InvalidOperation:
        amount = None
        reason.append("Amount is not a valid number.")

    if reason:
        return None , reason

    return {
        "name" : name,
        "category": category,
        "amount": f"{amount:.2f}",
    } , []

def clean(in_path , out_path):
    if not in_path.is_file():
        print("Error : input file does not exist or is not a file/")
        return None
    if in_path.resolve() == out_path.resolve():
        print("Error : Input and output paths cannot be same.")
        return None

    stats = {
        "processed": 0,
        "cleaned": 0,
        "rejected": 0,
        "reasons": {},
    }

    try:
        with in_path.open("r" , newline="" , encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)

            if (not reader.fieldnames or not all(field in reader.fieldnames for field in req_fields)):
                print("Error: csv is missing required colunms. For now , only name , category and amount are the allowed fields.")
                return None
            with out_path.open("w" , newline="" , encoding="utf-8") as destination:
                writer = csv.DictWriter(destination , fieldnames=req_fields,extrasaction="ignore")
                writer.writeheader()

                for line_num , row in enumerate(reader , start=2):
                    stats["processed"] += 1
                    if None in row:
                        cleaned_record = None
                        reason = ["too many columns."]
                    elif any(value is None for value in row.values()):
                        cleaned_record = None
                        reason = ["missing column value"]
                    else:
                        cleaned_record , reason = normalization(row)
                    if cleaned_record is not None:
                        writer.writerow(cleaned_record)
                        stats["cleaned"] += 1
                    else:
                        stats["rejected"] += 1
                        stats["reasons"][line_num] = reason
    except (OSError , csv.Error , UnicodeError) as error:
        print(f"Error processing CSV - {error}.")
        return None
    return stats

def summary(stats):
    print("+=+=+= CSV Cleaning Report =+=+=+")
    print(f"Rows processed : {stats["processed"]}")
    print(f"Rows Cleaned : {stats["cleaned"]}")
    print(f"Rows Rejected : {stats["rejected"]}")
    if stats["reasons"]:
        print("Rejected rows : ")
        for line_num , reason in stats["reasons"].items():
            print(f"CSV line {line_num}: {' , '.join(reason)}")
    else:
        print("No rows were rejected.")

    print("_"*60)

def main():
    in_path , out_path = get_path()
    stats = clean(in_path , out_path)
    if stats is None:
        return
    summary(stats)
    print(f"Cleaned data saved to : {out_path}")

main()