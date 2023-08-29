from flask import Flask, request, jsonify
# from hangman_agent import HangmanAPI
import random
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

secret_word = None
attempts_left = 0
hangman_secret_word = None
hangman_attempts_left = 0
hangman_game_state = None
correct_letters = []
custom_words = []
use_custom_dictionary = os.environ.get('USE_CUSTOM_DICTIONARY', 'False').lower() == 'true'
# hangman_ai = HangmanAPI()

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

# @app.route('/hangman/agent', methods=['POST'])
# def play_hangman_with_ai():
#     global hangman_secret_word, hangman_attempts_left
    
#     if hangman_ai.start_game():
#         response = {
#             'message': 'Hangman game played by AI agent.',
#             'attempts_left': hangman_ai.tries_remains
#         }
#         return jsonify(response)
#     else:
#         response = {
#             'message': 'AI agent failed to win Hangman game.',
#             'attempts_left': 0
#         }
#         return jsonify(response)

# def generate_word_ladder():
#     start_word = random.choice(dictionary)
#     end_word = random.choice(dictionary)

#     while end_word == start_word or len(end_word) != len(start_word):
#         end_word = random.choice(dictionary)

#     word_ladder = [start_word]

#     for _ in range(len(start_word) - 1):
#         new_word = word_ladder[-1]
#         while new_word in word_ladder or new_word == word_ladder[-1]:
#             new_word = list(new_word)
#             random_index = random.randint(0, len(new_word) - 1)
#             new_word[random_index] = random.choice(list(set(dictionary) - set(new_word)) - {new_word[random_index]})
#             new_word = ''.join(new_word)
#         word_ladder.append(new_word)

#     word_ladder.append(end_word)
#     return start_word, end_word, word_ladder

# def generate_word_ladder( max_ladder_length=5):
#     global current_word
#     start_word = random.choice(custom_words)
#     ladder = [start_word]

#     current_word = start_word

#     for _ in range(max_ladder_length - 1):
#         next_word = find_next_word(current_word, ladder)
#         if next_word:
#             ladder.append(next_word)
#             current_word = next_word
#         else:
#             break

#     return start_word, current_word, ladder


# def find_next_word(current_word, ladder):
#     possible_words = []
#     for word in custom_words:
#         if (len(word) == len(current_word)
#             and sum(1 for c1, c2 in zip(current_word, word) if c1 != c2) == 1
#             and word not in ladder):
#             possible_words.append(word)

#     return random.choice(possible_words) if possible_words else None

# @app.route('/word_ladder/start_game', methods=['GET'])
# def word_ladder_start_game():
#     global start_word, end_word, word_ladder, current_word, guessed_words
    
#     start_word, end_word, word_ladder = generate_word_ladder()
#     current_word = start_word
#     guessed_words = []
    
#     response = {
#         'message': 'Welcome to Word Ladder!',
#         'start_word': start_word,
#         'end_word': end_word
#     }
    
#     return jsonify(response)

# @app.route('/word_ladder/guess', methods=['POST'])
# def word_ladder_make_guess():
#     global current_word, guessed_words
    
#     if not current_word:
#         return jsonify({'error': 'Game has not been started. Use /start_game endpoint.'}), 400
    
#     guess = request.json.get('guess', '').lower()
    
#     if len(guess) != len(current_word) or guess not in dictionary:
#         return jsonify({'error': 'Invalid guess. The word must be of the same length and in the dictionary.'}), 400
    
#     if sum(c1 != c2 for c1, c2 in zip(guess, current_word)) != 1:
#         return jsonify({'error': 'Invalid guess. The word must have only one letter changed from the previous word.'}), 400
    
#     if guess == end_word:
#         response = {
#             'message': 'Congratulations! You have successfully completed the word ladder!',
#             'word_ladder': guessed_words + [current_word, guess]
#         }
#         current_word = None
#         guessed_words = []
#     else:
#         current_word = guess
#         guessed_words.append(guess)
#         response = {
#             'message': 'Guess accepted. Keep going!',
#             'current_word': current_word
#         }
    
#     return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
