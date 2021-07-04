from lib.image_helper import show_quick_augmented_image
from model import ExtractedTree, Node, NodeType
from lib.utils import pretty_list, pretty_dict, string2float
from datetime import datetime
from typing import List
import re

PRICE_REGEX = '[0-9]+[.,][0-9]{1,2}'
QUANTITY_REGEX = '( X )'

# Quantity Position Style
#   BEFORE - the QUANTITY is before the name, aka it's on the line above
#   AFTER  - the QUANTITY is after the name, aka it's on the same line or below

class ItemRecognizer:
    def __init__(self, image, environment, debug=None):
        self.image = image
        self.env = environment
        self.debug = debug if debug is not None else environment == 'development'

    def extract_items(self, data: ExtractedTree):
        d1, d2 = self.split_by_regions(data)
        quantity_position_style = None

        # Keep only lines inside of `items zone`
        lines = data.get_lines()
        lines = [line for line in lines if line.top > d1 and line.bottom < d2]
        lines = self._filter_falsy_items(lines)
        lines = self._sort_items_by_position(lines)
        lines = self._fix_prices(lines)

        # Go go!
        lines_copy = lines.copy()
        items_data = self.__try_parse_items(lines_copy, quantity_position_style)

        if self.debug:
            # print(pretty_list(lines, 1))
            show_quick_augmented_image(self.image, lines, wait=True)

        return items_data

    def __try_parse_items(self, lines: List[Node], quantity_position_style):
        # Try to parse the items assuming the quantity is after the name of the product
        item = {}
        ok = True
        lines_to_remove = []

        # Get the last price as a point of start
        last_price_line = None
        last_price_word = None
        for line in reversed(lines):
            for word in reversed(line.children):
                if self._is_on_price_column(word):
                    item['total_price'] = word.text
                    last_price_word = word
                    last_price_line = line
                    lines_to_remove.append(line)
                    break
            if last_price_line:
                break
        self.pprint('Started parsing: "{}"'.format(last_price_line))

        if not last_price_line:
            return []

        words = last_price_line.text.split()

        if re.search(QUANTITY_REGEX, last_price_line.text):
            # Quantity is on the same line with price
            # 1 BUC X 12.34 12.34 A
            self.pprint('Quantity is on the same line')

            # Try to extract quantity and update the item
            # i - the index where the extraction finished
            item_part, i = self.__try_extract_quantity(words, item)
            item.update(item_part)

            if i > 0:
                # If we do have something on the left of quantity,
                # it means we are lucky and that is the name of the product
                # Ketchup Chili 1 BUC X 12.34 12.34 A
                item['name'] = ' '.join(words[:i])
                quantity_position_style = 'AFTER'
                self.pprint('RECEIPT STYLE IS ## AFTER ## !')
            else:
                # If not, we have to find the name
                line_pos = lines.index(last_price_line)

                # If we know the style of the receipt,
                # we know where to look for
                if quantity_position_style == 'BEFORE':
                    next_line = lines[line_pos + 1]
                    item['name'] = next_line.text
                    lines_to_remove.append(next_line)
                elif quantity_position_style == 'AFTER':
                    prev_line = lines[line_pos - 1]
                    item['name'] = prev_line.text
                    lines_to_remove.append(prev_line)
                else:
                    # If we don't know the style, we try to guess it
                    # and we search for it above and below the current line
                    if line_pos == len(lines) - 1:
                        # If the current line is the last one, it is safe to assume
                        # that the name is above, so the style is AFTER
                        prev_line = lines[line_pos - 1]
                        item['name'] = prev_line.text
                        lines_to_remove.append(prev_line)
                        quantity_position_style = 'AFTER'
                    else:
                        # We assume the line bellow is the one containing the item
                        # and the style is BEFORE
                        next_line = lines[line_pos + 1]
                        item['name'] = next_line.text
                        lines_to_remove.append(next_line)
                        quantity_position_style = 'BEFORE'
        elif len(words) > 2:
            # Name is on the same line with price
            # Ketchup Chili 12.34 A
            pos = words.index(last_price_word.text)
            item['name'] = ' '.join(words[:pos])

            line_pos = lines.index(last_price_line)

            # Known style is BEFORE
            if quantity_position_style == 'BEFORE':
                prev_line = lines[line_pos - 1]
                quantity_line = prev_line

            # Known style is AFTER
            elif quantity_position_style == 'AFTER':
                next_line = lines[line_pos + 1]
                quantity_line = next_line

            # Don't know the style, but it's the last line
            elif line_pos == len(lines) - 1:
                prev_line = lines[line_pos - 1]
                quantity_line = prev_line
                quantity_position_style = 'BEFORE'

            # Meh, whatever
            else:
                next_line = lines[line_pos + 1]
                quantity_line = next_line
                quantity_position_style = 'AFTER'

            if re.search(QUANTITY_REGEX, quantity_line.text):
                item_part, i = self.__try_extract_quantity(quantity_line.text.split(), item)
                item.update(item_part)
                lines_to_remove.append(quantity_line)
                if i != 0:
                    self.pprint('I think this should have been 0')
            else:
                ok = False
                self.pprint('WARNING: Omitting! Style {} does not match: {}'.format(quantity_position_style, quantity_line.text))
                # raise Exception(
                #     'Style {}, but this is not quantity: {}'.format(quantity_position_style, quantity_line.text)
                # )
        else:
            ok = False
            self.pprint('Case not found')
            # raise Exception('Unknown case: "{}"'.format(last_price_line.text))

        self.pprint('Item found: {}'.format(pretty_dict(item)))

        for removable in lines_to_remove:
            lines.remove(removable)

        if ok and self.debug:
            show_quick_augmented_image(self.image, lines_to_remove)

        other_items = self.__try_parse_items(lines, quantity_position_style)

        return [item] + other_items if ok else other_items

    def __try_extract_quantity(self, words, item):
        # We search for the 'x'
        i = len(words) - 1
        while i >= 0:
            if re.search('X', words[i]):
                break
            i -= 1

        # On words[i+1] we can find the item per unit
        item['unit_price'] = words[i + 1]

        # Go to the left of 'X' to find the measurement unit
        i -= 1

        # Other characters like . (dot) can be found between unit and 'X'
        # and we should skip them
        # ex: 1 BUC . X 12.34
        if not re.search('[a-zA-Z]', words[i]):
            i -= 1

        # We save the measurement unit
        item['unit'] = words[i]

        if i > 0:
            # One item to the left we should find the quantity
            i -= 1
            item['quantity'] = words[i]
        else:
            # If there is nothing in the left, then we can assume
            # some misreading was made and we can take quantity = 1
            # (maybe we can divide total_price/unit_price)
            self.pprint('Quantity was not found, computing or defaulting to 1')
            try:
                quantity = string2float(item['total_price']) / string2float(item['unit_price'])
                # quantity = str(quantity) if int(quantity) == quantity else '1' # why this?
            except Exception:
                quantity = '1'
            item['quantity'] = quantity

        return item, i

    def _fix_prices(self, lines: List[Node]):
        separate_prices = []
        to_remove = []

        # Search for prices that are alone on their line
        for line in lines:
            if len(line.children) <= 2 and self._is_on_price_column(line):
                for word in line.children:
                    separate_prices.append(word)
                to_remove.append(line)

        for l in to_remove:
            lines.remove(l)

        for word in separate_prices:
            min_dist_lines = sorted(lines[:], key=lambda l: abs(word.middle - l.middle))
            min_dist_line = min_dist_lines[0]
            old_line = word.parent
            min_dist_line.add_children(word)

        return lines

    def _is_on_price_column(self, node: Node):
        return self.image.shape[1] * 3/4 < node.left and re.search(PRICE_REGEX, node.text)

    def split_by_regions(self, data: ExtractedTree):
        height, width = self.image.shape

        cif = self.search_cif(data)
        total = self.search_total(data, width)

        if cif:
            cif_delimiter = cif.top + cif.height / 2
        else:
            cif_delimiter = 0
            self.pprint('Could not find CIF')

        if total:
            total_delimiter = total.top + total.height / 2
        else:
            total_delimiter = height
            self.pprint('Could not find TOTAL')

        return cif_delimiter, total_delimiter

    def _filter_falsy_items(self, items: List[Node]):
        new_items = []

        for line in items:
            # Remove lines containing BON FISCAL
            # This usually appears on the first lines
            if re.search('BON FISCAL', line.text):
                continue

            # Remove lines containing SUBTOTAL
            if re.search('SUBTOTAL', line.text):
                continue

            new_items.append(line)

        return new_items

    def _sort_items_by_position(self, items: List[Node]):
        return sorted(items, key=lambda item: item.top)

    def search_cif(self, data: ExtractedTree):
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

    def search_total(self, data: ExtractedTree, image_width):
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

    def pprint(self, message):
        if self.debug:
            now = datetime.now().strftime('%H:%M:%S.%f')
            print(str(now) + ' [ItemRecognizer] ' + str(message))
