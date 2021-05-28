import pytesseract
import re
from typing import List
from datetime import datetime
from lib.utils import print_list
from lib.image_helper import image2bytes
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
    def recognize(image, image_ext, params={}):
        ocr = params.get('ocr-engine', 'tesseract')

        pprint('Extracting data')

        if ocr == 'tesseract':
            all_data = TextManager.extract_tesseract(image)
        else:
            all_data = TextManager.extract_tesseract(image)

        date = TextManager.extract_date(all_data)
        d1, d2 = TextManager.split_by_regions(all_data, image.shape)

        store = TextManager.extract_store(all_data)

        return {
            'date': date,
            'store': store,
            'delimiters': [d1, d2]
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

        vertical_data = TextManager.reindex_blocks(vertical_data)


        # DEBUG
        # TextManager.print_data_table(vertical_data)
        print_list(vertical_data)

        return vertical_data

    @staticmethod
    def reindex_blocks(data: List[ExtractedObject]):
        index_mapping = {}
        index = 1

        for d in data:
            if d.block not in index_mapping:
                index_mapping[d.block] = index
                index += 1

        for d in data:
            d.block = index_mapping[d.block]

        return data

    @staticmethod
    def print_data_table(data: List[ExtractedObject]):
        used_keys = ['text', 'block', 'par', 'line', 'word', 'confidence']
        used_data = [{key: obj.__getattribute__(key) for key in used_keys} for obj in data]

        rows = [list(value.values()) for value in used_data]

        table = Texttable()
        table.set_max_width(0)
        table.header(used_keys)
        table.add_rows(rows, header=False)

        print(table.draw())

    @staticmethod
    def compute_fitness(text, words):
        # Counts the number of found words from the given set in the text
        count = 0

        for word in words:
            if text.find(word) != -1:
                count += 1

        return count, len(words)

    @staticmethod
    def extract_date(data: List[ExtractedObject]):
        texts = [obj.text for obj in data]

        for text in texts:
            if len(text) < 5 or len(text) > 15:
                continue

            # 12-10-2021 and other delimiters
            possible_date = re.search('.?.[-.,|/].?.[-.,|/][12][0-9]{3}', text)

            if possible_date:
                return possible_date[0]
        return None

    @staticmethod
    def split_by_regions(data: List[ExtractedObject], image_shape):
        height, width = image_shape

        cif = TextManager.search_cif(data)
        total = TextManager.search_total(data, width)

        if cif:
            cif_delimiter = cif.top + cif.height / 2
        else:
            cif_delimiter = None
            pprint('Could not find CIF')

        if total:
            total_delimiter = total.top + total.height / 2
        else:
            total_delimiter = None
            pprint('Could not find TOTAL')

        return cif_delimiter, total_delimiter

    @staticmethod
    def search_cif(data: List[ExtractedObject]):
        # C.I.F. and small errors
        # Cod Identificare Fiscala
        for d in data:
            if re.search('[C08][.]?[I1][.]?[FP]', d.text):
                return d

        lines_data = TextManager.get_lines(data)

        for la in lines_data:
            if re.search('COD', la.text) and \
                    re.search('IDENTIFICARE', la.text) and \
                    re.search('FISCALA', la.text):
                return la

        for la in lines_data:
            if re.search('[C08][.]?[ ]*[I1][.]?[ ]*[FP]', la.text):
                return la

        return None

    @staticmethod
    def search_total(data: List[ExtractedObject], image_width):
        totals_found = []

        for d in data:
            if re.search('TOTAL', d.text) and not re.search('SUBTOTAL', d.text):
                totals_found.append(d)

        if image_width:
            # Total is located on the left side of the image
            half_width = image_width / 2
            totals_found = [t for t in totals_found if t.left < half_width]

        if len(totals_found) > 0:
            # Sort totals in appearance order from top to bottom
            totals_found.sort(key=lambda t: t.top)
            return totals_found[0]

        return None

    @staticmethod
    def get_lines(data: List[ExtractedObject]):
        def key(eo: ExtractedObject):
            return '{}-{}-{}'.format(eo.block, eo.par, eo.line)

        lines = {}

        for d in data:
            k = key(d)

            if k not in lines:
                new_obj = d.clone()
                new_obj.word = None
                lines[k] = new_obj
            else:
                lines[k].expand_with(d)

        return list(lines.values())

    @staticmethod
    def extract_store(data):
        return None


def pprint(message):
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(str(now) + ' [TextManager] ' + str(message))
