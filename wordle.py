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


INCORRECT = " "
YELLOW = "Y"
GREEN = "G"


def map_result_to_emoji(result_char: str) -> str:
    if len(result_char) != 1:
        raise RuntimeError("expected result char to be a single char")

    if result_char == INCORRECT:
        return "⬛"
    elif result_char == YELLOW:
        return "🟨"
    elif result_char == GREEN:
        return "🟩"


def beautify_results(r: str) -> str:
    """
    r = result
    """
    return "".join([map_result_to_emoji(c) for c in r])


if __name__ == "__main__":
    number_of_guesses: int = 0
    is_valid: bool = False
    guess: str = ""
    while not is_valid:
        answers = inquirer.prompt([inquirer.Text("name", message="guess")])
        guess: str = clean(answers["name"])
        is_valid = validate_guess(guess)

    is_valid: bool = False
    result: str = ""
    while not is_valid:
        answers = inquirer.prompt([inquirer.Text("result", message="result")])
        result: str = clean(answers["result"], whitelisted_chars=" yg")
        is_valid = validate_guess(result, check_dictionary=False)

    # pretty-print the current guess & result
    print("")
    print(guess)
    print(beautify_results(r=result))

    # filter the dictionary down based on what was revealed
    # show the top 10 most likely guesses based on the information we have
    #   need to find a list of the most common english 5-letter words from somewhere
    # rinse and repeat
