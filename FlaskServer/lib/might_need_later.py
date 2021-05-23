from lib.text_manager import TextManager
import lib.words as Words
from texttable import Texttable

def print_data_table(data):
    used_keys = ['text', 'block', 'par', 'line', 'word', 'conf']
    used_data = [{key: obj[key] for key in used_keys} for obj in data]


    rows = [list(value.values()) for value in used_data]

    table = Texttable()
    table.set_max_width(0)
    table.header(used_keys)
    table.add_rows(rows, header=False)

    print(table.draw())

def print_compared_text(text1, text2):
    # Compare side-by-side two texts
    lines1 = text1.split("\n")
    lines2 = text2.split("\n")

    fit1, total = TextManager.compute_fitness(text1, Words.IMPORTANT_WORDS)
    fit2, _ = TextManager.compute_fitness(text2, Words.IMPORTANT_WORDS)

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
