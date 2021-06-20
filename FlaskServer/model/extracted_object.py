# Object that stores extracted data
class ExtractedObject:
    def __init__(self, start, height, width, text, block, par, line, word, confidence):
        self.start = start
        self.height = height
        self.width = width
        self.text = text
        self.block = block
        self.par = par
        self.line = line
        self.word = word
        self.confidence = confidence

    @property
    def end(self):
        return self.right, self.bottom

    @property
    def left(self):
        return self.start[0]

    @property
    def top(self):
        return self.start[1]

    @property
    def right(self):
        return self.start[0] + self.width

    @property
    def bottom(self):
        return self.start[1] + self.height

    def expand_with(self, other):
        if not isinstance(other, ExtractedObject):
            raise TypeError('other should be an ExtractedObject')

        left = min(self.left, other.left)
        top = min(self.top, other.top)
        self.start = (left, top)

        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        self.height = bottom - top
        self.width = right - left

        self.text += ' ' + other.text

    @staticmethod
    def from_tesseract(data):
        start = (data['left'], data['top'])
        height = data['height']
        width = data['width']
        text = str(data['text']).upper()
        block = data['block_num']
        par = data['par_num']
        line = data['line_num']
        word = data['word_num']
        confidence = data['conf']

        return ExtractedObject(start, height, width, text, block, par, line, word, confidence)

    @staticmethod
    def from_google_vision(data, block=-1, par=-1, line=-1, word=-1):
        # vertices = [(l, t), (r, t), (r, b), (l, b)]
        vertices = data.bounding_box.vertices

        y_pad = 0   # works well with 5 (fixes h&m)
        x_pad = 0   # 1

        start = (vertices[0].x - x_pad, vertices[0].y - y_pad)
        height = vertices[3].y - vertices[0].y + y_pad
        width = vertices[1].x - vertices[0].x + x_pad
        confidence = data.confidence

        text = ''.join([s.text for s in data.symbols])

        return ExtractedObject(start, height, width, text, block, par, line, word, confidence)

    def clone(self):
        return ExtractedObject(
            self.start, self.height, self.width, self.text, self.block, self.par, self.line, self.word, self.confidence
        )

    def __str__(self):
        return '{} ({}-{}-{}-{})'.format(self.text, self.block, self.par, self.line, self.word)
        # return '{}-{}-{}'.format(self.block, self.line, self.word)
