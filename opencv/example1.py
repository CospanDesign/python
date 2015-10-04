#! /usr/bin/python

import numpy as np
import cv2


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    fourcc = cv2.cv.FOURCC("M", "P", "G", "4")
    out = cv2.VideoWriter("/home/cospan/Downloads/indi106.mpg", fourcc, 20.0, (640, 480))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            out.write(frame)

            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break


    cap.release()
    out.release()
    cv2.destroyAllWindows()
