import pytesseract
import re
from typing import List, Optional
from datetime import datetime
from lib.utils import pretty_list
from lib.image_helper import image2bytes
from model import ExtractedTree, Node, NodeType
from model import ExtractedObject
from texttable import Texttable
from google.cloud import vision

class TextManager:
    @staticmethod
    def recognize(image, image_ext, params={}):
        ocr = params.get('ocr-engine', 'tesseract')

        pprint('Extracting data')

        if ocr == 'tesseract':
            data = TextManager.extract_tesseract(image)
        else:
            data = TextManager.extract_google_vision(image, image_ext)

        date = TextManager.extract_date(data)
        total = TextManager.extract_total(data, image.shape)
        store = TextManager.extract_store(data)

        d1, d2 = TextManager.split_by_regions(data, image.shape)

        return {
            'date': date,
            'total': total,
            'store': store,
            'delimiters': [d1, d2]
        }, data

    @staticmethod
    def extract_google_vision(image, image_extension) -> ExtractedTree:
        client = vision.ImageAnnotatorClient()

        bytes_image = image2bytes(image, image_extension)
        vision_image = vision.Image(content=bytes_image)

        data = []
        response = client.document_text_detection(image=vision_image)
        blocks = response.full_text_annotation.pages[0].blocks

        for block_i, block in enumerate(blocks):
            for par_i, par in enumerate(block.paragraphs):
                for word_i, word in enumerate(par.words):
                    extracted_object = ExtractedObject.from_google_vision(word, block_i, par_i, -1, word_i)
                    data.append(extracted_object)

        # Sort by middle line of the word
        # This could help with ordering the lines, but breaks the order of the words
        # Disable it for now and we might enable it when we also order by words
        # data.sort(key=lambda d: int(d.top+d.height/2))

        tree_data = ExtractedTree()
        for d in data:
            node = Node(NodeType.WORD, d.text, d.start, d.end)
            tree_data.add_node(node)

        # Debug
        # TextManager.print_data_tree_table(tree_data, NodeType.LINE)

        return tree_data

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
        # pprint(pretty_list(vertical_data))

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
    def print_data_tree_table(data_tree: ExtractedTree, node_type):
        used_keys = ['text', 'top', 'bottom', 'height', 'left', 'right', 'width', 'parent']

        if node_type == NodeType.WORD:
            data = data_tree.get_words()
        else:
            data = data_tree.get_lines()

        used_data = [{key: obj.__getattribute__(key) for key in used_keys} for obj in data]

        rows = [list(value.values()) for value in used_data]

        table = Texttable()
        table.set_max_width(0)
        table.header(used_keys)
        table.add_rows(rows, header=False)

        print(table.draw())

    @staticmethod
    def print_data_table(data: List[ExtractedObject]):
        used_keys = ['text', 'block', 'par', 'line', 'word', 'confidence', 'top', 'bottom', 'height', 'middle_line']
        used_data = [{key: obj.__getattribute__(key) for key in used_keys} for obj in data]

        rows = [list(value.values()) for value in used_data]

        table = Texttable()
        table.set_max_width(0)
        table.header(used_keys)
        table.add_rows(rows, header=False)

        print(table.draw())

    @staticmethod
    def extract_date(data: ExtractedTree):
        texts = [obj.text for obj in data.get_words()]

        for text in texts:
            if len(text) < 5 or len(text) > 15:
                continue

            # 12-10-2021 and other delimiters
            possible_date = re.search('.?.[-.,|/].?.[-.,|/][12][0-9]{3}', text)

            if possible_date:
                return possible_date[0]
        return None

    @staticmethod
    def extract_total(data: ExtractedTree, image_shape):
        total_node = TextManager.search_total(data, image_shape[1])
        total_line = total_node.parent

        possible_total = re.search('[0-9]+[.,][0-9]{2}', total_line.text)

        if possible_total:
            return possible_total[0]

        return None

    @staticmethod
    def split_by_regions(data: ExtractedTree, image_shape):
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
    def search_cif(data: ExtractedTree):
        # C.I.F. and small errors
        # Cod Identificare Fiscala
        for d in data.get_words():
            if re.search('[C08][.]?[I1][.]?[FP]', d.text):
                return d

        lines_data = data.get_lines()

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
    def search_total(data: ExtractedTree, image_width):
        totals_found = []

        for d in data.get_words():
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

    # SHOULD BE REMOVED
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
    def extract_store(data: ExtractedTree):
        # Not confirmed from a legitimate source, but most of the time
        # the store is located on the first line in the document
        first_line = data.get_lines()[0]
        store = first_line.text

        store = re.sub('^S[.]?C[.]? ', '', store)       # Exclude S.C.
        store = re.sub(' S[.]?A[.]?$', '', store)       # Exclude S.A.
        store = re.sub(' S[.]?R[.]?L[.]?$', '', store)  # Exclude S.R.L.
        store = re.sub('[^a-zA-Z ]', '', store)         # Exclude non-alpha characters
        store = re.sub(' {2,}', ' ', store)             # Remove multiple spaces

        return store.strip()

def pprint(message):
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(str(now) + ' [TextManager] ' + str(message))
