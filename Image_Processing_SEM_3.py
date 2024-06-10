import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image_path = "/content/drive/MyDrive/Image Processing - Researcher/SEM_color/cropped_SEM_color.JPG"
image = cv2.imread(image_path)

# Convert the image to RGB (OpenCV loads images in BGR format by default)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define the color range for red and blue in RGB format
lower_red = np.array([90, 0, 0])
upper_red = np.array([255, 120, 120])
lower_blue = np.array([0, 0, 100])
upper_blue = np.array([100, 100, 255])

# Create masks for red and blue areas
mask_red = cv2.inRange(image_rgb, lower_red, upper_red)
mask_blue = cv2.inRange(image_rgb, lower_blue, upper_blue)

# Calculate the area of each color
total_pixels = image.shape[0] * image.shape[1]
red_area = np.sum(mask_red > 0)
blue_area = np.sum(mask_blue > 0)

# Calculate the percentage of each color area
red_percentage = (red_area / total_pixels) * 100
blue_percentage = (blue_area / total_pixels) * 100

# Print the results
print(f"Red area percentage: {red_percentage:.2f}%")
print(f"Blue area percentage: {blue_percentage:.2f}%")

# Display the original image and the masks
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.title("Original Image")
plt.imshow(image_rgb)
plt.axis('off')

plt.subplot(1, 3, 2)
plt.title("Red Area Mask")
plt.imshow(mask_red, cmap='gray')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.title("Blue Area Mask")
plt.imshow(mask_blue, cmap='gray')
plt.axis('off')

plt.show()
