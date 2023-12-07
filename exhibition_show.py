

def convert_deepface_emotions(deepface_emotion):
    """
    Convert DeepFace emotion to a standard set of emotions.

    Args:
    deepface_emotion (str): The emotion detected by DeepFace.

    Returns:
    str: The corresponding standard emotion.
    """
    emotion_mapping = {
        'angry': 'anger',
        'disgust': 'disgust',
        'fear': 'fear',
        'happy': 'joy',
        'sad': 'sadness',
        'surprise': 'surprise',
        'neutral': 'neutral'
    }

    return emotion_mapping.get(deepface_emotion.lower(), 'neutral')  # Default to 'neutral' if emotion is not recognized

import qrcode
from PIL import Image
from IPython.display import display


def display_qr_code(link, image_path='phone.png', output_path='output.png'):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    # Create an image from the QR Code
    qr_img = qr.make_image(fill_color='black', back_color='white')

    # Open the image file to overlay the QR code on
    base_image = Image.open(image_path)

    # Calculate the position to place the QR code: centered
    qr_size = (base_image.size[0] // 3, base_image.size[1] // 3)  # Set the QR size as a third of the base image size
    qr_img = qr_img.resize(qr_size)
    position = ((base_image.size[0] - qr_size[0]) // 2, (base_image.size[1] - qr_size[1]) // 2)

    # Prepare to draw text
    draw = ImageDraw.Draw(base_image)
    text = "SCAN HERE TO PLAY AND WIN"
    font_size = 20  # Adjust as needed
    font = ImageFont.truetype("arial.ttf", font_size)
    textwidth = draw.textlength(text, font)
    textheight = font_size  # Assuming a single line of text

    # Calculate text position (centered horizontally, above QR code)
    text_x = (base_image.size[0] - textwidth) // 2
    text_y = position[1] - textheight - 10  # 10 pixels above the QR code
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

    # Overlay the QR code onto the image
    base_image.paste(qr_img, position)

    # Save the resulting image
    base_image.save(output_path)


import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import threading
import time
import queue
import cv2
import pyautogui
from deepface import DeepFace
from emotion_responses import responses

class TypingEffectApp:
    def __init__(self, root, message_queue):
        self.root = root
        self.root.title("Artist's Virtual Verbal Verbiage")

        self.canvas_width = 400
        self.canvas_height = 300
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), color=(255, 255, 255))
        self.font = ImageFont.load_default()

        self.draw = ImageDraw.Draw(self.image)

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.message_queue = message_queue
        self.display_text = ""
        self.check_queue()

    def typing_effect(self, new_word, delay=0.1):
        emotion = new_word.split(':')[0]
        print(emotion)
        to_type = self.convert_emotion_to_verbiage(emotion)
        print(to_type)
        for char in to_type:
            time.sleep(delay)
            self.display_text += char  # Append new characters to the existing text
            max_chars_per_line = self.canvas_width // 7
            wrapped_text = self.wrap_text(self.display_text, max_chars_per_line)
            self.update_image(wrapped_text)  # Update display for each character
            self.root.update_idletasks()  # Force update of the Tkinter display

    def convert_emotion_to_verbiage(self, emotion):
        return responses.get(emotion.lower(), "")

    def update_image(self, lines):
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        max_chars_per_line = self.canvas_width // 7
        max_lines_to_display = self.canvas_height // 15  # Number of lines that fit the canvas

        if len(lines) > max_lines_to_display:
            lines_to_display = lines[-max_lines_to_display:]  # Show the latest lines that fit the canvas
        else:
            lines_to_display = lines

        for i, line in enumerate(lines_to_display):
            y_offset = i * 15  # Approximate line height
            self.draw.text((10, y_offset), line, fill="black", font=self.font)

        tk_image = ImageTk.PhotoImage(self.image)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

    def wrap_text(self, text, max_chars_per_line):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + word) <= max_chars_per_line:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines



    def check_queue(self):
        try:
            while not self.message_queue.empty():

                message = self.message_queue.get_nowait()
                self.typing_effect(message,delay=0.1)
                pyautogui.typewrite(message)
                pyautogui.press('enter')
        finally:
            self.root.after(1000, self.check_queue)  # Check the queue every second

def emotion_recognition_from_webcam(message_queue):
    video = cv2.VideoCapture(0)
    last_typed_time = time.time()

    while True:
        ret, frame = video.read()
        if not ret:
            break

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            for face_info in result:
                # Draw bounding boxes and annotations
                x, y, w, h = face_info['region']['x'], face_info['region']['y'], face_info['region']['w'], face_info['region']['h']
                emotions = face_info['emotion']

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                dominant_emotion = max(emotions, key=emotions.get)
                text = f"{dominant_emotion}: {round(emotions[dominant_emotion])}%"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Send message to queue if enough time has passed
                current_time = time.time()
                if current_time - last_typed_time >= 15:
                    message_queue.put(text)
                    last_typed_time = current_time

        except Exception as e:
            print(f"Error: {e}")

        cv2.imshow('Emotion Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    message_queue = queue.Queue()
    app = TypingEffectApp(root, message_queue)

    threading.Thread(target=emotion_recognition_from_webcam, args=(message_queue,), daemon=True).start()
    root.mainloop()
if __name__ == '__main__':
    display_qr_code('https://www.youtube.com/watch?v=n4zJBGjL7cI', 'phone.png')
    main()

