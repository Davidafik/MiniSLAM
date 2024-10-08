import cv2
import datetime
from OpenDJI import OpenDJI
import VCS
from MiniSLAM import Mapping
from Calibration import Calibration
import numpy as np
import Utils


####################### Input parameters #######################

PATH_CALIB = "Camera Calibration/CalibMini3Pro/Calibration.npy"
PATH_MAP = 'Testing Images/5/map.npy'

# True if you taking the images with the mini 3 pro.
DRONE_CAM = True

# IP address of the connected android device / cv2 video source.
VIDEO_SOURCE = "10.0.0.4"

# Maximum number of images the program will take.
MAX_IMAGES = 100

# Time to wait between 2 consecutive frame savings (in miliseconds)
WAIT_TIME = 20

SCALE_READ = 0.7

DISPLAY_IMAGE = False

# Scale the image for display:
SCALE_DISPLAY = 0.5

# Mirror the image on display.
MIRROR_DISPLAY = False

# pressing this key will close the program.
QUIT_KEY = 'q'

CONTROL = True

################################################################

def put_text(frame, count):
    font = cv2.FONT_HERSHEY_COMPLEX
    
    text = f"{count} frames read"
    frame = cv2.putText(frame, text, (5, 30), font, 1, (153, 153, 0), 1, cv2.LINE_AA)
    
    text = f"Press '{QUIT_KEY}' to quit"
    return cv2.putText(frame, text, (5, 60), font, 1, (153, 153, 0), 1, cv2.LINE_AA)


calib = Calibration(PATH_CALIB)
mapping = Mapping(calib.getIntrinsicMatrix(), calib.getExtrinsicMatrix(), add_new_pts=False)
mapping.load(PATH_MAP)

# print(f"***removing outliers. \n****num points before: {len(mapping._map3d.pts)}")
# mapping.remove_outliers()
# print(f"****num points after: {len(mapping._map3d.pts)}\n")# mapping.remove_isolated_points(0.05)

# Utils.draw_3d_cloud(mapping._map3d.pts)

if DRONE_CAM:
    cam = OpenDJI(VIDEO_SOURCE)
    if CONTROL:
        take_off = ""
        while take_off != "success":
            take_off = cam.takeoff(True)
            print(take_off)
            cv2.waitKey(300)
        cv2.waitKey(5000)
        print(f"enable: {cam.enableControl(get_result=True)}")
else:
    cam = VCS.VideoCapture(VIDEO_SOURCE)

ts = np.empty((0,3), float)

plot_position = Utils.plot_position()

# Count the number of frames.
count = 0

# Time of the last saved frame.
last_frame = datetime.datetime.now()

while count < MAX_IMAGES and cv2.waitKey(WAIT_TIME) != ord(QUIT_KEY):
    # Get frame from the camera.
    ret, frame = cam.read()

    # If no frame available - skip.
    if not ret:
        print ('Error retriving video stream')
        print(cam.move(0, 0, 0, 0, get_result=True))
        continue

    # Resize frame.
    frame = cv2.resize(frame, dsize = None,
                           fx = SCALE_READ,
                           fy = SCALE_READ)
    
    count += 1
    last_frame = datetime.datetime.now()
    
    print(f"{count}:")
    frame_details = mapping.process_frame(frame)
    # Utils.drawKeyPoints(frame, frame_details.kp)
    
    ascent, roll, pitch = 0, 0, 0
    
    if frame_details is not None:
        R, t = frame_details.R, frame_details.t
        print(f"R{count}: \n{R}\nt{count}: \n{t}\n")
        plot_position.plot_position_heading(R, t)
        
        c = (-R.T @ t) / 20
        ascent, roll, pitch = float(-c[1]), float(-c[0]), float(-c[2])
        pitch = min(0.005, max(-0.005, pitch))
        roll = min(0.005, max(-0.005, roll))
        ascent = min(0.005, max(-0.005, ascent))
        
        ts = np.vstack((ts, t.T))
        
    
    # Send control command.
    if DRONE_CAM and CONTROL:
        print(f'rc {0} {0:.2f} {roll:.2f} {pitch:.2f}')
        print(cam.move(0.,0., roll, pitch, get_result=True))
        # print(cam.move(0, ascent, roll, pitch, get_result=True))
            

    # Display frame.
    if DISPLAY_IMAGE:
        frame = cv2.resize(frame, dsize = None, fx = SCALE_DISPLAY, fy = SCALE_DISPLAY)
        if MIRROR_DISPLAY:
            frame = cv2.flip(frame, 1)
        frame = put_text(frame, count)
        cv2.imshow("frame", frame)
    
# cv2.destroyAllWindows()
print(cam.move(0, 0, 0, 0, get_result=True))
print(cam.disableControl(True))

print("*"*70)
# print(f"3d_pts: \n{mapping._map3d.pts}, \nshape {mapping._map3d.pts.shape}\n")
# print(f"ts: \n{ts}, \nshape {ts.shape}\n")

# Utils.draw_3d_cloud(mapping._map3d.pts, ts)


        