from pathlib import Path

import cv2


def anonimizar_rostros(input_path: str, output_path: str) -> int:
    """Aplica blur a cada rostro detectado y devuelve el total anonimizado."""
    classifier = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
    capture = cv2.VideoCapture(input_path)
    if not capture.isOpened():
        raise ValueError("No fue posible abrir el video")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS) or 25
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    total = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for x, y, face_width, face_height in faces:
            face = frame[y:y + face_height, x:x + face_width]
            frame[y:y + face_height, x:x + face_width] = cv2.GaussianBlur(face, (31, 31), 0)
            total += 1
        writer.write(frame)
    capture.release()
    writer.release()
    return total
