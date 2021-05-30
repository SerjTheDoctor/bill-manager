from lib.image_manager import ImageManager
from lib.image_helper import augment_image, draw_delimiter
from lib.text_manager import TextManager
from lib.utils import get_extension, pretty_dict
from datetime import datetime
import cv2
import os
import imutils

def process(path, env='development'):
    pprint("####### " + path + " #######")

    # -- Image processing -- #
    image_params = {
        'de_skew_binary_block_size': 17,
        'de_skew_binary_offset': 10
    }
    if env == 'test':
        image_params['show_progress_images'] = False
    image = ImageManager.process(path, image_params)

    # cv2.imwrite('processedimage.jpg', image)

    # -- Text parsing -- #
    text_params = {
        'ocr-engine': 'google'
    }
    recognized_data, all_data = TextManager.recognize(image, get_extension(path), text_params)

    pprint("Found: " + pretty_dict(recognized_data))

    # -- Augmented image -- #

    if env != 'test':
        pprint('Augmenting image')
        augmented_image = augment_image(image, all_data)

        delimiters = recognized_data['delimiters']
        if delimiters[0] is not None:
            augmented_image = draw_delimiter(augmented_image, delimiters[0])

        if delimiters[1] is not None:
            augmented_image = draw_delimiter(augmented_image, delimiters[1])

        ImageManager.show(augmented_image, path, only_destroy_this=False)
        # ImageManager.show(augmented_image, path, wait=False)

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
    # process('../uploads/auchan-2.jpg')
    process_all()

    cv2.waitKey(0)  # waits until a key is pressed
    cv2.destroyAllWindows()

    print("Finished")

