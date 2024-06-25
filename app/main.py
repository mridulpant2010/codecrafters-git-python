import os
import zlib
import argparse
import hashlib


def read_object_path(sha_objectname):
    git_prefix = ".git/objects"
    file_path = f"{git_prefix}/{sha_objectname[:2]}/{sha_objectname[2:]}"
    try:
        with open(file_path, "rb") as f:
            return zlib.decompress(f.read())
    except (NotADirectoryError, FileNotFoundError):
        return None


def get_file_content(blob_object):
    result = blob_object.split(b"\x00")
    return result[-1]


def get_tree_content(tree_object, name_only):
    null_index = tree_object.index(b"\x00")
    size = int(tree_object[4:null_index])
    index = null_index + 1
    while index < len(tree_object):
        empty_index = tree_object.index(b" ", index)
        mode = tree_object[index:empty_index].decode()
        null_index = tree_object.index(b"\x00", index)
        name = tree_object[empty_index + 1 : null_index].decode()
        sha = tree_object[null_index + 1 : null_index + 21].hex()
        if not name_only:
            print("0" * (6 - len(mode)), end="")
            print(mode, end="")
            print(sha, end="\t")
        print(name)
        index = null_index + 21


def create_blob_object(file_name):
    try:
        with open(file_name, "rb") as f:
            contents = f.read()
            content = f"blob {len(contents)}\x00{contents}".encode("utf-8")
            hex_value = hashlib.sha1(content).hexdigest()
            return zlib.compress(content), hex_value
    except FileNotFoundError:
        return None


def write_object(sha_value, content):

    git_prefix = ".git/objects"
    file_path = f"{git_prefix}/{sha_value[:2]}/{sha_value[2:]}"
    try:
        git_path = os.path.join(os.getcwd(), git_prefix)
        os.mkdir(os.path.join(git_path, sha_value[:2]))
        with open(file_path, "wb") as f:
            f.write(content)
    except FileNotFoundError:
        return None

    # seems a bit tough right now, I am unable to figure out what needs to be done.


def list_recursive_contents(directory_path):
    st = []
    for root, dirs, files in os.walk(directory_path):
        # Exclude specific directory names (recursively)
        dirs[:] = [d for d in dirs if d not in (".git", ".gitattributes", ".gitignore")]
        list_of_paths = []
        for name in dirs:
            dir_path = os.path.join(root, name)
            list_of_paths.append(dir_path)
            # print(f"Directory: {dir_path}")

        for filename in files:
            file_path = os.path.join(root, filename)
            list_of_paths.append(file_path)
            # print(f"{file_path}")

        # write tree object
        st.append(list_of_paths)
    return st

    # Usage
    # directory_path = "/path/to/your/directory"
    # list_recursive_contents(directory_path)


def write_tree_object(input_array, prev_tree_object, prev_parent_path):
    tree_object = b""
    for each_path in input_array:
        if os.path.isfile(each_path):
            compressed_contents, hash_value = create_blob_object(each_path)
            write_object(hash_value, compressed_contents)
            # print(hash_value, end="")
            tree_object += f"100644 {each_path}\0".encode() + int.to_bytes(
                int(hash_value, base=16), length=20, byteorder="big"
            )  # hash_value  # each_path is the full

        elif os.path.isdir(each_path):
            # involve prev_tree_object
            # ? how to get the hash_value of a directory?
            if each_path in prev_parent_path:
                tree_object += (
                    f"40000 {each_path}\0".encode()  # ?: hash_value required or not?
                )  # each_path is the full
                tree_object += prev_tree_object  # TODO: datatype difference between tree_object and prev_tree_object?
                # write_tree_object(list_recursive_contents(each_path))
                prepend = f"tree {len(tree_object)}\x00".encode()
                content_to_hash = (
                    prepend + tree_object
                )  # ?: is it the right contents of the file?
                compressed_obj = zlib.compress(content_to_hash)
                hash_value = hashlib.sha1(content_to_hash).hexdigest()
                # hash_value = int.to_bytes(
                #     int(hash_value, base=16), length=20, byteorder="big"
                # )
                write_object(hash_value, compressed_obj)

        parent_path = each_path.split("/")[:-1]
        parent_path = "/".join(parent_path)
    return tree_object, parent_path, hash_value
    # return compressed tree_object? and the parent_file_path?


def main():
    parser = argparse.ArgumentParser(description="A simple CLI example.")
    parser.add_argument("command", action="store", help="input git helper commands")
    parser.add_argument(
        "-p", dest="hash_value", action="store", type=str, help="enable p flag"
    )

    parser.add_argument(
        "-w", dest="write_file", action="store", help="write output to file"
    )

    # parser.add_argument("sha_hash_value",action="store", default="",help="SHA hash value for tree objects")
    parser.add_argument(
        "--name-only",
        dest="name_only",
        action="store",
        help="only prints the alphabetical names of file contents.",
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
        read_blob_object = read_object_path(sha_value)
        if read_blob_object:
            file_contents = get_file_content(read_blob_object)
            print(file_contents.decode("utf-8"), end="")
    elif args.command == "hash-object":
        file_name = args.write_file
        compressed_contents, hash_value = create_blob_object(file_name)
        write_object(hash_value, compressed_contents)
        print(hash_value, end="")
    elif args.command == "ls-tree":
        sha_value = args.name_only
        tree_object = read_object_path(sha_value)
        condition = args.name_only is not None
        # print(tree_object, end="")
        get_tree_content(tree_object, condition)
    elif args.command == "write-tree":
        # do we have to create a tree object file which will have the entire details?
        # find the contents of the file
        directory_path = os.getcwd()
        prev_tree_object, prev_parent_path = b"", None
        result = list_recursive_contents(directory_path)
        print(result)
        while len(result) > 0:
            ans = result.pop()
            print("level -> ",ans)
            prev_tree_object, prev_parent_path, sha_value = write_tree_object(
                ans, prev_tree_object, prev_parent_path
            )
            print(prev_tree_object, prev_parent_path,sha_value)
        print(sha_value)

    else:
        raise RuntimeError(f"Unknown command #{args.command}")


if __name__ == "__main__":
    main()
