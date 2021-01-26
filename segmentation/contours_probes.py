import cv2
import numpy as np

img = cv2.imread("/home/amaranth/Desktop/contours_test.png",1)
mask = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

contours,hierar = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
print(len(contours))
print(hierar[0,1])
cv2.drawContours(img,contours,1,[0,0,255],3,hierarchy=hierar)
cv2.imshow("drawed",img)
cv2.waitKey(0)
cv2.destroyAllWindows()