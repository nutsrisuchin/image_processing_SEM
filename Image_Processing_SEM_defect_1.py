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

        # Allow user to set the number of crop boxes
        num_boxes = st.number_input("Number of crop boxes", min_value=1, value=1, step=1)

        total_dark_area = 0
        total_pixels = image_rgb.shape[0] * image_rgb.shape[1]

        for i in range(num_boxes):
            st.write(f"Crop the image to focus on the area of interest (Box {i+1}):")
            cropped_image = st_cropper(pil_image, realtime_update=True, box_color="blue", key=f"cropper_{i}")

            # Convert the cropped image back to a NumPy array
            cropped_image_np = np.array(cropped_image)

            # Convert the cropped image to grayscale
            cropped_image_gray = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2GRAY)

            # Define a threshold to consider a pixel as dark/black
            threshold = st.slider("Select threshold for dark area detection", 0, 255, 165, key=f"threshold_{i}")

            # Create a mask for dark/black areas
            mask_dark = cropped_image_gray < threshold

            # Calculate the area of dark/black pixels
            dark_area = np.sum(mask_dark)
            total_dark_area += dark_area

            # Display the results for the current box
            dark_percentage_box = (dark_area / cropped_image_gray.size) * 100
            st.write(f"Dark/Black area percentage for Box {i+1}: {dark_percentage_box:.2f}%")

            # Highlight dark areas on the original image
            highlighted_image = cropped_image_np.copy()
            highlighted_image[mask_dark] = [255, 0, 0]  # Highlight dark areas in red

            # Display the cropped image and the mask
            fig, ax = plt.subplots(1, 2, figsize=(10, 5))

            ax[0].imshow(cropped_image_np)
            ax[0].set_title(f"Cropped Image (Box {i+1})")
            ax[0].axis('off')

            ax[1].imshow(highlighted_image)
            ax[1].set_title(f"Highlighted Dark Areas (Box {i+1})")
            ax[1].axis('off')

            st.pyplot(fig)

        # Calculate the total dark area percentage relative to the entire image
        total_dark_percentage = (total_dark_area / total_pixels) * 100
        st.write(f"Total Dark/Black area percentage for all boxes: {total_dark_percentage:.2f}%")

    except Exception as e:
        st.error(f"An error occurred: {e}")