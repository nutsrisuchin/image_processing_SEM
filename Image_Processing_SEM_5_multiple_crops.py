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

        # Convert the PIL image to a NumPy array
        image_rgb = np.array(pil_image)

        # Let user set the number of crops
        num_crops = st.number_input("Number of crops", min_value=1, value=1, step=1)

        # Variables to hold cumulative red and blue area
        total_red_area = 0
        total_blue_area = 0
        total_cropped_pixels = 0  # Track total number of pixels in all cropped regions

        # Iterate through each crop
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

            # Display the results for this crop
            red_percentage_crop = (red_area / cropped_pixels) * 100
            blue_percentage_crop = (blue_area / cropped_pixels) * 100
            st.write(f"Red area percentage for Crop {i+1}: {red_percentage_crop:.2f}%")
            st.write(f"Blue area percentage for Crop {i+1}: {blue_percentage_crop:.2f}%")

            # Display the cropped image and the masks
            fig, ax = plt.subplots(1, 3, figsize=(15, 5))

            ax[0].imshow(cropped_image_np)
            ax[0].set_title(f"Cropped Image {i+1}")
            ax[0].axis('off')

            ax[1].imshow(mask_red, cmap='gray')
            ax[1].set_title(f"Red Area Mask {i+1}")
            ax[1].axis('off')

            ax[2].imshow(mask_blue, cmap='gray')
            ax[2].set_title(f"Blue Area Mask {i+1}")
            ax[2].axis('off')

            st.pyplot(fig)

        # Calculate the overall percentages for red and blue areas across all crops
        overall_red_percentage = (total_red_area / total_cropped_pixels) * 100
        overall_blue_percentage = (total_blue_area / total_cropped_pixels) * 100

        # Display overall results
        st.write(f"Total Red area percentage across all crops: {overall_red_percentage:.2f}%")
        st.write(f"Total Blue area percentage across all crops: {overall_blue_percentage:.2f}%")

    except Exception as e:
        st.error(f"An error occurred: {e}")

