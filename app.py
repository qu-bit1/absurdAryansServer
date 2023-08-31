from flask import Flask, request, jsonify
from hangman_agent import HangmanAPI
import random
from collections import deque
import csv
import logging
import os

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(file_handler)

with open('/app/base', 'r') as f:
    words = [line.strip() for line in f if len(line.strip()) == 5]

with open('/app/base', 'r') as f:
    ladder_words = [line.strip() for line in f if len(line.strip()) == 4]

with open('/app/base', 'r') as f:
    hangman_words = [line.strip() for line in f]

secret_word = None
attempts_left = 0
hangman_secret_word = None
hangman_attempts_left = 0
hangman_game_state = None
correct_letters = []
custom_words = []
use_custom_dictionary = os.environ.get('USE_CUSTOM_DICTIONARY', 'False').lower() == 'true'

def read_csv_words(csv_path):
    dict_words = []
    try:
        with open(csv_path, 'r') as csv_file:
            for line in csv_file:
                words = line.strip().split(',')
                dict_words.extend(words)
    except Exception as e:
        app.logger.warning("Error reading CSV:" + str(e))
    app.logger.warning(dict_words)
    return dict_words

@app.route('/wordle/start_game', methods=['POST'])
def start_game():
    global secret_word, attempts_left, custom_words
    custom_csv_path = '/app/custom_dictionary/dictionary.csv'

    if use_custom_dictionary:
        custom_words = read_csv_words(custom_csv_path)
        app.logger.warning(custom_words)
        if not custom_words:
            return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
    else:
        custom_words = []

    if not custom_words:
        custom_words = words
    
    app.logger.warning(custom_words)

    secret_word = random.choice(custom_words)
    app.logger.warning(secret_word)
    attempts_left = 6
    response = {
        'message': 'Welcome to Wordle!',
        'attempts_left': attempts_left
    }
    return jsonify(response)

@app.route('/wordle/guess', methods=['POST'])
def make_guess():
    global secret_word, attempts_left
    if not secret_word:
        return jsonify({'error': 'Game has not been started. Use /start_game endpoint.'}), 400

    guess = request.json.get('guess', '').lower()
    app.logger.warning('Debugging in make_guess')
    app.logger.warning(custom_words)
    if len(guess) != len(secret_word):
        return jsonify({'error': 'Invalid guess. The word must be 5 letters long.'}), 400

    if guess not in custom_words:
        return jsonify({'error': 'Invalid guess. The word must be in the dictionary.'}), 400

    feedback = process_guess(guess)
    attempts_left -= 1

    response = {
        'feedback': feedback,
        'attempts_left': attempts_left
    }

    if guess == secret_word:
        response['message'] = 'Congratulations! You guessed the secret word.'
        secret_word = None

    elif attempts_left <= 0:
        response['message'] = f'Sorry, you have run out of attempts. The secret word was {secret_word}.'
        secret_word = None

    return jsonify(response)


def process_guess(guess):
    global secret_word

    correct_positions = []
    correct_letters_wrong_position = []
    incorrect_letters = []

    for i in range(len(secret_word)):
        if guess[i] == secret_word[i]:
            correct_positions.append(guess[i])
        elif guess[i] in secret_word:
            correct_letters_wrong_position.append(guess[i])
        else:
            incorrect_letters.append(guess[i])

    feedback = {
        'correct_positions': ' '.join(correct_positions),
        'correct_letters_wrong_position': ' '.join(correct_letters_wrong_position),
        'incorrect_letters': ' '.join(incorrect_letters)
    }

    return feedback

@app.route('/hangman/start_game', methods=['POST'])
def start_hangman_game():
    global hangman_secret_word, hangman_attempts_left, hangman_game_state, correct_letters
    custom_csv_path = '/app/custom_dictionary/dictionary.csv'

    if use_custom_dictionary:
        custom_words = read_csv_words(custom_csv_path)
        app.logger.warning(custom_words)
        if not custom_words:
            return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
    else:
        custom_words = []

    if not custom_words:
        custom_words = words
    
    app.logger.warning(custom_words)
    hangman_secret_word = random.choice(custom_words)
    hangman_attempts_left = 6
    hangman_game_state = None
    correct_letters = ['_'] * len(hangman_secret_word)  # Initialize with underscores
    response = {
        'message': 'Welcome to Hangman! The secret word is of '+ str(len(hangman_secret_word)) +' letters',
        'attempts_left': hangman_attempts_left
    }
    return jsonify(response)

