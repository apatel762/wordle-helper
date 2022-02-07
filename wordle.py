def read_dictionary_file(path: str = "./data/dictionary.txt"):
    with open(path, "r") as f:
        for line in f.readlines():
            word: str = line.replace("\n", "")
            yield word


if __name__ == "__main__":
    for word in read_dictionary_file():
        print(f"{word=}")
