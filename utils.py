from enum import Enum

import pandas as pd

from english_words import english_words_lower_set


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


def load_words():
    # Instead of using english_words_lower_alpha_set, we remove all words from
    # english_words_lower_set so we don't end up with words like "givin'" turning into "givin"
    words = [word for word in english_words_lower_set if word.isalpha()]
    words_df = pd.DataFrame(data={'word': sorted(words)})
    words_df['word_length'] = words_df.word.str.len()

    return words_df
