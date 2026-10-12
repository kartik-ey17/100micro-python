from pathlib import Path
from collections import Counter

def get_dir():
    raw_path = input("Enter the directory path to analyze: ").strip()
    return Path(raw_path)

def validate_dir(dir):
    if not dir.exists():
        print("Error: This path does not exist.")
        return False
    if not dir.is_dir():
        print("Error: The path is not a directory.")
        return False
    return True

def scan_dir(dir):
    ext_counts = Counter()
    file_records = []
    total_size = 0
    skipped_files = 0
    try:
        entries = list(dir.iterdir())
    except OSError as error:
        print(f"Error: Cannot read this directory: {error}")
        return None
    for entry in entries:
        try:
            if not entry.is_file():
                continue
            size = entry.stat().st_size
            ext = entry.suffix.lower() or "[no extension]"
            ext_counts[ext] += 1
            file_records.append((size , entry.name))
            total_size += size
        except OSError:
            skipped_files += 1
            continue
    return {
        "file_count": len(file_records),
        "total_size": total_size,
        "ext_counts": ext_counts,
        "largest_files": sorted(file_records , reverse=True)[:5],
        "skipped_files": skipped_files,
    }

def format_size(size):
    units = ["B" , "KB" , "MB" , "GB" , "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == "TB":
            return f"{value:.2f}{unit}"
        value /= 1024
    return f"{value:.2f} TB"

def print_report(dir , stats):
    print("+=+=+= Directory Analysis Report =+=+=+")
    print(f"Directory: {dir}")
    print(f"Files scanned: {stats['file_count']}")
    print(f"Total size: {format_size(stats['total_size'])}")
    print(f"Files skipped: {stats['skipped_files']}")
    print("\nFile counts by extension : ")
    if stats["ext_counts"]:
        for ext , count in stats["ext_counts"].most_common():
            print(f"{ext:<18} {count}")
    else:
        print("No files found.")
    print("\nFive largest files: ")
    if stats["largest_files"]:
        for size , filename in stats["largest_files"]:
            print(f"{format_size(size):>12} {filename}")
    else:
        print("No files found.")
    print("_"*45)

def main():
    dir = get_dir()
    if not validate_dir(dir):
        return
    stats = scan_dir(dir)
    if stats is None:
        return
    print_report(dir , stats)

main()