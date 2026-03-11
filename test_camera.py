
# find camera first
# lerobot-find-cameras opencv

import cv2

cap = cv2.VideoCapture("/dev/video0")

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame")
        break

    cv2.imshow("USB Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
