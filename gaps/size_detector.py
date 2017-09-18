import cv2
import bisect


class SizeDetector(object):
    """Detects piece size in pixels from given image

    Image is split into RGB single-channel images. Single-channel images are
    combined (R + G, R + B, G + B) in order to cover special edge cases where input
    image have one dominant color commponent.

    For each single channel-image size candidates are found and candidate with most
    occurances is selected.

    :param image: Input puzzle with square pieces.

    Usage::

        >>> import cv2
        >>> from gaps.size_detector import SizeDetector
        >>> image = cv2.imread('puzzle.jpg')
        >>> detector = SizeDetector(image)
        >>> piece_size = detector.detect_piece_size()

    """

    # Max absolute difference between width and height of bounding rectangle
    RECTANGLE_TOLERANCE = 3

    # Contour area / area of contours bounding rectangle
    EXTENT_RATIO = 0.75

    # Piece sizes bounds
    MIN_SIZE = 28
    MAX_SIZE = 64

    # Coefficient for MIN puzzle piece size
    MIN_SIZE_C = 0.9

    # Coefficient for MAX puzzle piece size
    MAX_SIZE_C = 1.3

    def __init__(self, image):
        self._image = image.copy()
        self._possible_sizes = []
        self._calculate_possible_sizes()

    def detect_piece_size(self):
        """Detects piece size in pixels"""

        if len(self._possible_sizes) == 1:
            return self._possible_sizes[0]

        blue, green, red = cv2.split(self._image)

        split_channel_images = [
            red,
            green,
            blue,
            cv2.add(red, green),
            cv2.add(red, blue),
            cv2.add(green, blue)
        ]

        size_candidates = []
        for image in split_channel_images:
            candidates = self._find_size_candidates(image)
            size_candidates.extend(candidates)

        sizes_probability = { size: 0 for size in self._possible_sizes }
        for size_candidate in size_candidates:
            nearest_size = self._find_nearest_size(size_candidate)
            sizes_probability[nearest_size] += 1

        piece_size = max(sizes_probability, key=sizes_probability.get)
        return piece_size

    def _find_size_candidates(self, image):
        binary_image = self._filter_image(image)

        _, contours, _ = cv2.findContours(binary_image,
                                          cv2.RETR_LIST,
                                          cv2.CHAIN_APPROX_SIMPLE)

        size_candidates = []
        for contour in contours:
            bounding_rect = cv2.boundingRect(contour)
            contour_area = cv2.contourArea(contour)
            if self._is_valid_contour(contour_area, bounding_rect):
                candidate = (bounding_rect[2] + bounding_rect[3]) / 2
                size_candidates.append(candidate)

        return size_candidates

    def _is_valid_contour(self, contour_area, bounding_rect):
        _, _, width, height = bounding_rect
        extent = float(contour_area) / (width * height)

        lower_limit = self.MIN_SIZE_C * self._possible_sizes[0]
        upper_limit = self.MAX_SIZE_C * self._possible_sizes[-1]

        is_valid_lower_range = width > lower_limit and height > lower_limit
        is_valid_upper_range = width < upper_limit and height < upper_limit
        is_square = abs(width - height) < self.RECTANGLE_TOLERANCE
        is_extent_valid = extent >= self.EXTENT_RATIO

        return is_valid_lower_range and is_valid_upper_range and is_square and is_extent_valid

    def _find_nearest_size(self, size_candidate):
        index = bisect.bisect_right(self._possible_sizes, size_candidate)

        if index == 0:
            return self._possible_sizes[0]

        if index >= len(self._possible_sizes):
            return self._possible_sizes[-1]

        right_size = self._possible_sizes[index]
        left_size = self._possible_sizes[index - 1]

        if abs(size_candidate - right_size) < abs(size_candidate - left_size):
            return right_size
        else:
            return left_size

    def _calculate_possible_sizes(self):
        """Calculates every possible piece size for given input image"""
        rows, columns, _ = self._image.shape

        for size in range(self.MIN_SIZE, self.MAX_SIZE + 1):
            if rows % size == 0 and columns % size == 0:
                self._possible_sizes.append(size)

    def _filter_image(self, image):
        _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, (5, 5), iterations=3)

        return cv2.bitwise_not(opened)
