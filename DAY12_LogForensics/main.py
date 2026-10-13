import re
import ipaddress
from pathlib import Path
from collections import Counter

email = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
ip_pattern = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
timestamp = re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b")
sus = re.compile(r"\b(?:failed|unauthorized|injection|permission denied)\b" , re.IGNORECASE,)

def get_path():
    raw_path = input("Enter the log file path : ").strip()
    return Path(raw_path.strip('"'))

def analyze_files(file_path):
    stats = {
        "lc": 0,
        "emails": Counter(),
        "ips": Counter(),
        "timestamps": Counter(),
        "sus_count": 0,
        "sus_ex": [],
    }
    try:
        with file_path.open("r" , encoding="utf-8" , errors = "replace") as file:
            for line_num , line in enumerate(file , start=1):
                stats["lc"] += 1
                emails = email.findall(line)
                stats["emails"].update(emails)
                for candidate in ip_pattern.findall(line):
                    try:
                        address = ipaddress.IPv4Address(candidate)
                        stats["ips"][str(address)] += 1
                    except ipaddress.AddressValueError:
                        continue
                timestamps = timestamp.findall(line)
                stats["timestamps"].update(timestamps)
                if sus.search(line):
                    stats["sus_count"] += 1
                    if len(stats["sus_ex"]) < 5:
                        stats["sus_ex"].append((line_num , line.strip()))
    except OSError as error:
        print(f"Error reading file: {error}")
        return None
    return stats

def print_rep(file_path , stats):
    print("+=+=+= Log Forensics Report =+=+=+")
    print(f"File : {file_path}")
    print(f"Lines processed : {stats["lc"]}")
    print(f"Email matches: {sum(stats["emails"].values())}")
    for email , count in stats["emails"].most_common(5):
        print(f"{email} - {count} occurences")
    print(f"Valid IPv4 matches: {sum(stats["ips"].values())}")
    for address , count in stats["ips"].most_common(5):
        print(f"{address} - {count} occurences")
    print(f"Timestamp mathces : {sum(stats["timestamps"].values())}")
    for timestamp , count in stats["timestamps"].most_common(5):
        print(f"{timestamp} - {count} occurences")
    print(f"Suspicious lines : {stats["sus_count"]}")
    for line_num , text in stats["sus_ex"]:
        print(f"Line {line_num}: {text}")
    print("_"*45)

def main():
    file_path = get_path()
    stats = analyze_files(file_path)
    if stats is None:
        return
    print_rep(file_path , stats)

main()