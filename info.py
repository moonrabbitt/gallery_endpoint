from PIL import Image, ImageDraw, ImageFont
import imageio
import numpy as np

# Define the GIF parameters
width, height = 400, 100
num_frames = 60  # Number of frames for smooth transition
font_size = 24  # Font size for the text

# Create an Image object for each frame
frames = []
for i in range(num_frames):
    # Create a new frame with an animated gradient background using GLSL shader
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        # Animate the gradient colors over time
        r, g, b = int(x * 255 / width), int(i * 255 / num_frames), int((width - x) * 255 / width)
        gradient[:, x] = [r, g, b]

    # Create an Image from the gradient numpy array
    background = Image.fromarray(gradient)

    # Create a drawing context
    draw = ImageDraw.Draw(background)

    # Add text (website and Instagram handle) with a larger font
    font = ImageFont.truetype("arial.ttf", font_size)
    website_text = "avikapulges.com"
    insta_text = "Instagram: avikaaa_p"
    text_color = (255, 255, 255)  # White

    # Calculate text width and height
    website_text_width = draw.textlength(website_text, font=font)
    insta_text_width = draw.textlength(insta_text, font=font)
    text_height = font_size * 2  # Two rows of text

    # Calculate text positions
    x_pos = (width - website_text_width) / 2
    y_pos = (height - text_height) / 2

    # Add some movement to the text (vertical oscillation)
    y_offset = int(5 * np.sin(2 * np.pi * i / num_frames))

    draw.text((x_pos, y_pos + y_offset), website_text, fill=text_color, font=font)
    draw.text((x_pos, y_pos + font_size + y_offset), insta_text, fill=text_color, font=font)

    frames.append(background)

# Save the frames as a GIF
imageio.mimsave("avikapulges.gif", frames, duration=0.1)

print("GIF created successfully.")
