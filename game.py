from collections import Counter, defaultdict

from utils import load_words, OrderedEnum


class GuessResult(OrderedEnum):
    NOT_GUESSED = 0
    NOT_PRESENT = 1
    WRONG_PLACE = 2
    CORRECT = 3

    @property
    def color(self) -> str:
        match self:
            case GuessResult.NOT_GUESSED:
                return '#c8c8c8'
            case GuessResult.NOT_PRESENT:
                return '#cf7272'
            case GuessResult.WRONG_PLACE:
                return '#ebd281'
            case GuessResult.CORRECT:
                return '#a4e38a'


class Game(object):
    words_df = load_words()

    def __init__(self, word_length: int):
        self.word = (
            self.words_df.loc[self.words_df.word_length == word_length, 'word'].sample(1).values[0]
        )
        self.letter_counts = Counter(self.word)
        self.guessed_letters: defaultdict[str, GuessResult] = defaultdict(
            lambda: GuessResult.NOT_GUESSED
        )
        self.guesses = set()

        self.won = False

    def guess(self, word: str) -> list[GuessResult]:
        self.guesses.add(word)

        if word == self.word:
            self.won = True
            return [GuessResult.CORRECT] * len(word)

        letter_counts = defaultdict(int)

        guess_results = []
        recheck_indices = []

        for i, (guess_letter, actual_letter) in enumerate(zip(word, self.word)):
            if guess_letter == actual_letter:
                result = GuessResult.CORRECT
                letter_counts[guess_letter] += 1
            elif letter_counts[guess_letter] <= self.letter_counts[guess_letter]:
                recheck_indices.append(i)  # Save index for later; see comment below
                result = GuessResult.NOT_PRESENT
            else:
                result = GuessResult.NOT_PRESENT
            guess_results.append(result)
            self.guessed_letters[guess_letter] = max(self.guessed_letters[guess_letter], result)

        # For letters that are in the wrong place, first we want to  see if there are instances of
        # the letter in the right place. If the real word has multiple instances of a letter, we
        # want to allow up to that many examples of GuessResult.WRONG_PLACE from left to right; if
        # there are ones in the correct place, the maximum number of GuessResult.WRONG_PLACE should
        # be reduced by the number of correct guesses of that letter.
        for idx in recheck_indices:
            guess_letter = word[idx]
            letter_counts[guess_letter] += 1
            if letter_counts[guess_letter] <= self.letter_counts[guess_letter]:
                guess_results[idx] = GuessResult.WRONG_PLACE
                self.guessed_letters[guess_letter] = max(
                    self.guessed_letters[guess_letter], GuessResult.WRONG_PLACE
                )

        return guess_results
