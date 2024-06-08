import os
import zlib
import argparse

def read_file_path(sha_objectname):
    git_prefix = ".git/objects"
    file_path = f"{git_prefix}/{sha_objectname[:2]}/{sha_objectname[2:]}"
    print(file_path)
    try:
        with open(file_path, "rb") as f:
            return zlib.decompress(f.read())
    except (NotADirectoryError,FileNotFoundError):
        return None
    
def get_file_content(read_blob_object):
    # how shall i get the contents from the blob object
    result= read_blob_object.split(b"\x00")
    return result[1]
    
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #
    
    parser = argparse.ArgumentParser(description="A simple CLI example.")
    parser.add_argument("command", action="store", help="input git helper commands")
    parser.add_argument("-p",dest='hash_value' ,action="store",type=str, help="enable p flag")

    args = parser.parse_args()

    if args.command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif args.command == "cat-file":
        sha_value = args.hash_value
        # print("sha value is:",sha_value)
        read_blob_object = read_file_path(sha_value)
        # print(" fetching the file blob object")
        # print(read_blob_object)
        if read_blob_object:
            file_contents=get_file_content(read_blob_object)
            print(file_contents.decode('utf-8'))
    else:
        raise RuntimeError(f"Unknown command #{args.command}")


if __name__ == "__main__":
    main()
