import cv2
import pytesseract
import random
import imutils
import os
import io
import numpy as np
from texttable import Texttable
from skimage.filters import threshold_local
from lib.image_manager import ImageManager
from lib.text_manager import TextManager
from lib.receipt_cpu import process
from google.cloud import vision


# process('../uploads/auchan-2.jpg')

def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    img = vision.Image(content=content)

    response = client.text_detection(image=img)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

# detect_text('../uploads/auchan-2.jpg')

def order_points(pts):
    # initialize a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped

def testing_extract_text(path='../receipts/1.jpg'):
    img = ImageManager.open_image(path)
    img = ImageManager.apply_contrast_and_brightness(img)

    data = []#TextManager.extract_tesseract(img)

    # print_data_table(data)

    img = ImageManager.augment_image(img, data)
    cv2.imshow('Receipt Viewer', img)

    cv2.waitKey(0)   # waits until a key is pressed
    cv2.destroyAllWindows()  # destroys the window showing image

# testing_extract_text()
# for i in [1000 + i for i in range(10)]:
#     testing_extract_text('../receipts/dataset-SRD/' + str(i) + '-receipt.jpg')


def get_coords(x, image_height, image_width):
    pass

def fill_border(image, left, right):
    print('Should fill from ' + str(left) + ' to ' + str(right))

def fix_outside_edge(image):
    first_row = list(image[0])[:-1]
    last_column = list(image[:, -1])[:-1]
    last_row = list(image[-1])[:-1]
    first_column = list(image[:, 0])[:-1]

    print(image.shape)
    border = first_row + last_column + last_row + first_column

    edges = []
    for i, pixel in enumerate(border):
        if pixel != 0:
            edges.append(i)

    print('Edges: ' + str(edges))

    for i in range(len(edges)):
        if i == 0:
            left = edges[-1]
            right = edges[i+1]

            dl = len(border) - left + edges[i]
            dr = right - edges[i]
        elif i == len(edges) - 1:
            left = edges[i-1]
            right = edges[0]

            dl = edges[i] - left
            dr = len(border) + right - edges[i]
        else:
            left = edges[i-1]
            right = edges[i+1]

            dl = edges[i] - left
            dr = right - edges[i]

        if dr < dl:
            fill_border(image, edges[i], right)
        else:
            fill_border(image, left, edges[i])


def apply_edge_detection(image):
    # convert the image to grayscale, blur it, and find edges in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    gray = cv2.copyMakeBorder(gray, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    edged = cv2.Canny(gray, 75, 200)
    # edged_imutils = imutils.auto_canny(gray)

    # fix_outside_edge(edged)

    # show the original image and the edge detected image
    print("STEP 1: Edge Detection")
    cv2.imshow("Image", image)
    cv2.imshow("Grayed", gray)
    cv2.imshow("Edged", edged)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return edged

def process_edges(edged_image, orig_image):
    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts = cv2.findContours(edged_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # findContours returns different parameters depending on the version
    # - opencv2 or opencv4+ returns [contours, hierarchy]
    # - opencv3 returns [image, contours, hierarchy]
    # using imutils.grab_contours we do not have to worry about that
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screen_cnt = None
    screen_cnts = []

    # loop over the contours
    for c in cnts:
        # Computes the perimeter and approximates the contour
        perimeter = cv2.arcLength(c, True)
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(c, epsilon, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        screen_cnts.append(approx)
        if len(approx) == 4:
            screen_cnt = approx
            break
        # else:

    if screen_cnt is None:
        print('No screen contour found, bounding box the biggest one')
        x, y, w, h = cv2.boundingRect(cnts[0])
        screen_cnt = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])

    # show the contour (outline) of the piece of paper
    print("STEP 2: Find contours of paper")
    cv2.drawContours(orig_image, [screen_cnt], -1, (0, 255, 0), 2)

    # cv2.drawContours(orig_image, screen_cnts, -1, (200, 255, 200), 1)
    cv2.imshow("Outline", imutils.resize(orig_image, height=1000))

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return screen_cnt

def de_skew_image(image, contour, orig_ratio):
    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(image, contour.reshape(4, 2) * orig_ratio)

    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method="gaussian")
    warped = (warped > T).astype("uint8") * 255

    # show the original and scanned images
    print("STEP 3: Apply perspective transform")
    # cv2.imshow("Original", imutils.resize(image, height=650))
    # cv2.imshow("Scanned", imutils.resize(warped, height=650))

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return warped

def testing_image_processing(path='../receipts/3.jpg'):
    # open image, compute the ratio of the old height
    # to the new height, clone it, and resize it
    image = cv2.imread(path)
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    edged = apply_edge_detection(image)

    # Compute the contour
    contour = process_edges(edged, image)

    # top-down view
    processed_image = de_skew_image(orig, contour, ratio)
    # processed_image = imutils.resize(processed_image, height=600)

    data = []#TextManager.extract_tesseract(processed_image)

    # print_data_table(data)

    img = ImageManager.augment_image(processed_image, data)
    cv2.imshow('Receipt Viewer', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def run_all():
    for filename in os.listdir("../uploads/"):
        print("Trying to process " + str(filename))
        filepath = '../uploads/' + filename
        testing_image_processing(filepath)
        print("Finished processing " + str(filename))

    print("Finished")


# testing_image_processing('../uploads/InternationalPaper-1.jpeg')
# for i in [1000 + i for i in range(10)]:
#     testing_image_processing('../receipts/dataset-SRD/' + str(i) + '-receipt.jpg')
