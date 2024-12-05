import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_cropper import st_cropper
from fpdf import FPDF
from io import BytesIO

st.title("Fiber Density Percentage Calculation")

# Add Fiber ID input section
fiber_id = st.text_input("Enter Fiber ID (optional)")

# Add Date input section (optional)
date_input = st.date_input("Select Date (optional)", value=None)

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

        # Save the original image to memory
        original_img_byte_arr = BytesIO()
        Image.fromarray(image_rgb).save(original_img_byte_arr, format='PNG')
        original_img_byte_arr.seek(0)

        # Let user set the number of crops
        num_crops = st.number_input("Number of crops", min_value=1, value=1, step=1)

        total_red_area = 0
        total_blue_area = 0
        total_cropped_pixels = 0  # Keep track of all cropped areas

        # Store results for PDF generation
        pdf_content = []
        image_paths = []  # To store the images for each crop

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

            # Store crop results for PDF
            pdf_content.append({
                "crop_number": i+1,
                "red_percentage": red_percentage_crop,
                "blue_percentage": blue_percentage_crop
            })

            # Save the cropped image to memory
            img_byte_arr = BytesIO()
            Image.fromarray(cropped_image_np).save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Store image data for PDF
            image_paths.append(img_byte_arr)

            # Display the cropped image and the masks for this crop
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

        # Result Section for user comments
        st.write("### Result Section")
        user_comments = st.text_area("Enter any additional comments or observations:")

        # Function to generate and download the PDF report
        def generate_pdf(pdf_content, overall_red, overall_blue, user_comments, fiber_id, date_input, image_paths, original_img):
            pdf = FPDF()

            # Add Fiber ID and Date on the first page
            pdf.add_page()
            pdf.set_font("Arial", 'B', size=16)
            pdf.cell(200, 10, txt="Fiber Density Percentage Calculation", ln=True, align='C')

            pdf.set_font("Arial", size=12)
            if fiber_id:
                pdf.cell(200, 10, txt=f"Fiber ID: {fiber_id}", ln=True, align='L')
            if date_input:
                pdf.cell(200, 10, txt=f"Date: {date_input}", ln=True, align='L')

            pdf.ln(10)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Original Image", ln=True, align='C')

            # Add original image on the first page
            pdf.image(original_img, x=10, y=pdf.get_y() + 10, w=190)
            pdf.ln(80)  # Ensure space after image

            # Add one crop per page with details and image
            for idx, content in enumerate(pdf_content):
                pdf.add_page()
                pdf.set_font("Arial", 'B', size=14)
                pdf.cell(200, 10, txt=f"Crop {content['crop_number']}:", ln=True, align='L')

                # Add crop details
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Red area percentage: {content['red_percentage']:.2f}%", ln=True, align='L')
                pdf.cell(200, 10, txt=f"Blue area percentage: {content['blue_percentage']:.2f}%", ln=True, align='L')

                # Add crop image on the same page
                pdf.ln(10)  # Add some spacing before the image
                pdf.image(image_paths[idx], x=10, y=pdf.get_y() + 10, w=120)
                pdf.ln(80)  # Space after image

            # Add final page for Overall Results and User Comments
            pdf.add_page()
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Overall Results", ln=True, align='L')

            # Overall results
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Total Red area percentage: {overall_red:.2f}%", ln=True, align='L')
            pdf.cell(200, 10, txt=f"Total Blue area percentage: {overall_blue:.2f}%", ln=True, align='L')

            pdf.ln(10)  # Add some space before user comments
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="User Comments", ln=True, align='L')
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(200, 10, txt=user_comments)

            # Save the PDF to a BytesIO object in memory
            pdf_output = BytesIO()
            pdf.output(pdf_output)  # Write PDF content into BytesIO object
            pdf_output.seek(0)  # Move pointer to the start of the stream
            return pdf_output

        # Button to download the PDF
        if st.button("Download Report as PDF"):
            pdf_file = generate_pdf(pdf_content, overall_red_percentage, overall_blue_percentage, user_comments, fiber_id, date_input, image_paths, original_img_byte_arr)
            # Generate custom file name
            report_date = date_input.strftime("%Y-%m-%d") if date_input else "unknown"
            report_file_name = f"report-{fiber_id}-{report_date}.pdf" if fiber_id else f"report-{report_date}.pdf"
            # Use the PDF content as bytes for download
            pdf_data = pdf_file.getvalue()  # Extract bytes from the BytesIO object
            st.download_button(label="Download PDF", data=pdf_data, file_name=report_file_name, mime="application/pdf")

    except Exception as e:
        st.error(f"An error occurred: {e}")