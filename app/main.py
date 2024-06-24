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
            content = f"blob {len(contents)}\x00{contents.decode("utf-8")}".encode("ascii")
            hex_value = hashlib.sha1(content).hexdigest()
            return zlib.compress(content), hex_value
    except FileNotFoundError:
        return None


def write_blob_object(sha_value, content):

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
        list_of_paths=[]
        for name in dirs:
            dir_path = os.path.join(root, name)
            list_of_paths.append(dir_path)
            print(f"Directory: {dir_path}")
            
        for filename in files:
            file_path = os.path.join(root, filename)
            list_of_paths.append(file_path)
            print(f"{file_path}")
        
        #write tree object
        st.append(list_of_paths)


    # Usage
    # directory_path = "/path/to/your/directory"
    # list_recursive_contents(directory_path)


def write_tree_object(input_array):
    file_info =[]
    for each_path in input_array:
        if each_path.os.path.isfile():
            compressed_contents, hash_value = create_blob_object(each_path)
            write_blob_object(hash_value, compressed_contents)
            print(hash_value, end="")
            file_info.append((each_path,hash_value))
        
        elif each_path.os.path.isdir():
            if len(file_info)>0:
                
               pass 
    

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
        write_blob_object(hash_value, compressed_contents)
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
        
        
        

    else:
        raise RuntimeError(f"Unknown command #{args.command}")


if __name__ == "__main__":
    main()
