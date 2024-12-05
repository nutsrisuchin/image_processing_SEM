import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_cropper import st_cropper
from fpdf import FPDF
from io import BytesIO

st.title("Dark/Black Area Percentage Calculator")

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

        # Convert the PIL image to a NumPy array
        image_rgb = np.array(pil_image)

        # Save the original image to memory
        original_img_byte_arr = BytesIO()
        pil_image.save(original_img_byte_arr, format='PNG')
        original_img_byte_arr.seek(0)

        # Allow user to set the number of crop boxes
        num_boxes = st.number_input("Number of crop boxes", min_value=1, value=1, step=1)

        total_dark_area = 0
        total_pixels = image_rgb.shape[0] * image_rgb.shape[1]
        
        pdf_content = []  # To store details for each crop for the PDF
        image_paths = []  # To store the original cropped images for each crop
        mask_image_paths = []  # To store the masked images for each crop

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

            # Calculate the percentage of dark area in this crop
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

            # Save crop details for PDF
            pdf_content.append({
                "box_number": i + 1,
                "dark_percentage": dark_percentage_box
            })

            # Save the original cropped image to memory for PDF generation
            image_byte_arr = BytesIO()
            Image.fromarray(cropped_image_np).save(image_byte_arr, format='PNG')
            image_byte_arr.seek(0)
            image_paths.append(image_byte_arr)

            # Save the masked image to memory for PDF generation
            mask_image_byte_arr = BytesIO()
            Image.fromarray(highlighted_image).save(mask_image_byte_arr, format='PNG')
            mask_image_byte_arr.seek(0)
            mask_image_paths.append(mask_image_byte_arr)

        # Calculate the total dark area percentage relative to the entire image
        total_dark_percentage = (total_dark_area / total_pixels) * 100
        st.write(f"Total Dark/Black area percentage for all boxes: {total_dark_percentage:.2f}%")

        # Result Section for user comments
        st.write("### Result Section")
        user_comments = st.text_area("Enter any additional comments or observations:")

        # Function to generate and download the PDF report
        def generate_pdf(pdf_content, total_dark, user_comments, fiber_id, date_input, image_paths, mask_image_paths, original_img):
            pdf = FPDF()

            # Add the title page
            pdf.add_page()
            pdf.set_font("Arial", 'B', size=16)
            pdf.cell(200, 10, txt="Dark/Black Area Percentage Report", ln=True, align='C')

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

            # Add one crop per page with details and images
            for idx, content in enumerate(pdf_content):
                pdf.add_page()
                pdf.set_font("Arial", 'B', size=14)
                pdf.cell(200, 10, txt=f"Box {content['box_number']}:", ln=True, align='L')

                # Add crop details
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Dark area percentage: {content['dark_percentage']:.2f}%", ln=True, align='L')

                # Add cropped image on the page
                pdf.ln(10)  # Add some spacing before the image
                pdf.image(image_paths[idx], x=10, y=pdf.get_y() + 10, w=120)
                pdf.ln(80)  # Space after image

                # Add masked image below the original image
                pdf.image(mask_image_paths[idx], x=10, y=pdf.get_y() + 10, w=120)
                pdf.ln(80)  # Space after masked image

            # Add final page for Overall Results and User Comments
            pdf.add_page()
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Overall Results", ln=True, align='L')

            # Overall results
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Total Dark area percentage: {total_dark:.2f}%", ln=True, align='L')

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
            pdf_file = generate_pdf(pdf_content, total_dark_percentage, user_comments, fiber_id, date_input, image_paths, mask_image_paths, original_img_byte_arr)
            # Generate custom file name
            report_date = date_input.strftime("%Y-%m-%d") if date_input else "unknown"
            report_file_name = f"report-{fiber_id}-{report_date}.pdf" if fiber_id else f"report-{report_date}.pdf"
            # Use the PDF content as bytes for download
            pdf_data = pdf_file.getvalue()  # Extract bytes from the BytesIO object
            st.download_button(label="Download PDF", data=pdf_data, file_name=report_file_name, mime="application/pdf")

    except Exception as e:
        st.error(f"An error occurred: {e}")
