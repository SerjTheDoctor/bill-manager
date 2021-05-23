from lib.image_manager import ImageManager
from lib.text_manager import TextManager
from datetime import datetime
import os

def process(path, env='development'):
    pprint("####### " + path + " #######")

    image_params = {}

    if env == 'test':
        image_params['show_progress_images'] = False

    image = ImageManager.process(path, image_params)

    text_params = {}
    recognized_data, all_data = TextManager.recognize(image, text_params)

    pprint("Found: " + str(recognized_data))

    if env != 'test':
        pprint('Augmenting image')
        augmented_image = ImageManager.augment_image(image, all_data)

        pprint('Displaying image')
        ImageManager.show(augmented_image, 'Augmented image')

    return recognized_data

def pprint(message):
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(str(now) + ' [ReceiptCPU] ' + str(message))

if __name__ == '__main__':
    process('../uploads/flaviandaCrisan-1.jpg')

    # results = ''
    # for filename in os.listdir("../uploads/"):
    #     print("Trying to process " + str(filename))
    #     filepath = '../uploads/' + filename
    #     date = process(filepath)
    #     results += '{}: {}\n'.format(filename, date)
    #     print("Finished processing " + str(filename))

    print("Finished")
    # print(results)
