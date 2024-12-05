import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_cropper import st_cropper

st.title("Hello, Red and Blue Area Percentage Calculator")

# Upload the image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "tif", "tiff"])

if uploaded_file is not None:
    try:
        # Open the uploaded file as a PIL image
        pil_image = Image.open(uploaded_file)

        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert the PIL image to a NumPy array for processing
        image_rgb = np.array(pil_image)

        # Create cumulative red and blue masks for the entire image
        red_mask_total = np.zeros(image_rgb.shape[:2], dtype=np.uint8)
        blue_mask_total = np.zeros(image_rgb.shape[:2], dtype=np.uint8)

        # Allow the user to set the number of crops
        num_crops = st.number_input("Number of crops", min_value=1, value=1, step=1)

        total_red_area = 0
        total_blue_area = 0
        total_cropped_pixels = 0  # Keep track of all cropped areas

        for i in range(num_crops):
            st.write(f"Crop the image to focus on the area of interest (Crop {i+1}):")
            cropped_image = st_cropper(pil_image, realtime_update=True, box_color="blue", key=f"cropper_{i}")

            # Convert the cropped image back to a NumPy array
            cropped_image_np = np.array(cropped_image)

            # Convert the cropped image to BGR for OpenCV processing
            cropped_image_bgr = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

            # Define the color range for red and blue in BGR format
            lower_red = np.array([0, 0, 90])
            upper_red = np.array([120, 120, 255])
            lower_blue = np.array([90, 0, 0])
            upper_blue = np.array([255, 120, 120])

            # Create masks for red and blue areas
            mask_red = cv2.inRange(cropped_image_bgr, lower_red, upper_red)
            mask_blue = cv2.inRange(cropped_image_bgr, lower_blue, upper_blue)

            # Calculate the area of each color for this crop
            cropped_pixels = cropped_image_bgr.shape[0] * cropped_image_bgr.shape[1]
            red_area = np.sum(mask_red > 0)
            blue_area = np.sum(mask_blue > 0)

            # Update total areas and total cropped pixels
            total_red_area += red_area
            total_blue_area += blue_area
            total_cropped_pixels += cropped_pixels

            # Overlay the red and blue masks onto the total mask
            resized_red_mask = cv2.resize(mask_red, (image_rgb.shape[1], image_rgb.shape[0]), interpolation=cv2.INTER_NEAREST)
            resized_blue_mask = cv2.resize(mask_blue, (image_rgb.shape[1], image_rgb.shape[0]), interpolation=cv2.INTER_NEAREST)

            red_mask_total = cv2.bitwise_or(red_mask_total, resized_red_mask)
            blue_mask_total = cv2.bitwise_or(blue_mask_total, resized_blue_mask)

        # Calculate the overall percentages for red and blue areas across all crops
        overall_red_percentage = (total_red_area / total_cropped_pixels) * 100
        overall_blue_percentage = (total_blue_area / total_cropped_pixels) * 100

        # Display overall results
        st.write(f"Total Red area percentage across all crops: {overall_red_percentage:.2f}%")
        st.write(f"Total Blue area percentage across all crops: {overall_blue_percentage:.2f}%")

        # Visualize the cumulative red and blue masks
        fig, ax = plt.subplots(1, 3, figsize=(15, 5))

        ax[0].imshow(image_rgb)
        ax[0].set_title("Original Image with Crops")
        ax[0].axis('off')

        ax[1].imshow(red_mask_total, cmap='gray')
        ax[1].set_title("Cumulative Red Mask")
        ax[1].axis('off')

        ax[2].imshow(blue_mask_total, cmap='gray')
        ax[2].set_title("Cumulative Blue Mask")
        ax[2].axis('off')

        st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")
