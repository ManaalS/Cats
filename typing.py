"""Typing test implementation"""

from utils import *
from ucb import main, interact, trace
from datetime import datetime


###########
# Phase 1 #
###########


def choose(paragraphs, select, k):
    """Return the Kth paragraph from PARAGRAPHS for which SELECT called on the
    paragraph returns true. If there are fewer than K such paragraphs, return
    the empty string.
    """
    counter, new_list = 0, []
    for element in paragraphs:
        if select(element):
            counter, new_list = counter + 1, new_list + [element]
    if counter <= k:
        return ''
    return new_list[k]


def about(topic):
    """Return a select function that returns whether a paragraph contains one
    of the words in TOPIC.

    >>> about_dogs = about(['dog', 'dogs', 'pup', 'puppy'])
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup!'], about_dogs, 0)
    'Cute Dog!'
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup.'], about_dogs, 1)
    'Nice pup.'
    """
    assert all([lower(x) == x for x in topic]), 'topics should be lowercase.'
    def checker(sentence):
        split_sentence = split(remove_punctuation(lower(sentence)))
        for element in topic:
            for word in split_sentence:
                if element == word:
                    return True
        return False
    return checker


def accuracy(typed, reference):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    when compared to the prefix of REFERENCE that was typed.

    >>> accuracy('Cute Dog!', 'Cute Dog.')
    50.0
    >>> accuracy('A Cute Dog!', 'Cute Dog.')
    0.0
    >>> accuracy('cute Dog.', 'Cute Dog.')
    50.0
    >>> accuracy('Cute Dog. I say!', 'Cute Dog.')
    50.0
    >>> accuracy('Cute', 'Cute Dog.')
    100.0
    >>> accuracy('', 'Cute Dog.')
    0.0
    """
    typed_words = split(typed)
    reference_words = split(reference)
    total = 0
    if len(typed_words) == 0:
        return 0.0
    for i in range(min(len(typed_words), len(reference_words))):
        if typed_words[i] == reference_words[i]:
            total += 1
    return total/len(typed_words) * 100


def wpm(typed, elapsed):
    """Return the words-per-minute (WPM) of the TYPED string."""
    assert elapsed > 0, 'Elapsed time must be positive'
    return len(typed)/5/(elapsed/60)


def autocorrect(user_word, valid_words, diff_function, limit):
    """Returns the element of VALID_WORDS that has the smallest difference
    from USER_WORD. Instead returns USER_WORD if that difference is greater
    than LIMIT.
    """
    def check_diff(word):
        return diff_function(user_word, word, limit)
    if user_word in valid_words:
        return user_word
    min_value = min(valid_words, key=check_diff)
    min_index = diff_function(user_word, min_value, limit)
    if min_index > limit:
        return user_word
    return min_value


def swap_diff(start, goal, limit):
    """A diff function for autocorrect that determines how many letters
    in START need to be substituted to create GOAL, then adds the difference in
    their lengths.
    """
    if start == goal:
        return 0
    elif len(start) == 0 or len(goal) == 0:
        if len(start) != 0 or len(goal) != 0:
            return max(len(start), len(goal))
        return 0
    elif limit < 0:
        return float('inf')
    if start[0] == goal[0]:
        return 0 + swap_diff(start[1:], goal[1:], limit)
    return 1 + swap_diff(start[1:], goal[1:], limit-1)


def edit_diff(start, goal, limit):
    """A diff function that computes the edit distance from START to GOAL."""
    if start == goal:
        return 0
    elif len(start) == 0 or len(goal) == 0:
        return max(len(start), len(goal))
    elif limit < 0:
        return float('inf')
    else:
        if start[0] == goal[0]:
            return edit_diff(start[1:], goal[1:], limit)
        add_diff = edit_diff(start, goal[1:], limit-1) + 1
        remove_diff = edit_diff(start[1:], goal,limit-1) + 1
        substitute_diff = edit_diff(start[1:], goal[1:], limit-1) + 1
        return min(add_diff, remove_diff, substitute_diff)

def final_diff(start, goal, limit):
    """A diff function. If you implement this function, it will be used."""
    assert False, 'Remove this line to use your final_diff function'




###########
# Phase 3 #
###########


def report_progress(typed, prompt, id, send):
    """Send a report of your id and progress so far to the multiplayer server."""
    num_correct, num_prompt = 0, len(prompt)
    for i in range(min(len(typed), len(prompt))):
        if typed[i] == prompt[i]:
            num_correct += 1
        else:
            break
    progress = num_correct / num_prompt
    send({'id': id, 'progress': progress})
    return progress


def fastest_words_report(word_times):
    """Return a text description of the fastest words typed by each player."""
    fastest = fastest_words(word_times)
    report = ''
    for i in range(len(fastest)):
        words = ','.join(fastest[i])
        report += 'Player {} typed these fastest: {}\n'.format(i + 1, words)
    return report


def fastest_words(word_times, margin=1e-5):
    """A list of which words each player typed fastest."""
    n_players = len(word_times)
    n_words = len(word_times[0]) - 1
    assert all(len(times) == n_words + 1 for times in word_times)
    assert margin > 0
    maxScore, winner, playersResults = float('inf'), -1, []
    playersResults = [[] for player in range(n_players)]
    for words in range(n_words):
        bestScore = float ('inf')
        for players in range(n_players):
            timePassed = elapsed_time(word_times[players][words+1]) - elapsed_time(word_times[players][words])
            if timePassed < bestScore:
                bestScore, winner = timePassed, players
        for player_pt2 in range(n_players):
            elapsed = elapsed_time(word_times[player_pt2][words+1]) - elapsed_time(word_times[player_pt2][words])
            if elapsed - bestScore <= margin:
                playersResults[player_pt2].append(word(word_times[player_pt2][words+1]))
    return playersResults



def word_time(word, elapsed_time):
    """A data abstrction for the elapsed time that a player finished a word."""
    return [word, elapsed_time]


def word(word_time):
    """An accessor function for the word of a word_time."""
    return word_time[0]


def elapsed_time(word_time):
    """An accessor function for the elapsed time of a word_time."""
    return word_time[1]


enable_multiplayer = False  # Change to True when you


##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        reference = choose(paragraphs, select, i)
        if not reference:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(reference)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print("Nice work!")
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, reference))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Typing Test")
    parser.add_argument('topic', help="Topic word", nargs='*')
    parser.add_argument('-t', help="Run typing test", action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)
