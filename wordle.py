if __name__ == "__main__":
    # todo: actually do something with the dictionary
    with open("./data/dictionary.txt", "r") as f:
        for word in f.readlines():
            print(word)
