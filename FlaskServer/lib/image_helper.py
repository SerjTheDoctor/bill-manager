import cv2

def image2bytes(image, extension: str):
    if not extension.startswith('.'):
        extension = '.' + extension

    status, encoded_image = cv2.imencode(extension, image)

    if not status:
        return None

    return encoded_image.tobytes()
