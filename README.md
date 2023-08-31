# Absurd Agents by Aryans

This is a web-based application that features three word games:  Wordle, Hangman and Word Ladder. The application provides an interface for playing these games interactively.

## Introduction

This application provides three word-based games: Hangman, Word Ladder, and Wordle. Users can interact with the AI agent to play Hangman, word ladders, and solve Wordle puzzles. The project is built using Python, Flask, and various libraries for language processing.

## Rules

### Hangman

1. The AI selects a random word.
2. You have a limited number of attempts to guess the word.
3. You can guess one letter at a time.
4. Correctly guessed letters are revealed in their positions.
5. Incorrect guesses reduce the remaining attempts.
6. Guess the entire word within the attempts to win.
7. If you run out of attempts without guessing the word, you lose.

### Wordle

1. The server selects a random five-letter word.
2. You have a limited number of attempts to guess the word.
3. After each guess, you'll receive feedback on the correctness of each letter.
4. A correct letter in the correct position is marked as "correct_positions"
5. A correct letter in the wrong position is marked as "correct_letters_wrong_positions"
6. Incorrect letters are marked as "incorrect_letters"
7. Use the feedback to make educated guesses and solve the word within attempts.
8. Guess the entire word correctly within the attempts to win.

### Word Ladder

1. The server generates a word ladder between two random words.
2. A word ladder is a sequence of words, where each word differs by only one letter from the previous word.
3. You're provided with the start and end words.
4. The challenge is to find a sequence of intermediate 5. words that link the start and end words.
6. Each intermediate word must be present in a standard dictionary.

## Getting Started

### Installation

1. Clone the repository to your local machine.
2. Run the Count_Table Creator.ipynb and you get the Count_Table.npy

## Using Docker

1. Install Docker on your machine.
2. Build the Docker image: `docker build -t absurd-agents .`
3. Run the Docker container: `docker run -p 5000:5000 absurd-agents`
4. To use your custom dictionary use -v flag to mount your dictionary and set the USE_CUSTOM_DICTIONARY environment variable as True: `docker run --name wordle-game-1 -p 5000:5000 -e USE_CUSTOM_DICTIONARY=True -v "$(pwd)/dictionary.csv:/app/custom_dictionary/dictionary.csv" wordle-game`

## API endpoints

### Hangman

- To start game for user: `/hangman/start_game` (POST)
- To guess letter for user: `/hangman/guess` (POST)
- You can enter your guess using the parameter guess, for example, if your guess letter is 's', then you can enter this command on your terminal `http POST http://localhost:5000/hangman/guess guess=s`
- For agent to play: `hangman/agent` (POST)

### Wordle

- To start game for user: `/wordle/start_game` (POST)
- To guess letter for user: `/wordle/guess` (POST)
- You can enter your guess using the parameter guess, for example, if your guess letter is 'sport', then you can enter this command on your terminal `http POST http://localhost:5000/wordle/guess guess=sport`

### Word Ladder

- To start game for user: `/word_ladder/start_game` (GET)
- To guess letter for user: `/word_ladder/guess` (POST)
- You can enter your guess using the parameter guess, for example, if your guess letter is 'mute', then you can enter this command on your terminal `http POST http://localhost:5000/word_ladder/guess guess=mute`

## Dependencies

- Flask
- NumPy
