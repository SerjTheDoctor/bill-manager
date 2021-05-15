import cv2 as cv
import lib.words as Words
import re
from lib.ImageManager import ImageManager
from lib.TextManager import TextManager


def get_date(path):
    img = ImageManager.open_image(path)
    img = ImageManager.apply_brightness_contrast(img)

    data = TextManager.extract_data(img)
    texts = [obj["text"] for obj in data]

    print(texts)

    for text in texts:
        if len(text) < 5 or len(text) > 15:
            continue

        possible_date = re.search('^.?.-.?.-....', text)

        if possible_date:
            return possible_date.string

    return None


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


def main():
    img = ImageManager.open_image("1-min-min.jpg")
    # cv.imshow('image', img)

    img2 = ImageManager.apply_brightness_contrast(img)
    diff_images = cv.hconcat((img, img2))
    cv.imshow("diff", diff_images)

    print_compared_text(TextManager.extract_text(img), TextManager.extract_text(img2))

    cv.waitKey(0)  # waits until a key is pressed
    cv.destroyAllWindows()  # destroys the window showing image


if __name__ == "__main__":
    main()
