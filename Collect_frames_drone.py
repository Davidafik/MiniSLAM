import cv2
import datetime
from os import mkdir, path
from OpenDJI import OpenDJI
import VCS
import Utils


####################### Input parameters #######################

# True if you taking the images with the mini 3 pro.
DRONE_CAM = True

# IP address of the connected android device
# VIDEO_SOURCE = "192.168.137.94"
VIDEO_SOURCE = "10.0.0.3"

# Save folder
SAVE_PATH = 'Testing Images/3'

# Maximum number of images the program will take.
MAX_IMAGES = 1000

# Time to wait between 2 consecutive frame savings (in miliseconds)
WAIT_TIME = 300

# Scale the image (for display only):
SCALE_FACTOR = 0.5

# Mirror the image on display.
MIRROR_DISPLAY = False

# pressing this key will close the program.
QUIT_KEY = 'q'

################################################################


# Create the folder if it does not exist.
if not path.isdir(SAVE_PATH):
    mkdir(SAVE_PATH)

if DRONE_CAM:
    cam = OpenDJI(VIDEO_SOURCE)
else:
    cam = VCS.VideoCapture(VIDEO_SOURCE)


# Count the number of frames.
count = 0

cv2.waitKey(3000)

# Time of the last saved frame.
last_saved_frame = datetime.datetime.now()

# Press QUIT_KEY to close the program.
while count < MAX_IMAGES and cv2.waitKey(20) != ord(QUIT_KEY):
    # Get frame from the camera.
    ret, frame = cam.read()

    # What to do when no frame available.
    if not ret:
        print ('Error retriving video stream')
        continue
    
    # Save frame to folder every WAIT_TIME ms.
    if last_saved_frame + datetime.timedelta(milliseconds=WAIT_TIME) < datetime.datetime.now():
        count += 1
        last_saved_frame = datetime.datetime.now()
        
        # Save frame to folder. 
        save_to = f"{SAVE_PATH}/image{count:04}.jpg"
        cv2.imwrite(save_to, frame)
        print (f"{count} saved - {save_to}")

        # Change the frame's brightness to indicate with a flase to the user that a frame was saved.
        frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=50)
            
    # Display frame.
    frame = cv2.resize(frame, dsize = None, fx = SCALE_FACTOR, fy = SCALE_FACTOR)
    if MIRROR_DISPLAY:
        frame = cv2.flip(frame, 1)
    frame = Utils.put_text(frame, count)
    cv2.imshow("frame", frame)
    
cv2.destroyAllWindows()
print(f"Collection ended. {count} images saved.")
      