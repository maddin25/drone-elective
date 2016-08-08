import cv2

cam = cv2.VideoCapture(0)
running = True
while running:
   running, frame=cam.read()
   if running:
       cv2.imshow('frame',frame)
   if cv2.waitKey(1) & 0xFF == 27:
       running = False
   else:
       print 'error reading video feed'
cam.release()
cv2.destroyAllWindows()