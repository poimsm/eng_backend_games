import os
import re
import math

import tensorflow as tf
from transformers import TFBertModel, BertTokenizer
from tensorflow.keras.models import load_model

import textstat
from word_forms.word_forms import get_word_forms

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import words

from api.utils.helpers import read_file_to_array
from api.utils.thresholds import moderate

import logging

logger = logging.getLogger('text_analyzer')


class TextAnalyzer:

    def __init__(self):
        logger.info('Initializing new instance')
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logger.info(f'Base directory set to: {self.base_dir}')

        model_path = os.path.join(self.base_dir, 'models', 'modelo_small_01.h5')
        self.model = load_model(model_path, custom_objects={'TFBertModel': TFBertModel})
        logger.info(f'Model loaded from: {model_path}')

        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        logger.info('BERT tokenizer initialized')

        common_words_path = os.path.join(self.base_dir, 'data', '10k_commom_words.txt')
        self.common_words = read_file_to_array(common_words_path)
        logger.info(f'Common words loaded from: {common_words_path}')

        phrasal_verbs_path = os.path.join(self.base_dir, 'data', 'phrasal_verbs.txt')
        self.phrasal_verbs = read_file_to_array(phrasal_verbs_path)
        logger.info(f'Phrasal verbs loaded from: {phrasal_verbs_path}')

        fantasy_path = os.path.join(self.base_dir, 'data', 'fantasy.txt')
        self.fantasy = read_file_to_array(fantasy_path)
        logger.info(f'Fantasy words loaded from: {fantasy_path}')

        self.thresholds = moderate
        logger.info('Thresholds set to moderate')

        self.text = ''
        self.reqID = ''

        logger.info(f'TextAnalyzer initialized')

    def check_creativity(self):
        logger.info(f'ReqID={self.reqID} | Initiating check creativity')

        if self.__check_short_talk():
            logger.info(f'ReqID={self.reqID} | Result: Triggered short_talk check')
            return False

        if self.__check_complexity():
            logger.info(f'ReqID={self.reqID} | Result: Passed complexity check')
            return True

        if self.__check_fantasy():
            logger.info(f'ReqID={self.reqID} | Result: Passed fantasy check')
            return True

        if self.__check_distant_ideas():
            logger.info(f'ReqID={self.reqID} | Result: Passed distant_ideas check')
            return True

        logger.info(f'ReqID={self.reqID} | Result: Did not meet any criteria')
        return False

    def detect_phrasal_verbs(self):
        logger.info(f'ReqID={self.reqID} | Initiating detect phrasal verbs')

        text = self.text.lower()
        found_verbs = []

        for pv in self.phrasal_verbs:
            parts = pv.lower().split()
            if len(parts) != 2:
                logger.debug(f'ReqID={self.reqID} | Invalid phrasal verb format: {pv}')
                continue

            verb, particle = parts
            verb_forms = get_word_forms(verb)
            forms = [verb_form + r'( \w+)? ' + particle for verb_form in verb_forms['v']]

            for form in forms:
                if re.search(r'\b' + form + r'\b', text):
                    found_verbs.append(pv)
                    logger.info(f'ReqID={self.reqID} | Detected phrasal verb: "{pv}" in text')
                    break

        if found_verbs:
            logger.info(f'ReqID={self.reqID} | Phrasal verbs found: {len(found_verbs)}')
        else:
            logger.info(f'ReqID={self.reqID} | No phrasal verbs detected')

        return len(found_verbs) > 0

    def check_fluency(self, duration_seconds):
        logger.info(f'ReqID={self.reqID} | Initiating fluency check')

        if self.__check_short_talk():
            logger.info(f'ReqID={self.reqID} | Fluency check: Short talk detected, considered not fluent')
            return False

        text_length = len(self.text)
        fluency_rate = text_length / duration_seconds
        threshold = self.thresholds['fluency_short']
        
        if(text_length > 170):
            threshold = self.thresholds['fluency_long']        

        logger.info(f'ReqID={self.reqID} | Calculated fluency rate: {fluency_rate} (Length: {text_length}, Duration: {duration_seconds}s, Threshold: {threshold})')

        if fluency_rate > threshold:
            logger.info(f'ReqID={self.reqID} | Fluency check: Passed (Above threshold)')
            return True
        else:
            logger.info(f'ReqID={self.reqID} | Fluency check: Failed (Below threshold)')
            return False

    def check_vocabulary(self):
        logger.info(f'ReqID={self.reqID} | Initiating vocabulary check')

        if self.__check_short_talk():
            logger.info(f'ReqID={self.reqID} | Vocabulary check: Short talk detected, considered limited vocabulary')
            return False

        vocabulary_score = self.__vocabulary_log_exp()
        threshold = self.thresholds['vocabulary']

        logger.info(f'ReqID={self.reqID} | Calculated vocabulary score: {vocabulary_score} (Threshold: {threshold})')

        if vocabulary_score > threshold:
            logger.info(
                f'ReqID={self.reqID} | Vocabulary check: Passed (Above threshold)')
            return True
        else:
            logger.info(f'ReqID={self.reqID} | Vocabulary check: Failed (Below threshold)')
            return False

    def check_long_talk(self):
        logger.info(f'ReqID={self.reqID} | Initiating long talk check')

        words = re.findall(r'\b\w+\b', self.text)
        word_count = len(words)
        threshold = self.thresholds['long_talk']

        logger.info(f'ReqID={self.reqID} | Word count in text: {word_count} (Long talk threshold: {threshold})')

        if word_count > threshold:
            logger.info(f'ReqID={self.reqID} | Long talk check: Passed (Above threshold)')
            return True
        else:
            logger.info(f'ReqID={self.reqID} | Long talk check: Failed (Below threshold)')
            return False

    def __check_short_talk(self):
        words = re.findall(r'\b\w+\b', self.text)
        word_count = len(words)
        threshold = self.thresholds['short_talk']
        return word_count < threshold

    def __vocabulary_log_exp(self, log_base=1.2, exp_factor=1.3, range_factor=2.5):
        word_pattern = r'\b\w+\b'
        words = re.findall(word_pattern, self.text.lower())

        if not words:
            return 0

        counter = 0
        for word in words:
            if len(word) == 1:
                continue

            found = False
            index = -1
            for i, elem in enumerate(self.common_words):
                if elem == word:
                    found = True
                    index = i
                    break

            if found:
                adjustment = 1 + (index // 100) * range_factor
                counter += (math.log(index + 1, log_base)
                            ** exp_factor) * adjustment
            elif self.__word_exists_in_english(word):
                # counter += (math.log(50000, log_base) ** exp_factor)
                # counter += (math.log(50000, log_base) ** exp_factor * 1.0) + 100
                counter += (math.log(50000, log_base)
                            ** exp_factor * 1.0) + 50000
                # counter += 5000

        if 0 < len(words) and len(words) < 5:
            return 0
        elif 5 <= len(words) and len(words) < 7:
            return round(counter / len(words) / 200) - 40
        elif 7 <= len(words) and len(words) < 9:
            return round(counter / len(words) / 200) - 30
        elif 9 <= len(words) and len(words) < 12:
            return round(counter / len(words) / 200) - 0
        elif 12 <= len(words) and len(words) < 15:
            return round(counter / len(words) / 200) + 10
        elif 15 <= len(words) and len(words) < 18:
            return round(counter / len(words) / 200) + 0
        elif 18 <= len(words) and len(words) < 22:
            return round(counter / len(words) / 200) + 20
        elif 22 <= len(words) and len(words) < 26:
            return round(counter / len(words) / 200) + 40
        else:
            return round(counter / len(words) / 200) + 40

    def __word_exists_in_english(self, word):
        word = word.lower()
        if self.__is_verb(word):
            word = self.__to_base_form(word)
        english_words = set(words.words())

        return word in english_words

    def __is_verb(self, word):
        synsets = wordnet.synsets(word)
        for synset in synsets:
            if synset.pos() == 'v':
                return True
        return False

    def __to_base_form(self, word):
        lemmatizer = WordNetLemmatizer()
        base_form = lemmatizer.lemmatize(word, 'v')
        return base_form

    def __check_complexity(self):
        return textstat.flesch_reading_ease(self.text) < self.thresholds['reading_complexity']

    def __check_fantasy(self):
        text_words = re.findall(r'\b\w+\b', self.text.lower())
        return any(word.lower() in text_words for word in self.fantasy)

    def __check_distant_ideas(self):
        logger.info(f'ReqID={self.reqID} | Initiating distant ideas check')

        # Tokenizing the input text
        inputs = self.tokenizer(self.text, padding='max_length',
                                truncation=True, max_length=30, return_tensors="tf")
        logger.debug(f'ReqID={self.reqID} | Text tokenized for distant ideas check')

        # Making a prediction
        prediction = self.model.predict(
            {'input_ids': inputs['input_ids'], 'attention_mask': inputs['attention_mask']})
        prediction_score = prediction[0, 0]
        threshold = self.thresholds['distant_ideas']

        logger.info(f'ReqID={self.reqID} | Distant ideas prediction score: {prediction_score} (Threshold: {threshold})')

        if prediction_score >= threshold:
            logger.info(f'ReqID={self.reqID} | Distant ideas check: Passed (Above or equal to threshold)')
            return True
        else:
            logger.info(f'ReqID={self.reqID} | Distant ideas check: Failed (Below threshold)')
            return False
