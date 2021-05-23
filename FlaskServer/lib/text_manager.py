import pytesseract
import re

columns_map = {
    'level': 'level',
    'page_num': 'page',
    'block_num': 'block',
    'par_num': 'par',
    'line_num': 'line',
    'word_num': 'word',
    'left': 'left',
    'top': 'top',
    'width': 'width',
    'height': 'height',
    'conf': 'conf',
    'text': 'text',
}

class TextManager:
    @staticmethod
    def extract_text(image, language='ron+eng'):
        text = pytesseract.image_to_string(image, lang=language)

        return text.strip()

    @staticmethod
    def extract_data(image, language='ron+eng'):
        data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)

        if len(data) == 0:
            return []

        vertical_data = []
        data_keys = list(data.keys())

        for i in range(len(data[data_keys[0]])):
            object_details = {}

            if data['text'][i].strip() == '':
                continue

            for k in data_keys:
                object_details[columns_map[k]] = data[k][i]

            vertical_data.append(object_details)

        return vertical_data

    @staticmethod
    def compute_fitness(text, words):
        # Counts the number of found words from the given set in the text
        count = 0

        for word in words:
            if text.find(word) != -1:
                count += 1

        return count, len(words)

    @staticmethod
    def extract_date(data):
        texts = [obj["text"] for obj in data]

        print(texts)

        for text in texts:
            if len(text) < 5 or len(text) > 15:
                continue

            possible_date = re.search('^.?.-.?.-....', text)

            if possible_date:
                return possible_date.string

        return None
