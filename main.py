import cv2
cap = cv2.VideoCapture(0)

import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

from pynput.mouse import Controller
mouse = Controller()

# from keyboards import QWERTYKeyboard
# keyboard = QWERTYKeyboard.QWERTYKeyboard()

from keyboards import LTNKKeyboard
keyboard = LTNKKeyboard.LTNKKeyboard()

from model import Model as m
model = m.Model()

cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Image", keyboard.on_mouse)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    height, width, _ = image.shape
    
    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    image = keyboard.draw(image)

    if results.multi_face_landmarks:
      for face_landmarks in results.multi_face_landmarks:
        relative_left_x = face_landmarks.landmark[473].x * width
        relative_left_y = face_landmarks.landmark[473].y * height
        relative_right_x = face_landmarks.landmark[468].x * width
        relative_right_y = face_landmarks.landmark[468].y * height

        ave_x = int((relative_left_x + relative_right_x) / 2)
        ave_y = int((relative_left_y + relative_right_y) / 2)

        pred_x, pred_y = model.predict(ave_x, ave_y)

        cv2.circle(image, (int(ave_x), ave_y), 1, (255, 0, 0), 5)

        mouse.position = keyboard.adjust_cursor(int(pred_x // 1.125), int(pred_y // 1.25))

    cv2.imshow("Image", image)

    if cv2.waitKey(5) & 0xFF == 27:
      break

  cv2.destroyAllWindows()

cap.release()