@app.route('/hangman/guess', methods=['POST'])
def make_hangman_guess():
    global hangman_secret_word, hangman_attempts_left, hangman_game_state, correct_letters
    if not hangman_secret_word:
        return jsonify({'error': 'Game has not been started. Use /hangman/start_game endpoint.'}), 400

    guess = request.json.get('guess', '').lower()
    if len(guess) != 1 or not guess.isalpha():
        return jsonify({'error': 'Invalid guess. Please enter a single letter.'}), 400

    feedback = process_hangman_guess(guess)

    response = {
        'feedback': feedback,
        'attempts_left': hangman_attempts_left
    }

    if guess in hangman_secret_word:
        for i, letter in enumerate(hangman_secret_word):
            if letter == guess:
                correct_letters[i] = letter
        response['message'] = f'Word guessed till now : {correct_letters}\nLetter {guess} is present in the secret word.'
        
        if correct_letters == list(hangman_secret_word):
            hangman_game_state = 'win'
            response['message'] = 'Congratulations! You have correctly guessed the secret word.'
    else:
        hangman_attempts_left -= 1
        response['attempts_left'] -= 1
        response['message'] = f'Word guessed till now : {correct_letters}\n. Wrong guess !!'

        if hangman_attempts_left <= 0:
            hangman_game_state = 'lose'
            response['message'] = f'Sorry, you have run out of attempts. The secret word was {hangman_secret_word}.'
            hangman_secret_word = None

    return jsonify(response)

def process_hangman_guess(guess):
    global hangman_secret_word

    feedback = []
    for i, letter in enumerate(hangman_secret_word):
        if letter == guess:
            feedback.append((letter, i + 1))

    return feedback

hangmanAPI_instance = HangmanAPI()

@app.route('/hangman/agent', methods=['GET'])
def play_hangman_agent():
    custom_csv_path = '/app/custom_dictionary/dictionary.csv'

    if use_custom_dictionary:
        custom_words = read_csv_words(custom_csv_path)
        app.logger.warning(custom_words)
        if not custom_words:
            return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
    else:
        custom_words = []

    if not custom_words:
        custom_words = hangman_words

    hangmanAPI_instance.reset()
    global hangman_secret_word, attempts_left, hangman_game_state, correct_letters
    hangman_secret_word = random.choice(custom_words)
    correct_letters = ['_', ' ']*len(hangman_secret_word)
    app.logger.warning(secret_word)
    attempts_left = 6
    hangmanAPI_instance.guessed_letters = []
    responses = []

    while attempts_left > 0:
        app.logger.warning(attempts_left)
        app.logger.warning(hangman_secret_word)
        agent_guess = hangmanAPI_instance.guess(''.join(correct_letters))

        if len(agent_guess) != 1 or not agent_guess.isalpha():
            responses.append({'error': 'Invalid guess. Please enter a single letter.'})
            break

        prev_attempt = attempts_left

        feedback = process_hangman_guess(agent_guess)

        response = {
            'agent_guess': agent_guess,
            'feedback': feedback,
            'attempts_left': attempts_left
        }

        if agent_guess in hangman_secret_word:
            app.logger.warning(attempts_left)
            correct_letters = [
                letter if letter == agent_guess else correct_letters[i]
                for i, letter in enumerate(hangman_secret_word)
            ]
            app.logger.warning(correct_letters)
            response['message'] = f'Word guessed till now : {correct_letters}\nLetter {agent_guess} is present in the secret word.'

            if ''.join(correct_letters).replace(" ", "") == hangman_secret_word:
                hangman_game_state = 'win'
                response['message'] = 'Congratulations! You have correctly guessed the secret word.'
                break
        else:
            app.logger.warning(attempts_left)
            app.logger.warning(correct_letters)
            attempts_left -= 1
            response['attempts_left'] -= 1
            response['message'] = f'Word guessed till now : {correct_letters}\n. Wrong guess !!'

        if prev_attempt > attempts_left:
            was_guess_correct = False
        else:
            was_guess_correct = True

        hangmanAPI_instance.upd(agent_guess, was_guess_correct)

        responses.append(response)

    if attempts_left <= 0:
        hangman_game_state = 'lose'
        response['message'] = f'Sorry, you have run out of attempts. The secret word was {hangman_secret_word}.'
        hangman_secret_word = None
        responses.append(response)

    return jsonify(responses)

# def generate_word_ladder( max_ladder_length=5):
#     global current_word
#     custom_csv_path = '/app/custom_dictionary/dictionary.csv'

