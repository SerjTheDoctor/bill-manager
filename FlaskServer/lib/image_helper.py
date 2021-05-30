from model import ExtractedTree, NodeType
import random
import cv2

def image2bytes(image, extension: str):
    if not extension.startswith('.'):
        extension = '.' + extension

    status, encoded_image = cv2.imencode(extension, image)

    if not status:
        return None

    return encoded_image.tobytes()

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

def draw_delimiter(image, del_y, color=(255, 0, 0)):
    start = (10, int(del_y))
    end = (image.shape[1] - 10, int(del_y))

    image = cv2.putText(image, str(start[1]), (end[0], start[1]-3), cv2.FONT_HERSHEY_PLAIN, 1, color)
    image = cv2.line(image, start, end, color, 2)

    return image