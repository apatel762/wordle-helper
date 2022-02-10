import itertools
import json
import string
import unicodedata
from typing import List


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


INCORRECT: str = "_"
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


def show_tutorial_text() -> None:
    print(
        """
    HOW TO USE THIS SCRIPT
    ======================

    Open up wordle @ https://www.powerlanguage.co.uk/wordle/
    and take your first guess.

    Once you can see the result of your guess, enter it below
    and after that, you'll be prompted to enter the result of
    the guess - do that as well.

    The result be a string of five letters representing the
    answer, see examples below:

    🟩⬛⬛🟨⬛ = g__y_
    ⬛🟨⬛🟩🟩 = _y_gg
    🟩🟩🟩🟩🟩 = ggggg

    etc.

    Have fun!
    """
    )


def get_long_line(line_character: str = "-", length: int = 72) -> str:
    return line_character * length


def print_long_line() -> None:
    print(get_long_line())


def print_spacer_line() -> None:
    print("")


if __name__ == "__main__":
    show_tutorial_text()

    number_of_guesses: int = 1
    guesses_so_far: dict[str, str] = {}
    while number_of_guesses <= 6:
        print_spacer_line()

        print_long_line()
        print(f"GUESS NUMBER {number_of_guesses}")
        print(get_long_line(line_character="~", length=14))
        print_spacer_line()
        is_valid: bool = False
        guess: str = ""
        while not is_valid:
            guess: str = clean(input("Enter your guess> "))
            is_valid = validate_guess(guess)

        is_valid: bool = False
        result: str = ""
        while not is_valid:
            result: str = clean(
                input("Enter the result> "), whitelisted_chars=ALLOWED_RESULTS_CHARS
            )
            is_valid = validate_guess(result, check_dictionary=False)

        guesses_so_far[guess] = beautify_results(r=result)
        # if the guess is correct, end the script here and dump all
        # guesses and results
        if result == GREEN * 5:
            print_spacer_line()
            print("Congratulations!")
            print_spacer_line()
            print(f"Wordle {number_of_guesses}/6")
            print_spacer_line()
            for _, emoji_representation in guesses_so_far.items():
                print(f"{emoji_representation}")
            print_spacer_line()
            print("Your guesses were:")
            for guess, _ in guesses_so_far.items():
                print(f"{guess}")
            break

        words_with_frequencies: dict[str, float] = filter_dictionary(
            dictionary=words_with_frequencies, guessed_word=guess, guess_result=result
        )

        print_spacer_line()
        print("Try one of these words for your next guess:")
        print_spacer_line()
        # todo: pretty-print the most frequent words
        pretty_print_most_frequent_words(
            dictionary_of_words_with_frequencies=words_with_frequencies
        )

        number_of_guesses += 1
    else:
        print_spacer_line()
        print("Sorry! You ran out of guesses.")
        print_spacer_line()
        print("Wordle X/6")
        for _, emoji_representation in guesses_so_far.items():
            print(f"{emoji_representation}")
        print_spacer_line()
        print("Your guesses were:")
        for guess, _ in guesses_so_far.items():
            print(f"{guess}")
