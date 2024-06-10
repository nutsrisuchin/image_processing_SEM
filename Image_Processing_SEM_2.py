import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_cropper import st_cropper

st.title("Red and Blue Area Percentage Calculator")

# Upload the image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Convert the uploaded file to an OpenCV image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Crop the image using streamlit_cropper
    st.write("Crop the image to focus on the area of interest:")
    cropped_image = st_cropper(Image.fromarray(image_rgb), realtime_update=True)

    # Convert the cropped image back to an OpenCV image
    cropped_image_np = np.array(cropped_image)
    cropped_image_rgb = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

    # Define the color range for red and blue in RGB format
    lower_red = np.array([90, 0, 0])
    upper_red = np.array([255, 120, 120])
    lower_blue = np.array([0, 0, 100])
    upper_blue = np.array([100, 100, 255])

    # Create masks for red and blue areas
    mask_red = cv2.inRange(cropped_image_rgb, lower_red, upper_red)
    mask_blue = cv2.inRange(cropped_image_rgb, lower_blue, upper_blue)

    # Calculate the area of each color
    total_pixels = cropped_image_rgb.shape[0] * cropped_image_rgb.shape[1]
    red_area = np.sum(mask_red > 0)
    blue_area = np.sum(mask_blue > 0)

    # Calculate the percentage of each color area
    red_percentage = (red_area / total_pixels) * 100
    blue_percentage = (blue_area / total_pixels) * 100

    # Display the results
    st.write(f"Red area percentage: {red_percentage:.2f}%")
    st.write(f"Blue area percentage: {blue_percentage:.2f}%")

    # Display the original image and the masks
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))

    ax[0].imshow(cv2.cvtColor(cropped_image_rgb, cv2.COLOR_BGR2RGB))
    ax[0].set_title("Cropped Image")
    ax[0].axis('off')

    ax[1].imshow(mask_red, cmap='gray')
    ax[1].set_title("Red Area Mask")
    ax[1].axis('off')

    ax[2].imshow(mask_blue, cmap='gray')
    ax[2].set_title("Blue Area Mask")
    ax[2].axis('off')

    st.pyplot(fig)
