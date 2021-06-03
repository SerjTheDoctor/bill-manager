from model import ExtractedTree, NodeType, Node
from typing import List
import random
import cv2


def open_image(path):
    # Reads image from path
    image = cv2.imread(path)
    # image = cv2.resize(image, (756, 1008))

    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    return image


def show_image(image, title='Image', wait=True, only_destroy_this=True):
    cv2.imshow(title, image)

    if wait:
        cv2.waitKey(0)  # waits until a key is pressed

        if only_destroy_this:
            cv2.destroyWindow(title)
        else:
            cv2.destroyAllWindows()

def image2bytes(image, extension: str):
    if not extension.startswith('.'):
        extension = '.' + extension

    status, encoded_image = cv2.imencode(extension, image)

    if not status:
        return None

    return encoded_image.tobytes()

def show_quick_augmented_image(image, data: List[Node], wait=True):
    tree = ExtractedTree()
    tree.root.children = data

    image = augment_image(image, tree, NodeType.LINE)
    title = 'Quick Augmented Image '# + str(random.randint(0, 10))
    show_image(image, title, wait=wait)

def augment_image(image, data_tree: ExtractedTree, nodes_type=NodeType.LINE, scale=1, pad=1):
    colored_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    if nodes_type == NodeType.WORD:
        data = data_tree.get_words()
    else:
        data = data_tree.get_lines()

    for obj in data:
        start = (obj.left * scale - pad, obj.top * scale - pad)
        end = (obj.right * scale + pad, obj.bottom * scale + pad)

        r = random.randrange(257)
        g = random.randrange(257)
        b = random.randrange(257)
        color = (r, g, b)

        colored_image = cv2.rectangle(colored_image, start, end, color, 2)

        text_origin = (start[0], start[1] - 5)
        # colored_image = cv2.putText(colored_image, str(obj), text_origin, cv2.FONT_HERSHEY_PLAIN, 0.7, color)

    return colored_image

def draw_y_delimiter(image, del_y, color=(255, 0, 0)):
    start = (10, int(del_y))
    end = (image.shape[1] - 10, int(del_y))

    image = cv2.putText(image, str(start[1]), (end[0]-10, start[1]-5), cv2.FONT_HERSHEY_PLAIN, 1, color)
    image = cv2.line(image, start, end, color, 2)

    return image

def draw_x_delimiter(image, del_x, color=(255, 0, 0)):
    start = (int(del_x), 10)
    end = (int(del_x), image.shape[0] - 10)

    image = cv2.putText(image, str(start[1]), (start[0]-5, end[1]-10), cv2.FONT_HERSHEY_PLAIN, 1, color)
    image = cv2.line(image, start, end, color, 2)

    return image

