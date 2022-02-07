import string
import unicodedata
from typing import List

import inquirer


def read_dictionary_file(path: str = "./data/dictionary.txt") -> List[str]:
    with open(path, "r") as f:
        for line in f.readlines():
            word: str = line.replace("\n", "")
            yield word


words: List[str] = read_dictionary_file()


def clean(s: str) -> str:
    valid_filename_chars: str = string.ascii_letters
    max_length: int = 5

    # keep only valid ascii chars
    cleaned_string: str = (
        unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode()
    )

    # keep only whitelisted chars
    cleaned_string: str = "".join(
        c for c in cleaned_string if c in valid_filename_chars
    )

    # truncate the guess to the maximum allowed number of letters
    return cleaned_string[:max_length]


def validate_guess(s: str) -> bool:
    if len(s) != 5:
        return False

    if s not in words:
        return False

    return True


if __name__ == "__main__":
    valid: bool = False
    guess: str = ""
    while not valid:
        answers = inquirer.prompt(
            [inquirer.Text("name", message="What is your guess?")]
        )
        guess: str = clean(answers["name"])
        valid = validate_guess(guess)

    print(f"{guess=}")
