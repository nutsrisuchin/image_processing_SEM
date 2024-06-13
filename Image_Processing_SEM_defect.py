import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_cropper import st_cropper

st.title("Dark/Black Area Percentage Calculator")

# Upload the image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "tif", "tiff"])

if uploaded_file is not None:
    try:
        # Open the uploaded file as a PIL image
        pil_image = Image.open(uploaded_file)

        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert the PIL image to a NumPy array
        image_rgb = np.array(pil_image)

        # Crop the image using streamlit_cropper
        st.write("Crop the image to focus on the area of interest:")
        cropped_image = st_cropper(pil_image, realtime_update=True)

        # Convert the cropped image back to a NumPy array
        cropped_image_np = np.array(cropped_image)

        # Convert the cropped image to grayscale
        cropped_image_gray = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2GRAY)

        # Define a threshold to consider a pixel as dark/black
        threshold = st.slider("Select threshold for dark area detection", 0, 255, 165)

        # Create a mask for dark/black areas
        mask_dark = cropped_image_gray < threshold

        # Calculate the area of dark/black pixels
        dark_area = np.sum(mask_dark)
        total_pixels = cropped_image_gray.size
        dark_percentage = (dark_area / total_pixels) * 100

        # Display the results
        st.write(f"Dark/Black area percentage: {dark_percentage:.2f}%")

        # Highlight dark areas on the original image
        highlighted_image = cropped_image_np.copy()
        highlighted_image[mask_dark] = [255, 0, 0]  # Highlight dark areas in red

        # Display the cropped image and the mask
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))

        ax[0].imshow(cropped_image_np)
        ax[0].set_title("Cropped Image")
        ax[0].axis('off')

        ax[1].imshow(highlighted_image)
        ax[1].set_title("Highlighted Dark Areas")
        ax[1].axis('off')

        st.pyplot(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")




