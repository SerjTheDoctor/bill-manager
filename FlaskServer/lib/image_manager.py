import cv2 as cv
import random

class ImageManager:
    @staticmethod
    def open_image(path):
        # Reads image from path
        image = cv.imread(path)
        image = cv.resize(image, (756, 1008))
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        # img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        return image

    @staticmethod
    def show_and_wait(image, title='Image'):
        cv.imshow(title, image)
        cv.waitKey(0)  # waits until a key is pressed
        cv.destroyAllWindows()  # destroys the window showing image

    @staticmethod
    def apply_brightness_and_contrast(image, alpha=1, beta=60):
        # Applies brightness and contrast to the image
        # alpha - contrast (1.0 - 3.0)
        # beta  - brightness (0 - 100)
        return cv.convertScaleAbs(image, alpha=alpha, beta=beta)

    @staticmethod
    def augment_image(image, data):
        pad = 1
        colors = {}

        for obj in data:
            start = (obj['left'] - pad, obj['top'] - pad)
            end = (obj['left'] + obj['width'] + pad, obj['top'] + obj['height'] + pad)
            block = str(obj['block'])

            if block not in colors:
                # TODO: maybe change to some standard colors
                r = random.randrange(257)
                g = random.randrange(257)
                b = random.randrange(257)
                colors[block] = (r, g, b)

            # image = cv.rectangle(image, start, end, colors[block], 1)
            image = cv.rectangle(image, start, end, (0, 0, 0), 1)

        return image
