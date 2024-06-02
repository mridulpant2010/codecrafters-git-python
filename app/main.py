import os
import zlib
import argparse


def read_compressed_data():
    pass


def read_file_path():
    git_prefix = ".git"
    file_path = f"{git_prefix}/{}"
    





def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #
    
    parser = argparse.ArgumentParser(description="A simple CLI example.")
    parser.add_argument("command", action="store_true", help="input git helper commands")
    parser.add_argument("-p", action="store_true", help="enable p flag")

    args = parser.parse_args()

    if args.command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif args.command == "cat-file":
        sha_value = args.p
        subdir_path = sha_value[:2]
        object_name = sha_value[2:]
        
        
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
