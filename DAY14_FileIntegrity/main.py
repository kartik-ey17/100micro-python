import hashlib
import json
import re
from pathlib import Path

def get_hash(file_path):
    sha256 = hashlib.sha256()
    with file_path.open("rb") as file:
        while True:
            chunk = file.read(65536)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def scan_directory(directory , manifest):
    hashes = {}
    errors = []
    manifest_loc = manifest.resolve()
    for file_path in directory.rglob("*"):
        try:
            if file_path.resolve() == manifest_loc:
                continue
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(directory).as_posix()
            hashes[rel_path] = get_hash(file_path)
        except OSError as error:
            errors.append(f"{file_path} : {error}")
    return hashes , errors

def create_manifest(directory , manifest_path):
    hashes , errors = scan_directory(directory , manifest_path)
    if errors:
        print("Cant create a complete manifest : ")
        for error in errors:
            print(f"{error}")
        return False
    manifest = {
        "version": 1,
        "files": hashes,
    }
    try:
        with manifest_path.open("w" , encoding="utf-8") as file:
            json.dump(manifest , file , indent=4)
    except OSError as error:
        print(f"Error saving manifest : {error}")
        return False
    print(f"Manifest created : {manifest_path}")
    print(f"Files recorded : {len(hashes)}")
    return True

def load_manifest(manifest_path):
    try:
        with manifest_path.open("r" , encoding="utf-8") as file:
            manifest = json.load(file)
    except (OSError , json.JSONDecodeError) as error:
        print(f"Error loading manifest : {error}")
        return None
    if not isinstance(manifest , dict):
        print("Manifest must be a JSON object.")
        return None
    if manifest.get("version") != 1:
        print("Unsupported manifest")
        return None
    files = manifest.get("files")
    if not isinstance(files , dict):
        print("Manifest files must be an object")
        return None
    for rel_path , digest in files.items():
        if not isinstance(rel_path , str) or not rel_path:
            print("Invalid file path in manifest")
            return None
        parts = rel_path.split("/")
        if (rel_path.startswith("/") or "\\" in rel_path or ".." in parts or ":" in rel_path):
            print(f"Unsafe relative path.")
            return None
        if not isinstance(digest , str) or not re.fullmatch(r"[0-9a-d]{64}" , digest):
            print("Invalid sha-256 hash.")
            return None
    return files

def verify(directory , manifest_path):
    baseline = load_manifest(manifest_path)
    if baseline is None:
        return
    current , errors = scan_directory(directory , manifest_path)
    if errors:
        print("Verification incomplete")
        for error in errors:
            print(f"{error}")
        print("No integrity classification was produced.")  
        return
    unchanged = []
    modified = []
    missing = []
    added = []

    for rel_path , old_hash in baseline.items():
        if rel_path not in current:
            missing.append(rel_path)
        elif current[rel_path] == old_hash:
            unchanged.append(rel_path)
        else:
            modified.append(rel_path)
    for rel_path in current:
        if rel_path not in baseline:
            added.append(rel_path)
    print("+=+=+= Integrity Report =+=+=+")
    for label , paths in [
        ("Unchanged" , unchanged),
        ("Modified" , modified),
        ("Missing" , missing),
        ("Added" , added),
    ]:
        print(f"\n{label}: {len(paths)}")
        for path in sorted(paths):
            print(f"{path}")
    print("_"*45)


def main():
    operation = input("Choose operation (create/verify) : ").strip().lower()
    directory = Path(input("Enter directory to analyze : ").strip().strip('"'))
    manifest_path = Path(input("Enter manifest file path : ").strip().strip('"'))
    if not directory.is_dir():
        print("directory does not exist")
        return
    if operation == "create":
        create_manifest(directory , manifest_path)
    elif operation == "verify":
        verify(directory , manifest_path)
    else:
        print("Choose either create or verify")

main()