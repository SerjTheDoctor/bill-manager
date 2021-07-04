from lib.image_manager import ImageManager
from lib.image_helper import show_image, augment_image, draw_y_delimiter, draw_x_delimiter
from lib.text_manager import TextManager
from lib.utils import get_extension, pretty_bill
from datetime import datetime
import cv2
import os
import imutils

def process(path, ext=None, env='development'):
    pprint("####### " + path + " #######")

    # -- Image processing -- #
    image_manager = ImageManager(path, env)
    image_params = {
        'de_skew_binary_block_size': 17,
        'de_skew_binary_offset': 10,
    }
    image = image_manager.process(image_params)

    # cv2.imwrite('processed_image.jpg', image)

    # -- Text parsing -- #
    file_ext = get_extension(path) if ext is None else ext
    text_manager = TextManager(image, file_ext, env)
    text_params = {
        'ocr-engine': 'google'
    }
    recognized_data, delimiters, all_data = text_manager.recognize(text_params)

    # -- Augmented image -- #

    if env == 'development':
        print(pretty_bill(recognized_data))

        pprint('Augmenting image')
        # colored_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        augmented_image = augment_image(image, all_data)

        if delimiters[0] is not None:
            augmented_image = draw_y_delimiter(augmented_image, delimiters[0])

        if delimiters[1] is not None:
            augmented_image = draw_y_delimiter(augmented_image, delimiters[1])

        show_image(augmented_image, path, only_destroy_this=False)

    return recognized_data


def pprint(message):
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(str(now) + ' [ReceiptCPU] ' + str(message))

def process_all():
    results = ''
    for filename in os.listdir("../uploads/"):
        print("Trying to process " + str(filename))
        filepath = '../uploads/' + filename
        date = process(filepath)
        results += '{}: {}\n'.format(filename, date)
        print("Finished processing " + str(filename))

    print(results)

if __name__ == '__main__':
    # process('../uploads/fusionCuisine-2.jpeg')
    # process_all()

    cv2.waitKey(0)  # waits until a key is pressed
    cv2.destroyAllWindows()

    print("Finished")
