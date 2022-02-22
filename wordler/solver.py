import os
import pandas as pd
from wordler.utils import get_word_list
from .constants import DATA_PATH, FIXED, FLOATING, FORBIDDEN

class Wordler:
    
    def __init__(self):
        
        self._tuples = self._init_tuple()
        self.word_list = get_word_list()
        
    @property
    def constraints(self):
        return self._tuples

    def _init_tuple(self,):
        """Keep track of the the fixed (green), floating (yellow), and forbidden (black) letters.
        The tuples contain the index position of the letter and the letter itself e.g. [(0, "A"), (1, "S")].
        """

        tuples = dict(
            fixed_letters = [],
            floating_letters = [],
            forbidden_letters = [],
        )
        return tuples

    def reset(self,):
        self._tuples = self._init_tuple()
        
    def update_constraint(self, guess, result):
        """update the constraints (tuples) based on the guess and the wordle outcoming result.
        The constraints will be used to filter the word list for the next guess."""

        fixed_letters = [(i, l) for i, l in enumerate(guess) 
                         if (result[i]==FIXED) and ((i, l) not in self._tuples["fixed_letters"])]
        floating_letters = [(i, l) for i, l in enumerate(guess) 
                            if (result[i]==FLOATING) and ((i, l) not in self._tuples["floating_letters"])]
        forbidden_letters = [(i, l) for i, l in enumerate(guess) 
                             if (result[i]==FORBIDDEN) and ((i, l) not in self._tuples["forbidden_letters"])]
        
        #FIXME: Add logic around repeated letters.
        #TODO: if repeated letters are detected (e.g. yellow and green on the same round) 
        #      the next block should leave at least one instance of the letter floating.

        # for each fixed (green) letter found, pop one floating (yellow) letter from the constraints
        for i, fix_l in self._tuples["fixed_letters"]:
            pop_list = [j for j,  (_, float_l) in enumerate(self._tuples["floating_letters"]) if float_l==fix_l]
            try:
                self._tuples["floating_letters"].pop(pop_list[0])
            except IndexError:
                pass
                
        self._tuples["fixed_letters"].extend(fixed_letters)
        self._tuples["floating_letters"].extend(floating_letters)
        self._tuples["forbidden_letters"].extend(forbidden_letters)
        
    def _filter_word_list(self, word_df):
        return word_df[word_df["word"].apply(filter_word, **self._tuples)]

    def suggest_next_word(self, key_sort="wiki score", head=10):
        """Return list with words that fit the constraints, and sort by the given key.
        key_sort options: ['wiki score', 'letter score', wiki score x letter score'] """

        if head == 0:
            head = -1 # display all rows
        suggestion_df = self._filter_word_list(self.word_list)
        # update the probabilities
        # suggestion_df["probability"] = (suggestion_df["probability"]/suggestion_df["probability"].sum()).round(4)
        return suggestion_df.sort_values(key_sort, ascending=False).reset_index(drop=True).head(head)
    

def filter_word(word, fixed_letters, floating_letters, forbidden_letters):
    """Determine if the word fits the given constraints."""

    aux_word = list(word)
    
    for i, l in fixed_letters:
        if word[i] != l:
            return False
        aux_word[i] = "🟩"

    for i, l in floating_letters:
        if word[i] == l:
            return False
        elif l not in word:
            return False
        
        try:
            aux_word_index = aux_word.index(l)
            aux_word[aux_word_index] = "🟨"
        except Exception as e:
            pass    
    
    for _, l in forbidden_letters:
        if l in aux_word:
            return False
    
    return True



