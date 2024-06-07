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

    # Initialize session state variables for input boxes if not existing
    if "lower_red" not in st.session_state:
        st.session_state["lower_red"] = [130, 50, 80]
    if "upper_red" not in st.session_state:
        st.session_state["upper_red"] = [180, 255, 255]
    if "lower_blue" not in st.session_state:
        st.session_state["lower_blue"] = [100, 30, 0]
    if "upper_blue" not in st.session_state:
        st.session_state["upper_blue"] = [170, 255, 255]

    # Helper function to create input boxes with labels, range validation, and unique keys
    def create_rgb_input_boxes(label, default_values, key_prefix=""):  
        col1, col2, col3 = st.columns(3) 
        with col1:
            r = st.number_input(f"{label} Red", min_value=0, max_value=255, value=default_values[0], key=f"{key_prefix}_r")
        with col2:
            g = st.number_input(f"{label} Green", min_value=0, max_value=255, value=default_values[1], key=f"{key_prefix}_g")
        with col3:
            b = st.number_input(f"{label} Blue", min_value=0, max_value=255, value=default_values[2], key=f"{key_prefix}_b")
        return np.array([r, g, b])

    # Get color ranges from user input (input boxes)
    st.subheader("Red Parameters:")
    lower_red = create_rgb_input_boxes("Lower", st.session_state["lower_red"], "lower_red")
    upper_red = create_rgb_input_boxes("Upper", st.session_state["upper_red"], "upper_red")
    st.subheader("Blue Parameters:")
    lower_blue = create_rgb_input_boxes("Lower", st.session_state["lower_blue"], "lower_blue")
    upper_blue = create_rgb_input_boxes("Upper", st.session_state["upper_blue"], "upper_blue")

    # Update session state variables with input box values
    st.session_state["lower_red"] = lower_red
    st.session_state["upper_red"] = upper_red
    st.session_state["lower_blue"] = lower_blue
    st.session_state["upper_blue"] = upper_blue

    # "Run" button
    if st.button("Run"):
        calculator = ColorAreaCalculator()
        # Calculate color areas
        percentage_red, mask_red = calculator.calculate_color_area(img, lower_red, upper_red)
        percentage_blue, mask_blue = calculator.calculate_color_area(img, lower_blue, upper_blue)

        # Display images (masked areas in white)
        masked_img_red = np.zeros_like(img)
        masked_img_red[mask_red > 0] = (255, 255, 255)
        st.image(masked_img_red, caption=f"Red Mask ({percentage_red:.2f}%)", use_column_width=True)

        masked_img_blue = np.zeros_like(img)
        masked_img_blue[mask_blue > 0] = (255, 255, 255)
        st.image(masked_img_blue, caption=f"Blue Mask ({percentage_blue:.2f}%)", use_column_width=True)

