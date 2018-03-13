#!/usr/bin/env python
# ! -*- coding: utf-8 -*-

import os
import sys
import cv2
import numpy as np
from optparse import OptionParser


class Drawer(object):
    drawing = False
    sx, sy = 0, 0
    gx, gy = 0, 0
    rectangles = []
    folder = './images/'
    tolerable_ratio = 1.5
    max_side = 512
    label = 'label'

    def __init__(self, options):
        if options.ratio is not None:
            self.tolerable_ratio = float(options.ratio)
        if options.max_side is not None:
            self.max_side = int(options.max_side)
        if options.label is not None:
            self.label = options.label

    def draw_rect(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.sx, self.sy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if 0 < x < img.shape[1]:
                self.gx = x
            if 0 < y < img.shape[0]:
                self.gy = y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            w = abs(self.sx - x)
            h = abs(self.sy - y)
            if w < h * self.tolerable_ratio and h < w * self.tolerable_ratio:
                self.rectangles.append([(self.sx, self.sy), (x, y)])

    def read_and_write(self):
        i = 0
        writable_file = open('coordinate.txt', 'w')
        files = os.listdir(self.folder)
        total_count = len(files)
        while i < total_count:
            self.rectangles = []
            scale = 1.0
            while True:
                file = ''.join([self.folder, files[i]])
                img = cv2.imread(file)
                if img is not None:
                    h, w = img.shape[:2]
                    if self.max_side < h or self.max_side < w:
                        # get scaling factor
                        scale = self.max_side / float(h)
                        if self.max_side / float(w) < scale:
                            scale = self.max_side / float(w)
                        # resize image
                        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

                    for r in self.rectangles:
                        cv2.rectangle(img, r[0], r[1], (255, 255, 255), 2)

                    if self.drawing:
                        w = abs(self.sx - self.gx)
                        h = abs(self.sy - self.gy)
                        if w < h * self.tolerable_ratio and h < w * self.tolerable_ratio:
                            color = (0, 255, 0)
                        else:
                            color = (0, 0, 255)
                        cv2.rectangle(img, (self.sx, self.sy), (self.gx, self.gy), color, 2)
                    cv2.imshow('image', img)

                    k = cv2.waitKey(1) & 0xFF
                    if k == ord('d'):
                        if self.rectangles:
                            self.rectangles.pop()
                    elif k == ord('n'):
                        if len(self.rectangles) > 0:
                            for r in self.rectangles:
                                x = min(r[0][0], r[1][0])
                                y = min(r[0][1], r[1][1])
                                w = abs(r[0][0] - r[1][0])
                                h = abs(r[0][1] - r[1][1])

                                if i == 0:
                                    writable_file.write('[')
                                writable_file.write('{')
                                writable_file.write('"%s": {' % file)
                                writable_file.write('"type": "rectangle",')
                                writable_file.write('"label": "%s",' % self.label)
                                writable_file.write('"coordinates": {')
                                writable_file.write('"x": %s,' % round(x / scale, 4))
                                writable_file.write('"y": %s,' % round(y / scale, 4))
                                writable_file.write('"width": %s,' % round(w / scale, 4))
                                writable_file.write('"height": %s' % round(h / scale, 4))
                                writable_file.write('}')
                                writable_file.write('}')
                                writable_file.write('}')
                                if i != total_count - 1:
                                    writable_file.write(',')
                                else:
                                    writable_file.write(']')
                        i += 1
                        break
                    elif k == ord('b'):
                        if i > 1:
                            i -= 2
                            break
                    elif k == ord('q'):
                        writable_file.close()
                        sys.exit()
                else:
                    i += 1


parser = OptionParser()
parser.add_option("-r", "--ratio", dest="ratio", help="Image tolerable ratio")
parser.add_option("-m", "--max_side", dest="max_side", help="Max display size")
parser.add_option("-l", "--label", dest="label", help="Image label name")

(options, args) = parser.parse_args()
drawer = Drawer(options)
img = np.zeros((512, 512, 3), np.uint8)
cv2.namedWindow('image')
cv2.setMouseCallback('image', drawer.draw_rect)
drawer.read_and_write()
