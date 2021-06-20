import cv2
import random
import imutils
import numpy as np
from skimage.filters import threshold_local
from lib.image_helper import open_image, order_points
from datetime import datetime

# Maybe remove class and leave only methods
class ImageManager:
    @staticmethod
    def process(path, params=None):
        if params is None:
            params = {}

        if isinstance(path, str):
            image = open_image(path)
        else:
            image = path

        original_image = image.copy()
        image_ratio = image.shape[0] / 500.0
        image = imutils.resize(image, height=500)

        edges_image = ImageManager.detect_edges(
            image,
            gaussian_kernel_size=params.get('gaussian_kernel_size', (5, 5)),
            canny_min=params.get('canny_min', 75),
            canny_max=params.get('canny_max', 200),
            visuals=params.get('show_progress_images', True)
        )
        receipt_polygon, all_contours = ImageManager.find_receipt_contour(edges_image)

        if params.get('show_progress_images', True):
            # ImageManager.draw_contours(image, all_contours, color='all_random', thickness=1)
            ImageManager.draw_contours(image, [receipt_polygon])

        receipt_centered_image = ImageManager.de_skew_image(
            original_image,
            image_ratio,
            receipt_polygon,
            binary_bsize=params.get('de_skew_binary_block_size', 11),
            binary_offset=params.get('de_skew_binary_offset', 10),
            binary_method=params.get('de_skew_binary_method', 'gaussian'),
            visuals=params.get('show_progress_images', True)
        )

        return imutils.resize(receipt_centered_image, height=1000)


    @staticmethod
    def apply_contrast_and_brightness(image, alpha=1, beta=60):
        # Applies brightness and contrast to the image
        # alpha - contrast (1.0 - 3.0)
        # beta  - brightness (0 - 100)
        pprint('Applying contrast: {} and brightness: {}'.format(alpha, beta))
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    @staticmethod
    def detect_edges(image, gaussian_kernel_size=(5, 5), canny_min=75, canny_max=200, visuals=True):
        # convert the image to grayscale, blur it, and find edges in the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        pprint('Applying GaussianBlur with kernel size: {}'.format(gaussian_kernel_size))
        gray = cv2.GaussianBlur(gray, gaussian_kernel_size, 0)
        # gray = cv2.copyMakeBorder(gray, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        pprint('Running Canny Edge detector algorithm ({}, {})'.format(canny_min, canny_max))
        edged = cv2.Canny(gray, canny_min, canny_max)
        # auto_edged = imutils.auto_canny(gray)

        if visuals:
            # pprint('Displaying current images')
            cv2.imshow("Original", image)
            # cv2.imwrite('original.jpg', image)
            cv2.imshow("Gaussian Blur", gray)
            # cv2.imwrite('gaussian.jpg', gray)
            cv2.imshow("Edges", edged)
            # cv2.imwrite('edges.jpg', edged)

            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        return edged

    @staticmethod
    def find_receipt_contour(edges_image):
        # find the contours in the image with edges
        pprint('Finding contours')
        contours = cv2.findContours(edges_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # findContours returns different parameters depending on the version
        # - opencv2 or opencv4+ returns [contours, hierarchy]
        # - opencv3 returns [image, contours, hierarchy]
        # using imutils.grab_contours we do not have to worry about that
        contours = imutils.grab_contours(contours)

        # Sorting by the largest polygon
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        # pprint('Trying to find receipt contour')
        receipt_contour = None
        approx_contours = []

        for c in contours:
            # Computes the perimeter and approximates points of the contour
            perimeter = cv2.arcLength(c, True)
            epsilon = 0.02 * perimeter
            approx = cv2.approxPolyDP(c, epsilon, True)

            approx_contours.append(approx)
            # if our approximated contour has four points, then we
            # can assume that we have found our receipt
            if len(approx) == 4:
                receipt_contour = approx
                pprint('Found receipt contour')
                break

        if receipt_contour is None:
            pprint('No receipt contour found, bounding box the biggest polygon')
            x, y, w, h = cv2.boundingRect(contours[0])
            receipt_contour = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])

        return receipt_contour, approx_contours

    @staticmethod
    def draw_contours(image, contours, color=(0, 255, 0), thickness=2):
        # show the contour (outline) of the piece of paper
        nr = len(contours)
        pprint('Drawing {} contour{}'.format(nr, 's' if nr != 1 else ''))

        if len(color) == 3:
            cv2.drawContours(image, contours, -1, color, thickness)
            # cv2.imwrite('contoured.jpg', image)

            cv2.imshow("Contour", imutils.resize(image, height=1000))
            cv2.waitKey(0)
            cv2.destroyWindow("Contour")
        elif color == 'all_random':
            for c in contours:
                r = random.randrange(257)
                g = random.randrange(257)
                b = random.randrange(257)
                cv2.drawContours(image, [c], -1, (r, g, b), thickness)

                cv2.imshow("Contour", imutils.resize(image, height=1000))
                cv2.waitKey(0)
                cv2.destroyWindow("Contour")

        else:
            r = random.randrange(257)
            g = random.randrange(257)
            b = random.randrange(257)
            cv2.drawContours(image, contours, -1, (r, g, b), thickness)

            cv2.imshow("Contour", imutils.resize(image, height=1000))
            cv2.waitKey(0)
            cv2.destroyWindow("Contour")

    @staticmethod
    def de_skew_image(
            original_image, original_image_ratio, contour, binary_bsize=11,
            binary_offset=10, binary_method='gaussian', visuals=True
    ):
        # apply the four point transform to obtain a top-down
        # view of the original image
        pprint('Applying four point transformation and thresholding')
        image = ImageManager.four_point_transform(original_image, contour.reshape(4, 2) * original_image_ratio)
        # image_s = image
        # convert the warped image to grayscale, then threshold it
        # to give it that 'black and white' paper effect
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_local
        # pprint('Thresholding image')
        threshed = threshold_local(image, binary_bsize, offset=binary_offset, method=binary_method)
        image = (image > threshed).astype("uint8") * 255

        if visuals:
            # show the original and scanned images
            # cv2.imshow("Original", imutils.resize(original_image, height=650))
            # cv2.imshow("De skewed simple", imutils.resize(image_s, height=650))
            # cv2.imshow("De skewed", imutils.resize(image, height=650))
            # cv2.imshow("Warped", imutils.resize(image, height=500))
            pass
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        return image

    @staticmethod
    def four_point_transform(image, pts):
        # obtain a consistent order of the points and unpack them
        rect = order_points(pts)
        (tl, tr, br, bl) = rect

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordinates or the top-right and top-left x-coordinates
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        # compute the perspective transform matrix and then apply it
        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))

        # return the warped image
        return warped


def pprint(message):
    now = datetime.now().strftime('%H:%M:%S.%f')
    print(str(now) + ' [ImageManager] ' + str(message))
