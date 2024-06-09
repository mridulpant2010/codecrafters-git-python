import os
import zlib
import argparse
import hashlib


def read_file_path(sha_objectname):
    git_prefix = ".git/objects"
    file_path = f"{git_prefix}/{sha_objectname[:2]}/{sha_objectname[2:]}"
    try:
        with open(file_path, "rb") as f:
            return zlib.decompress(f.read())
    except (NotADirectoryError, FileNotFoundError):
        return None


def get_file_content(read_blob_object):
    result = read_blob_object.split(b"\x00")
    return result[-1]


def create_blob_object(file_name):
    try:
        with open(file_name, "rb") as f:
            contents = f.read()
            content = f"blob {len(contents)}\x00{contents.decode("utf-8")}".encode("ascii")
            hex_value = hashlib.sha1(content).hexdigest()
            return zlib.compress(content), hex_value
    except FileNotFoundError:
        return None


def write_blob_object(sha_value, content):
    
    git_prefix = ".git/objects"
    file_path = f"{git_prefix}/{sha_value[:2]}/{sha_value[2:]}"
    try:
        git_path=os.path.join(os.getcwd(),git_prefix)
        os.mkdir(os.path.join(git_path,sha_value[:2]))
        with open(file_path, "wb") as f:
            f.write(content)
    except FileNotFoundError:
        return None


def main():
    parser = argparse.ArgumentParser(description="A simple CLI example.")
    parser.add_argument("command", action="store", help="input git helper commands")
    parser.add_argument(
        "-p", dest="hash_value", action="store", type=str, help="enable p flag"
    )

    parser.add_argument(
        "-w", dest="write_file", action="store", help="write output to file"
    )

    args = parser.parse_args()

    if args.command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
    elif args.command == "cat-file":
        sha_value = args.hash_value
        read_blob_object = read_file_path(sha_value)
        if read_blob_object:
            file_contents = get_file_content(read_blob_object)
            print(file_contents.decode("utf-8"), end="")
    elif args.command == "hash-object":
        file_name = args.write_file
        compressed_contents, hash_value = create_blob_object(file_name)
        write_blob_object(hash_value, compressed_contents)
        print(hash_value, end="")

    else:
        raise RuntimeError(f"Unknown command #{args.command}")


if __name__ == "__main__":
    main()
