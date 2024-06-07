import streamlit as st
import cv2
import numpy as np

class ColorAreaCalculator:
    def __init__(self):
        pass

    def calculate_color_area(self, image, lower_color, upper_color):
        mask = cv2.inRange(image, lower_color, upper_color) # Directly use image in RGB
        total_pixels = image.size // 3
        color_pixels = np.count_nonzero(mask)
        percentage_color = (color_pixels / total_pixels) * 100
        return percentage_color, mask

    def visualize_color_area(self, image, percentage, mask, color):
        color_img = image.copy()
        color_img[mask == 255] = color
        cv2.putText(
            color_img,
            f"{percentage:.2f}%",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        return color_img

# --- Streamlit App ---
st.title("SEM Color Area Calculator")

# File uploader for image input
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Display original image
    st.image(img, caption="Original Image", use_column_width=True)  

    # Initialize the color ranges
    # --- Red --- 
    lower_red1 = np.array([100, 0, 0])   
    upper_red1 = np.array([255, 100, 100])
    lower_red2 = np.array([150, 0, 0])  
    upper_red2 = np.array([255, 150, 150])    

    # --- Blue ---
    lower_blue = np.array([80, 0, 100])
    upper_blue = np.array([160, 100, 255])

    # "Run" button (No changes here)
    if st.button("Run"):
        calculator = ColorAreaCalculator()

        # Calculate red areas for both ranges and combine masks
        percentage_red1, mask_red1 = calculator.calculate_color_area(img, lower_red1, upper_red1)
        percentage_red2, mask_red2 = calculator.calculate_color_area(img, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        percentage_red = percentage_red1 + percentage_red2  # Total red percentage

        # Calculate blue area
        percentage_blue, mask_blue = calculator.calculate_color_area(img, lower_blue, upper_blue)

        # Display images (masked areas in white)
        masked_img_red = np.zeros_like(img)
        masked_img_red[mask_red > 0] = (255, 255, 255)
        st.image(masked_img_red, caption=f"Red Mask ({percentage_red:.2f}%)", use_column_width=True)

        masked_img_blue = np.zeros_like(img)
        masked_img_blue[mask_blue > 0] = (255, 255, 255)
        st.image(masked_img_blue, caption=f"Blue Mask ({percentage_blue:.2f}%)", use_column_width=True)

