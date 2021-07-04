from lib.text_manager import TextManager
from texttable import Texttable
import numpy as np
import cv2

def print_data_table(data):
    used_keys = ['text', 'block', 'par', 'line', 'word', 'conf']
    used_data = [{key: obj[key] for key in used_keys} for obj in data]


    rows = [list(value.values()) for value in used_data]

    table = Texttable()
    table.set_max_width(0)
    table.header(used_keys)
    table.add_rows(rows, header=False)

    print(table.draw())

IMPORTANT_WORDS = [
    'S.C.', 'PROFI ROM FOOD', 'S.R.L',
    '1.000', 'Buc', 'x', '2.69',
    'SUGUS', 'JELLYMANIA', 'VIE', '2.69 B',
    '13.79',
    'PUFINA', 'HARTIE', 'IGIEN8', '13.79 A',
    '2.000', '6.99',
    'APA', 'DE', 'IZVOR', 'IZVOARE', '13.98 B',
    '2.49',
    'CIPI', 'ACADELE', 'POPSY', '4.98 B',
    'TOTAL', '35.44'
]

def print_compared_text(text1, text2):
    # Compare side-by-side two texts
    lines1 = text1.split("\n")
    lines2 = text2.split("\n")

    fit1, total = TextManager.compute_fitness(text1, IMPORTANT_WORDS)
    fit2, _ = TextManager.compute_fitness(text2, IMPORTANT_WORDS)

    max_length_1 = max([len(line) for line in lines1])

    print(
        "Word fitness: {}/{}".format(fit1, total).ljust(max_length_1)
        + " | Word fitness: "
        + "{}/{}\n".format(fit2, total)
    )

    for i in range(max(len(lines1), len(lines2))):
        display_l1 = ""
        display_l2 = ""

        if i < len(lines1):
            display_l1 = lines1[i]
        if i < len(lines2):
            display_l2 = lines2[i]

        diff = display_l1.ljust(max_length_1) + " | " + display_l2
        print(diff)


"""
    bimg = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)
    bimg = show_blocks(bimg, blocks, (0, 0, 255), text="B")
    # cv2.imwrite('blocks.jpg', bimg)

    # bimg = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)
    paragraphs = []
    for block in blocks:
        paragraphs.extend(block.paragraphs)
    bimg = show_blocks(bimg, paragraphs, (255, 110, 128), text="P")
    # cv2.imwrite('paragraphs.jpg', bimg)

    # bimg = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)
    words = []
    for block in blocks:
        for para in block.paragraphs:
            words.extend(para.words)
    bimg = show_blocks(bimg, words, (102, 204, 0), text="W")
    # cv2.imwrite('words.jpg', bimg)


    cv2.imshow("Blocks", bimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
"""
def show_blocks(bimage, blocks, color, text=None):
    for i, block in enumerate(blocks):
        vertices = [[v.x, v.y] for v in block.bounding_box.vertices]
        coords = []     # Import order_pointsorder_points(np.array(vertices))

        start = (int(coords[0][0]) - 4, int(coords[0][1]) - 4)
        end = (int(coords[2][0]) + 4, int(coords[2][1]) + 4)
        # r = random.randrange(256)
        # g = random.randrange(256)
        # b = random.randrange(256)
        # color = (r, g, b)
        bimage = cv2.rectangle(bimage, start, end, color, 1)

        # if text:
        #     text_origin = (max(5, start[0]), start[1] - 5)
        #     bimage = cv2.putText(bimage, text + str(i), text_origin, cv2.FONT_HERSHEY_PLAIN, 0.9, color)

    return bimage

    # cv2.imshow("Blocks", bimage)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# From image_helper.py
# Used to show the process of adding a word to a line
# def quick_thing(i, image, line, word):
#     cimg = image.copy()
#
#     cimg = cv2.rectangle(cimg, line.box_start, line.box_end, (240, 174, 0))
#     cimg = cv2.rectangle(cimg, word.box_start, word.box_end, (70, 200, 145))
#     cimg = draw_y_delimiter(cimg, (word.top+word.bottom)/2+1, (100, 100, 100))
#     print("{} ({}, {} = {})".format(word.text, word.top, word.bottom, (word.top+word.bottom)/2+1))
#
#     cimg = imutils.resize(cimg[:150], height=200)
#     cv2.imwrite("lining{}.jpg".format(i), cimg)
#
#     show_image(cimg, "some title")
