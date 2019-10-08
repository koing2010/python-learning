import cv2
import numpy as np

cv2.namedWindow("test") # Create a window
cap = cv2.VideoCapture(0) #Open camera one
success, frame = cap.read() #Read one frame

print("Camera open operation is: ", success);
color = (255,0,0) #Config the color
classfier = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml") #Make sure this xml file is in the same directory with py file
                                                                     #Otherwise change it to absolute directory. This xml file can be found in D:\My Documents\Downloads\opencv\sources\data\haarcascades

while success:
    success, frame = cap.read()
    size = frame.shape[:2] #
    image = np.zeros(size, dtype = np.float16) #
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #
    cv2.equalizeHist(image, image) #
    #Below three lines config the minimal image size
    divisor = 8
    h, w = size
    minSize = ((int)(w/divisor), (int)(h/divisor))
    faceRects = classfier.detectMultiScale(image, 1.2, 2, cv2.CASCADE_SCALE_IMAGE, minSize) #Face detect
    if len(faceRects) > 0:#If face array length > 0
        for faceRect in faceRects: #Draw a rectangle for every face
                xf, yf, wf, hf = faceRect
                x = int((float)(xf))
                y = int((float)(yf))
                w = int((float)(wf))
                h = int((float)(hf))
                cv2.rectangle(frame, (x, y), (x + w, y + h), color)
                cv2.circle(frame, ((int)(x + 1.2 * w / 4), (int)(y + h / 3)), min((int)(w / 8), (int)(h / 8)), (255, 0, 0))
                cv2.circle(frame, ((int)(x + 2.8 * w / 4), (int)(y + h / 3)), min((int)(w / 8), (int)(h / 8)), (255, 0, 0))
                #cv2.rectangle(frame, ((int)(x + 3 * w / 8, (int)(y + 3 * h / 4))), ((int)(x + 5 * w / 8), (int)(y + 7 * h / 8)), (255, 0, 0))
    cv2.imshow("test", frame) #Display image
    key = cv2.waitKey(10)
    c = chr(key & 255)
    if c in ['Q', 'q', chr(27)]:
        break

cv2.destroyWindow("test")
