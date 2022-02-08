import itertools
import json
import string
import unicodedata
from typing import List

import inquirer


def read_dictionary_file(
    path: str = "./data/dictionary_with_frequency.json",
) -> dict[str, float]:
    with open(path, "r") as f:
        return json.load(f)


words_with_frequencies: dict[str, float] = read_dictionary_file()


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
        print(f"Bad guess: {s} (not five letters long)")
        return False

    if check_dictionary and s not in words_with_frequencies:
        print(f"Bad guess: {s} (not in dictionary)")
        return False

    return True


INCORRECT: str = " "
YELLOW: str = "Y"
GREEN: str = "G"

ALLOWED_RESULTS_CHARS: str = "".join([INCORRECT, YELLOW, GREEN]).lower()


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


def filter_dictionary(
    dictionary: dict[str, float], guessed_word: str, guess_result: str
) -> dict[str, float]:
    if not validate_guess(s=guess_result, check_dictionary=False):
        raise RuntimeError("cannot filter dictionary with invalid guess result")

    for index, pair in enumerate(zip(guessed_word, guess_result)):
        letter: str = pair[0]
        result: str = pair[1]
        if result == INCORRECT:
            dictionary = {w: f for w, f in dictionary.items() if letter not in w}
        elif result == YELLOW:
            dictionary = {w: f for w, f in dictionary.items() if letter in w}
        elif result == GREEN:
            dictionary = {w: f for w, f in dictionary.items() if w[index] == letter}

    return dictionary


def get_most_frequent_words(
    dictionary_of_words_with_frequencies: dict[str, float], limit: int = 10
) -> List[str]:
    sorted_dict: dict[str, float] = dict(
        sorted(
            dictionary_of_words_with_frequencies.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    )
    for word, freq in itertools.islice(sorted_dict.items(), limit):
        print(f"{word} ({freq=})")


if __name__ == "__main__":
    # number_of_guesses: int = 0
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
        result: str = clean(answers["result"], whitelisted_chars=ALLOWED_RESULTS_CHARS)
        is_valid = validate_guess(result, check_dictionary=False)

    # pretty-print the current guess & result
    print("")
    print(f"{guess} -> {beautify_results(r=result)}")

    # filter the dictionary down based on what was revealed
    # show the top 10 most likely guesses based on the information we have
    #   need to find a list of the most common english 5-letter words from somewhere
    # rinse and repeat
    print("filtering results...")
    print(f"before filtering: {len(words_with_frequencies)} results")
    words_with_frequencies: dict[str, float] = filter_dictionary(
        dictionary=words_with_frequencies, guessed_word=guess, guess_result=result
    )
    print(f"after filtering: {len(words_with_frequencies)} results")

    print("pick one of the below words:")
    print("")
    words: List[str] = get_most_frequent_words(words_with_frequencies)
