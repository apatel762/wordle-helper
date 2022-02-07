import string
import unicodedata
from typing import List

import inquirer


def read_dictionary_file(path: str = "./data/dictionary.txt") -> List[str]:
    tmp: List[str] = []
    with open(path, "r") as f:
        for line in f.readlines():
            word: str = line.replace("\n", "")
            tmp.append(word)
    return tmp


words: List[str] = read_dictionary_file()


def clean(s: str, whitelisted_chars: str = string.ascii_letters) -> str:
    max_length: int = 5

    # keep only valid ascii chars
    cleaned_string: str = (
        unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode()
    )

    # keep only whitelisted chars
    cleaned_string: str = "".join(c for c in cleaned_string if c in whitelisted_chars)

    # truncate the guess to the maximum allowed number of letters
    return cleaned_string[:max_length].upper()


def validate_guess(s: str, check_dictionary: bool = True) -> bool:
    if len(s) != 5:
        print(f"Bad guess: {s} (not five letters long")
        return False

    if check_dictionary and s not in words:
        print(f"Bad guess: {s} (not in dictionary)")
        return False

    return True


if __name__ == "__main__":
    number_of_guesses: int = 0
    is_valid: bool = False
    guess: str = ""
    while not is_valid:
        answers = inquirer.prompt([inquirer.Text("name", message="guess")])
        guess: str = clean(answers["name"])
        is_valid = validate_guess(guess)

    print(f"{guess=}")

    is_valid: bool = False
    while not is_valid:
        answers = inquirer.prompt([inquirer.Text("result", message="result")])
        result: str = clean(answers["result"], whitelisted_chars="_ yg")
        is_valid = validate_guess(result, check_dictionary=False)

    # filter the dictionary down based on what was revealed
    # rinse and repeat somehow
