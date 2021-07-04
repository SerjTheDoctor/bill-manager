import pytesseract
import re
from typing import List, Optional
from datetime import datetime
from lib.utils import pretty_list
from lib.image_helper import image2bytes, show_quick_augmented_image
from lib.item_recognizer import ItemRecognizer
from lib.text_processor import TextProcessor
from model import ExtractedTree, Node, NodeType
from model import ExtractedObject
from texttable import Texttable
from google.cloud import vision
import cv2
import numpy as np
import random

class TextManager:
    def __init__(self, image, image_file_extension, environment):
        self.image = image
        self.extension = image_file_extension
        self.debug = environment == 'development'
        self.item_recognizer = ItemRecognizer(image, environment)
        self.text_processor = TextProcessor(environment)

    def recognize(self, params=None):
        if params is None:
            params = {}

        ocr = params.get('ocr-engine', 'tesseract')

        self.pprint('Extracting data using {} engine'.format(ocr.capitalize()))

        if ocr == 'tesseract':
            data = self.extract_tesseract(self.image)
        else:
            data = self.extract_google_vision()

        date = self.extract_date(data)
        total = self.extract_total(data)
        store = self.extract_store(data)

        date = self.text_processor.process_date(date)
        total = self.text_processor.process_total(total)
        store = self.text_processor.process_store(store)

        items = self.item_recognizer.extract_items(data)

        d1, d2 = self.item_recognizer.split_by_regions(data)

        return {
            'date': date,
            'total': total,
            'store': store,
            'items': items,
        }, [d1, d2], data

    def extract_google_vision(self) -> ExtractedTree:
        client = vision.ImageAnnotatorClient()

        bytes_image = image2bytes(self.image, self.extension)
        vision_image = vision.Image(content=bytes_image)

        data = []
        response = client.document_text_detection(image=vision_image)

        if len(response.full_text_annotation.pages) <= 0:
            raise Exception("No text detected")

        blocks = response.full_text_annotation.pages[0].blocks

        # print(blocks)

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

            # Show the process of creating lines step by step
            # show_quick_augmented_image(image, tree_data.get_lines())

        # show_quick_augmented_image(image, tree_data.get_lines())

        # Print data in a table
        # TextManager.print_data_tree_table(tree_data, NodeType.LINE)

        return tree_data

    def extract_tesseract(self, language='ron+eng') -> List[ExtractedObject]:
        data = pytesseract.image_to_data(self.image, lang=language, output_type=pytesseract.Output.DICT)

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

        vertical_data = self.reindex_blocks(vertical_data)


        # DEBUG
        # TextManager.print_data_table(vertical_data)
        # pprint(pretty_list(vertical_data))

        return vertical_data

    def reindex_blocks(self, data: List[ExtractedObject]):
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

    def extract_date(self, data: ExtractedTree):
        words = data.get_words()

        for word in words:
            if len(word.text) < 5:
                continue

            # 12-10-2021 and other delimiters
            possible_date = re.search('.?.[-.,|/].?.[-.,|/][12][0-9]{3}', word.text)

            if not possible_date:
                # 2021-10-12
                possible_date = re.search('[12][0-9]{3}[-.,|/].?.[-.,|/].?.', word.text)

            if possible_date:
                if self.debug:
                    show_quick_augmented_image(self.image, [word])
                return possible_date.group()
        return None

    def extract_total(self, data: ExtractedTree):
        total_node = self.item_recognizer.search_total(data, self.image.shape[1])
        if total_node is None:
            return None

        total_line = total_node.parent

        possible_total = re.search('[0-9]+[.,][0-9]{2}', total_line.text)

        if possible_total:
            if self.debug:
                show_quick_augmented_image(self.image, [total_line])
            return possible_total[0]

        return None

    def extract_store(self, data: ExtractedTree):
        # Not confirmed from a legitimate source, but most of the time
        # the store is located on the first line in the document
        first_line = data.get_lines()[0]
        store = first_line.text

        if self.debug:
            show_quick_augmented_image(self.image, [first_line])

        return store.strip()

    def pprint(self, message):
        if self.debug:
            now = datetime.now().strftime('%H:%M:%S.%f')
            print(str(now) + ' [TextManager] ' + str(message))
