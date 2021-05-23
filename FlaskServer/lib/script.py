from lib.image_manager import ImageManager
from lib.text_manager import TextManager


def get_date(path):
    img = ImageManager.open_image(path)
    img = ImageManager.apply_contrast_and_brightness(img)

    # ImageManager.show(img)

    data = TextManager.extract_data(img)
    date = TextManager.extract_date(data)

    return date


if __name__ == "__main__":
    print(get_date("../uploads/1-min-min.jpg"))
