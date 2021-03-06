import glob, cv2, numpy as np
from difflib import SequenceMatcher


def text_to_bit_array(text):
    return map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in text]))


def bit_array_to_text(array):
    return "".join(chr(int("".join(map(str, array[i:i + 8])), 2)) for i in range(0, len(array), 8))


def hide_text_in_image(b, text):
    x = len(b)
    y = len(b[0])
    n = 8
    nc = x * y / (n ** 2)
    v1 = 2
    v2 = 3
    u1 = 2
    u2 = 3
    p1 = 127
    p2 = 10
    c1 = 0
    c2 = n
    msg = text_to_bit_array(text[:nc].ljust(nc - len(text)))

    for index in range(0, nc):
        r1 = (n * index) % x
        r2 = r1 + n

        cb = b[r1:r2, c1:c2]

        u, s, v = np.linalg.svd(cb)
        s = np.diag(s)

        w1 = s[u1, v1]
        w2 = s[u2, v2]

        if msg[index] == 0:
            if w1 - w2 != p1:
                w1 = p1 + w2

        if msg[index] == 1:
            if w1 - w2 != p2:
                w1 = p2 + w2

        s[u1, v1] = w1
        s[u2, v2] = w2

        b[r1:r2, c1:c2] = np.dot(u, np.dot(s, v))
        if r2 == x:
            c1 += n
            c2 += n
    return


def extract_text_from_image(b):
    x = len(b)
    y = len(b[0])
    n = 8
    nc = x * y / (n ** 2)
    v1 = 1
    v2 = 2
    u1 = 1
    u2 = 2
    c1 = 0
    c2 = n
    msg = []
    p = 60
    for index in range(0, nc):
        r1 = (n * index) % x
        r2 = r1 + n
        cb = b[r1:r2, c1:c2]
        u, s, v = np.linalg.svd(cb)
        s = np.diag(s)

        w1 = s[u1, v1]
        w2 = s[u2, v2]

        msg.append(0 if abs(w1 - w2) > p else 1)

        if r2 == x:
            c1 += n
            c2 += n

    return bit_array_to_text(msg)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


if __name__ == '__main__':
    for fileName in glob.glob("images/*.tiff"):
        processedFileName = fileName.replace('.tiff', '_processed.tiff').replace('images\\', 'images\\processed\\')

        img = cv2.imread(fileName)
        B, g, r = cv2.split(img)

        message = 'now this shit supports text any length if too much it will be truncated'

        hide_text_in_image(B, message)

        cv2.imwrite(processedFileName, cv2.merge((B, g, r)))

        img1 = cv2.imread(processedFileName)

        result = extract_text_from_image(cv2.split(img1)[0])[:len(message)]

        print '{0:<5}{1:<20}{2:>5.2f}%'.format(len(B), fileName.replace('images\\', ''), similar(message, result) * 100)
