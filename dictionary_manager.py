import os
import json
from enum import Enum

class WordMasteryLevel(Enum):
    NEW = "new"
    LEARNT = "learnt"
    MASTERED = "mastered"

class DictionaryManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dictionary_file = os.path.join(self.base_dir, 'words', 'own_dictionary.txt')
        self.usage_file = os.path.join(self.base_dir, 'words', 'word_usage.txt')
        # Load both seen words and successful guesses
        self.word_data = self._load_usage_data()

    def _load_usage_data(self):
        """Load the word usage data from file."""
        usage_data = {}
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split(':')
                        if len(parts) >= 3:
                            word, seen, correct = parts
                            usage_data[word.lower()] = {
                                'seen': int(seen),
                                'correct_guesses': int(correct)
                            }
            except Exception:
                pass
        return usage_data

    def _save_usage_data(self):
        """Save the word usage data to file."""
        os.makedirs(os.path.dirname(self.usage_file), exist_ok=True)
        with open(self.usage_file, 'w') as f:
            for word, data in self.word_data.items():
                f.write(f"{word}:{data['seen']}:{data['correct_guesses']}\n")

    def mark_word_seen(self, word):
        """Mark a word as seen (when it becomes the target word)."""
        word = word.lower()
        
        # Add word to dictionary file if not already present
        self._add_to_dictionary_file(word)
        
        # Update seen count
        if word not in self.word_data:
            self.word_data[word] = {'seen': 1, 'correct_guesses': 0}
        else:
            self.word_data[word]['seen'] += 1
        
        self._save_usage_data()

    def mark_word_guessed(self, word):
        """Mark a word as correctly guessed."""
        word = word.lower()
        
        if word not in self.word_data:
            self.word_data[word] = {'seen': 1, 'correct_guesses': 1}
        else:
            self.word_data[word]['correct_guesses'] += 1
        
        self._save_usage_data()

    def _add_to_dictionary_file(self, word):
        """Add word to the dictionary file if not already present."""
        os.makedirs(os.path.dirname(self.dictionary_file), exist_ok=True)
        
        existing_words = set()
        if os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'r') as f:
                existing_words = set(line.strip().lower() for line in f)
        
        if word not in existing_words:
            with open(self.dictionary_file, 'a') as f:
                f.write(word + '\n')

    def get_mastery_level(self, word):
        """Get the mastery level of a word based on successful guesses."""
        word = word.lower()
        if word not in self.word_data:
            return WordMasteryLevel.NEW.value
            
        correct_guesses = self.word_data[word]['correct_guesses']
        
        if correct_guesses >= 4:
            return WordMasteryLevel.MASTERED.value
        elif correct_guesses >= 2:
            return WordMasteryLevel.LEARNT.value
        else:
            return WordMasteryLevel.NEW.value

    def get_all_words(self):
        """Get all words from the dictionary file."""
        words = []
        if os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'r') as f:
                words = [line.strip().lower() for line in f if line.strip()]
        return sorted(words) 