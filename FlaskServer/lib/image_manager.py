import cv2
import random
import imutils
import numpy as np
from skimage.filters import threshold_local
from lib.image_helper import open_image, order_points
from datetime import datetime

# Maybe remove class and leave only methods
class ImageManager:
    def __init__(self, path, environment, debug=None):
        self.path = path
        self.env = environment
        self.debug = debug if debug is not None else environment == 'development'

    def process(self, params=None):
        if params is None:
            params = {}

        if isinstance(self.path, str):
            image = open_image(self.path)
        else:
            image = self.path

        original_image = image.copy()
        image_ratio = image.shape[0] / 500.0
        image = imutils.resize(image, height=500)

        edges_image = self.detect_edges(
            image,
            gaussian_kernel_size=params.get('gaussian_kernel_size', (5, 5)),
            canny_min=params.get('canny_min', 75),
            canny_max=params.get('canny_max', 200)
        )
        receipt_polygon, all_contours = self.find_receipt_contour(edges_image)

        if self.debug:
            # self.draw_contours(image, all_contours, color='all_random', thickness=1)
            self.draw_contours(image, [receipt_polygon])

        receipt_centered_image = self.de_skew_image(
            original_image,
            image_ratio,
            receipt_polygon,
            binary_bsize=params.get('de_skew_binary_block_size', 11),
            binary_offset=params.get('de_skew_binary_offset', 10),
            binary_method=params.get('de_skew_binary_method', 'gaussian'),
        )

        # cv2.imwrite('processed_image_2.jpg', receipt_centered_image)

        return imutils.resize(receipt_centered_image, height=1000)


    def apply_contrast_and_brightness(self, image, alpha=1, beta=60):
        # Applies brightness and contrast to the image
        # alpha - contrast (1.0 - 3.0)
        # beta  - brightness (0 - 100)
        self.pprint('Applying contrast: {} and brightness: {}'.format(alpha, beta))
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    def detect_edges(self, image, gaussian_kernel_size=(5, 5), canny_min=75, canny_max=200):
        # convert the image to grayscale, blur it, and find edges in the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        self.pprint('Applying GaussianBlur with kernel size: {}'.format(gaussian_kernel_size))
        gray = cv2.GaussianBlur(gray, gaussian_kernel_size, 0)
        # gray = cv2.copyMakeBorder(gray, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        self.pprint('Running Canny Edge detector algorithm ({}, {})'.format(canny_min, canny_max))
        edged = cv2.Canny(gray, canny_min, canny_max)
        # auto_edged = imutils.auto_canny(gray)

        if self.debug:
            # pprint('Displaying current images')
            cv2.imshow("Original", image)
            # cv2.imwrite('original.jpg', image)
            cv2.imshow("Gaussian Blur", gray)
            # cv2.imwrite('gaussian.jpg', gray)
            cv2.imshow("Edges", edged)
            # cv2.imwrite('edges.jpg', edged)

            cv2.waitKey(0)
            # cv2.destroyAllWindows()

        return edged

    def find_receipt_contour(self, edges_image):
        # find the contours in the image with edges
        self.pprint('Finding contours')
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
                self.pprint('Found receipt contour')
                break

        if receipt_contour is None:
            if len(contours) == 0:
                self.pprint('No contour found, bounding box the document')
                h, w = edges_image.shape
                receipt_contour = np.array([[0, 0], [w, 0], [w, h], [0, h]])
            else:
                self.pprint('No receipt contour found, bounding box the biggest polygon')
                x, y, w, h = cv2.boundingRect(contours[0])
                receipt_contour = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])

        return receipt_contour, approx_contours

    def draw_contours(self, image, contours, color=(0, 255, 0), thickness=2):
        # show the contour (outline) of the piece of paper
        nr = len(contours)
        self.pprint('Drawing {} contour{}'.format(nr, 's' if nr != 1 else ''))

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

    def de_skew_image(
            self, original_image, original_image_ratio, contour,
            binary_bsize=11, binary_offset=10, binary_method='gaussian'
    ):
        # apply the four point transform to obtain a top-down
        # view of the original image
        self.pprint('Applying four point transformation and thresholding')
        image = self.four_point_transform(original_image, contour.reshape(4, 2) * original_image_ratio)
        # image_s = image
        # convert the warped image to grayscale, then threshold it
        # to give it that 'black and white' paper effect
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_local
        # pprint('Thresholding image')
        threshed = threshold_local(image, binary_bsize, offset=binary_offset, method=binary_method)
        image = (image > threshed).astype("uint8") * 255

        if self.debug:
            # show the original and scanned images
            # cv2.imshow("Original", imutils.resize(original_image, height=650))
            # cv2.imshow("De skewed simple", imutils.resize(image_s, height=650))
            # cv2.imshow("De skewed", imutils.resize(image, height=650))
            # cv2.imshow("Warped", imutils.resize(image, height=500))
            pass
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        return image

    def four_point_transform(self, image, pts):
        # order the points
        source = order_points(pts)
        (top_left, top_right, bottom_right, bottom_left) = source

        # compute the width of the new image, which will be the maximum distance between
        # the bottom_right and bottom_left x-coordinates or
        # the top_right and top_left x-coordinates
        width_1 = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
        width_2 = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
        max_width = max(int(width_1), int(width_2))

        # compute the height of the new image, which will be the maximum distance between
        # the top_right and bottom_right y-coordinates or
        # the top_left and bottom_left y-coordinates
        height_1 = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
        height_2 = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))
        max_height = max(int(height_1), int(height_2))

        # construct the destination points
        destination = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype="float32")

        # compute the perspective transform matrix and then apply it
        matrix = cv2.getPerspectiveTransform(source, destination)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))

        return warped

    def pprint(self, message):
        if self.debug:
            now = datetime.now().strftime('%H:%M:%S.%f')
            print(str(now) + ' [ImageManager] ' + str(message))
