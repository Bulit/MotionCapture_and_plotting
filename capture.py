"""
Application for monitoring and recording motion on webcam image.
Every motion are recorded on separate video file.
"""
import warnings
import time
from datetime import datetime
import cv2
import pandas

# Add this line to suppress FutureWarning from pandas about using .append method
warnings.simplefilter(action="ignore", category=FutureWarning)

first_frame = None
status_list = [None, None]
times = []
recording = False
video_nr = 0
df = pandas.DataFrame(columns=["Start", "End"])

# VideoCapture (0 - first camera, 1 for second, 2 for third etc, or u can give path to video file)
# add cv2.CAP_DSHOW to not get warning msg about geting access to camera
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# Next two line is needed to app work on older pc/notebook like my own
# becouse my first camera frame is black app launch camera then wait 3 sec
# and then save frame in while loop
time.sleep(3)
video.read()

while True:
    check, frame = video.read()
    status = 0
    # rotating camera becouse of broken cam in my laptop,
    # if your cam work ok, then delete cv2.ROTATE_180
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:
        first_frame = gray
        continue

    delta_frame = cv2.absdiff(first_frame, gray)
    tresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    # Dilating white area // smoothing treshhold frame //
    # None - Kernel Array used for dilatation // iteration to set how many times
    # we want to get through the img to get rid of black holes on img
    tresh_frame = cv2.dilate(tresh_frame, None, iterations=2)

    # Looking for conturs of dilated treshhold_frame
    (cnts, _) = cv2.findContours(
        tresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in cnts:
        # if the area of contour got less than 10000 pixel go check next
        # change 10000 value depending on object size u want to capture
        if cv2.contourArea(contour) < 10000:
            continue
        status = 1
        # else draw rectangle on that contour
        (x, y, w, h) = cv2.boundingRect(contour)
        # draw that rectangle on our current frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
    status_list.append(status)

    status_list = status_list[-2:]

    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now())
        video_nr += 1
        print("recording")
        videoWriter = cv2.VideoWriter(
            "recorded_" + str(video_nr) + " .avi",
            cv2.VideoWriter_fourcc(*"MJPG"),
            27,
            (640, 480),
        )
        recording = True
    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now())
        videoWriter.release()

    # motion recoding
    if recording:
        videoWriter.write(frame)

    # adding Gray, Delta, Treshold and Color frame for learning purpose only,
    # can delete all except one and it will still work
    cv2.imshow("Gray Frame", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Treshold Frame", tresh_frame)
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)

    if key == ord("q"):
        if status == 1:
            times.append(datetime.now())
        break

print(status_list)
print(times)

for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i + 1]}, ignore_index=True)

df.to_csv("Times.csv")

video.release()
cv2.destroyAllWindows()
