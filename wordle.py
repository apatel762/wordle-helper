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


def get_result_value(result_char: int) -> int:
    if result_char == GREEN:
        return 0
    if result_char == YELLOW:
        return 1
    if result_char == INCORRECT:
        return 2

    raise RuntimeError(f"cannot get result value for {result_char}")


def filter_dictionary(
    dictionary: dict[str, float], guessed_word: str, guess_result: str
) -> dict[str, float]:
    if not validate_guess(s=guess_result, check_dictionary=False):
        raise RuntimeError("cannot filter dictionary with invalid guess result")

    # keep track of what we've seen so far
    # this will stop us from filtering out letters that we've already
    # confirmed to be correct in our previous guesses
    seen: dict[str, str] = {}

    for index, pair in sorted(
        enumerate(zip(guessed_word, guess_result)),
        key=lambda index_and_letter_result_pair: get_result_value(
            index_and_letter_result_pair[1][1]
        ),
    ):
        letter: str = pair[0]
        result: str = pair[1]
        print(f"debug: {index=}, {letter=}, {result=}")
        if result == GREEN:
            # we got it correct!
            dictionary = {w: f for w, f in dictionary.items() if w[index] == letter}
        elif result == YELLOW:
            # letter is in the word, but in a different position to where we guessed
            dictionary = {
                w: f
                for w, f in dictionary.items()
                if letter in w and w[index] != letter
            }
        elif result == INCORRECT:
            # only filter out words containing this letter if we have not already
            # confirmed that it's in the word
            if letter in seen.keys() and seen[letter] in (YELLOW, GREEN):
                dictionary = {w: f for w, f in dictionary.items() if w[index] != letter}
            else:
                # letter is not in the word
                dictionary = {w: f for w, f in dictionary.items() if letter not in w}

        if letter not in seen.keys():
            seen[letter] = result

    return dictionary


def pretty_print_most_frequent_words(
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
    number_of_guesses: int = 1
    guesses_so_far: dict[str, str] = {}
    while number_of_guesses <= 6:
        is_valid: bool = False
        guess: str = ""
        while not is_valid:
            answers = inquirer.prompt(
                [inquirer.Text("name", message="What's your guess?")]
            )
            guess: str = clean(answers["name"])
            is_valid = validate_guess(guess)

        is_valid: bool = False
        result: str = ""
        while not is_valid:
            answers = inquirer.prompt(
                [inquirer.Text("result", message="What was the result?")]
            )
            result: str = clean(
                answers["result"], whitelisted_chars=ALLOWED_RESULTS_CHARS
            )
            is_valid = validate_guess(result, check_dictionary=False)

        # pretty-print the current guess & result
        guesses_so_far[guess] = beautify_results(r=result)
        if result == GREEN * 5:
            print("")
            print("Congratulations!")
            print("")
            print("Below are the guesses that you made:")
            print("")
            for guess, emoji_representation in guesses_so_far.items():
                print(f"{guess} {emoji_representation}")
            break

        words_with_frequencies: dict[str, float] = filter_dictionary(
            dictionary=words_with_frequencies, guessed_word=guess, guess_result=result
        )

        print("Try one of these words for your next guess:")
        print("")
        # todo: pretty-print the most frequent words
        pretty_print_most_frequent_words(
            dictionary_of_words_with_frequencies=words_with_frequencies
        )

        number_of_guesses += 1

    print("")
    print("Sorry! You ran out of guesses.")
