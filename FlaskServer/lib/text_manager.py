import pytesseract
import re
from typing import List
from datetime import datetime
from lib.logger import print_list
from model.extracted_object import ExtractedObject

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
    def recognize(image, params):
        ocr = params.get('ocr', 'tesseract')

        pprint('Extracting data')

        if ocr == 'tesseract':
            all_data = TextManager.extract_tesseract(image)
        else:
            all_data = TextManager.extract_tesseract(image)

        date = TextManager.extract_date(all_data)

        return {
            'date': date,
        }, all_data

    @staticmethod
    def extract_text(image, language='ron+eng'):
        text = pytesseract.image_to_string(image, lang=language)

        return text.strip()

    @staticmethod
    def extract_tesseract(image, language='ron+eng') -> List[ExtractedObject]:
        data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)

        if len(data) == 0:
            return []

        vertical_data = []
        data_keys = list(data.keys())

        for i in range(len(data[data_keys[0]])):
            if data['text'][i].strip() == '':
                continue

            object_details = {}

            for k in data_keys:
                object_details[k] = data[k][i]

            extracted_object = ExtractedObject.from_tesseract(object_details)

            vertical_data.append(extracted_object)

        print_list([obj.text for obj in vertical_data])

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
        texts = [obj.text for obj in data]

        for text in texts:
            if len(text) < 5 or len(text) > 15:
                continue

            # 12-10-2021 and other delimiters
            possible_date = re.search('.?.[-.,|/].?.[-.,|/][12][0-9]{3}', text)

            if possible_date:
                return possible_date[0]
        return None


def pprint(message):
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(str(now) + ' [TextManager] ' + str(message))
