
import os
import numpy as np
import pandas as pd
import string
import streamlit as st 
from typing import List
from wordler import DATA_PATH, LOGO_PATH

colors = ["⬛️", "🟩", "🟨"]
color_dict = {
    "⬛️": 0, 
    "🟨": 1,
    "🟩": 2,
}

def submit_guesses(n_guesses=6):
    """Create a word submission word with n steps.
    Return all the guesss and hints submitted."""

    with st.form(f"form"):
        all_guesses = []
        all_hints = []
        for n in range(1, n_guesses+1):
            guess_letters = []
            guess_hints = []

            letters_cols = st.columns(5)
            for i, col in enumerate(letters_cols):
                with col:
                    letter = st.text_input(" ", max_chars=1, key=f"guess_{n}_letter_{i}")
                    guess_letters.append(letter.upper())

            hints_cols = st.columns(5)
            for i, col in enumerate(hints_cols):
                with col:
                    hint = st.selectbox(" ", colors,  key=f"guess_{n}_hint_{i}")
                    guess_hints.append(hint)
            st.markdown("---")
            all_guesses.append(guess_letters)
            all_hints.append(guess_hints)

        st.form_submit_button("submit")

    return all_guesses, all_hints

def keep_valid_guesses(all_guesses, all_hints):
    """Loop through all the submited existing guesses and only keep the 5 letter submissions (exclude empty strings)"""

    valid_guesses = []
    valid_hints = []
    for guess, hint in zip(all_guesses, all_hints):
        if all(guess):
            valid_guesses.append(guess)
            valid_hints.append(hint)
    return valid_guesses, valid_hints


def print_letters_hints(all_letters, all_hints):
    """Print the submitted letters and hints on the sidebar for reference."""

    n_steps = len(all_letters)
    for step in range(n_steps):
        if all(all_letters[step]):
            st.sidebar.write("".join(all_hints[step]) + f" ({''.join(all_letters[step])})"  )

def step_results(letters: List[str], colors: List[str], step):
    """Print out the letters and the selected colors in a containter"""    

    with st.container():
            letters_column = st.columns(5)
            for i, col in enumerate(letters_column):
                with col:
                    text = st.text_input(" ", value=letters[i], max_chars=1, key=f"{step}_letters_{i}", disabled=True)

            hints_column = st.columns(5)
            for i, col in enumerate(hints_column):
                with col: 
                    st.selectbox(" ", colors, index=i, key=f"{step}_color_{i}", disabled=True)

@st.cache
def get_word_list():
    """Load the word list dataset."""

    data = pd.read_csv(os.path.join(DATA_PATH, "word_scores.csv"), index_col=0)
    data.rename(columns=lambda x : x.replace("_", " "), inplace=True)
    return data

@st.cache
def get_word_set():
    """Create a word list look up table."""

    return set(get_word_list()["word"].values)

def is_valid_word(word):
    """Raise a warning if the submitted word is not valid."""

    if isinstance(word, list):
        word = "".join(word)

    if len(word) < 1:
        return
    
    all_words = get_word_set()
    if word.upper() not in all_words:
        word_warning(word)

def word_warning(not_a_word):
    """Return a warning message for invalid words."""

    templates = [
        f"Are you sure '{not_a_word}' is a word?",
        f"'{not_a_word}' doesn't seem to be a word.",
        f"What is '{not_a_word}'? Is that a word?",
        f"'{not_a_word}'? Is that a typo?",
        f"I've never heard '{not_a_word}' before...",
        f"I'm pretty sure '{not_a_word}' isn't a word...",
    ]
    message_index = np.random.randint(4)
    st.sidebar.warning(templates[message_index])

def convert_guess_and_hints(guess, hints):
    """Normalize the submitted guesses and hints to be ingestible by solver.Wordler()."""

    guess_word = "".join(guess)
    hint_numbers = [color_dict[color] for color in hints]
    return guess_word, hint_numbers

def get_logo():
    """Load the WORDLEr logo."""
    st.image(LOGO_PATH)

def parse_metric(metric, valid_guesses):
    if metric in ["wiki score", "letter score", "wiki score x letter score"]:
        return metric
    elif metric == "auto":
        if n_step := len(valid_guesses) <=1:
            st.write("ls")
            return "letter score"
        else:
            st.write("wiki")
            return "wiki score"
    else:
        raise ValueError(f"Metric {metric} is not valid")