#     if use_custom_dictionary:
#         custom_words = read_csv_words(custom_csv_path)
#         app.logger.warning(custom_words)
#         if not custom_words:
#             return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
#     else:
#         custom_words = []

#     if not custom_words:
#         custom_words = ladder_words

#     start_word1 = random.choice(custom_words)
#     ladder = [start_word1]

#     current_word = start_word1

#     # for _ in range(max_ladder_length - 1):
#     #     next_word = find_next_word(current_word, ladder)
#     #     if next_word:
#     #         ladder.append(next_word)
#     #         current_word = next_word
#     #     else:
#     #         break

#     while len(ladder) < 5:
#         current_word = ladder[-1]
#         next_word = find_next_word(current_word, ladder)
#         if next_word:
#             ladder.append(next_word)
#         else:
#             return generate_word_ladder()

#     return start_word1, ladder[-1], ladder

def findWordLadder():  
    global ladder, startWord, endWord
    custom_csv_path = '/app/custom_dictionary/dictionary.csv'

    if use_custom_dictionary:
        custom_words = read_csv_words(custom_csv_path)
        app.logger.warning(custom_words)
        if not custom_words:
            return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
    else:
        custom_words = []

    if not custom_words:
        custom_words = words
    
    startWord, endWord = random.sample(custom_words, 2)  
    wordSet = set(custom_words)
    queue = deque([(startWord, [startWord])])
    visited = set()
    parents = {}
    ladder = []

    # while len(ladder)<4:
    while queue:
        currentWord, ladder = queue.popleft()
        visited.add(currentWord)

        if len(ladder)<4:
            for i in range(len(currentWord)):
                for char in 'abcdefghijklmnopqrstuvwxyz':
                    nextWord = currentWord[:i] + char + currentWord[i+1:]

                    if nextWord in wordSet and nextWord not in visited:
                        queue.append((nextWord, ladder + [nextWord]))
                        visited.add(nextWord)
                        parents[nextWord] = currentWord

                        if nextWord == endWord:
                            ladder = ladder + [endWord]
        else:
            break
    app.logger.warning(ladder)

    return []

@app.route('/word_ladder/start_game', methods=['GET'])
def word_ladder_start_game():
    global startWord, endWord, ladder, current_word, guessed_words
    custom_csv_path = '/app/custom_dictionary/dictionary.csv'

    if use_custom_dictionary:
        custom_words = read_csv_words(custom_csv_path)
        app.logger.warning(custom_words)
        if not custom_words:
            return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
    else:
        custom_words = []

    if not custom_words:
        custom_words = words

    startWord = random.sample(custom_words, 1)

    findWordLadder()
    endWord = ladder[-1]
    current_word = startWord
    guessed_words = []
    
    response = {
        'message': 'Welcome to Word Ladder!',
        'start_word': startWord,
        'end_word': endWord
    }
    
    return jsonify(response)

@app.route('/word_ladder/guess', methods=['POST'])
def word_ladder_make_guess():
    global current_word, guessed_words

    custom_csv_path = '/app/custom_dictionary/dictionary.csv'

    if use_custom_dictionary:
        custom_words = read_csv_words(custom_csv_path)
        app.logger.warning(custom_words)
        if not custom_words:
            return jsonify({'error': 'Custom CSV dictionary is empty or could not be read.'}), 400
    else:
        custom_words = []

    if not custom_words:
        custom_words = words
    
    if not current_word:
        return jsonify({'error': 'Game has not been started. Use /start_game endpoint.'}), 400
    
    guess = request.json.get('guess', '').lower()
    
    if len(guess) != len(current_word):
        return jsonify({'error': 'Invalid guess. The word must be of the same length.'}), 400
    
    if guess not in custom_words:
        return jsonify({'error': 'Invalid guess. The word must be in the dictionary.'}), 400
    
    if sum(c1 != c2 for c1, c2 in zip(guess, current_word)) != 1:
        return jsonify({'error': 'Invalid guess. The word must have only one letter changed from the previous word.'}), 400
    
    if guess == endWord:
        response = {
            'message': 'Congratulations! You have successfully completed the word ladder!',
            'word_ladder': guessed_words + [current_word, guess]
        }
        current_word = None
        guessed_words = []
    else:
        current_word = guess
        guessed_words.append(guess)
        response = {
            'message': 'Guess accepted. Keep going!',
            'current_word': current_word
        }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
