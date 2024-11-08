import os
import numpy as np
import cv2

class MedianCutQuantizier:
    def __init__(self, input_folder, output_folder, colors = 8):
        """
        Initialize the median cut quantizer.
        """
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.images = []
        self.output_images = []
        self.colors = colors
        self.all_pixels = []
        self.color_palette = []
    
    def _collect_all_pixels(self):
        """
        Collects pixel values from all images and store them in an array.
        """
        all_pixels = []
        # Read all images and collect pixels
        for image_file in os.listdir(self.input_folder):
            # Check for valid image file types
            if image_file.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(self.input_folder, image_file)
                # Read and convert image to RGB color space
                image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
                self.images.append((image, image_file))
                for row in image:
                    for pixel in row:
                        all_pixels.append(pixel)
        self.all_pixels = np.array(all_pixels)
        return
    
    def _quantize_and_update_palette(self, all_pixels):
        """
        Calculate the average color for a group of pixels and add it to the color palette.
        """
        r_average = np.mean(all_pixels[:, 0])
        g_average = np.mean(all_pixels[:, 1])
        b_average = np.mean(all_pixels[:, 2])

        self.color_palette.append([r_average, g_average, b_average])
    
    def _split_into_buckets(self, all_pixels, depth):
        """
        Recursively split pixels into buckets for median cut quantization.
        """
        if len(all_pixels) == 0:
            return
        
        if depth == 0:
            self._quantize_and_update_palette(all_pixels)
            return
        
        # Find the color channel with the highest range variation
        r_range = np.max(all_pixels[:, 0]) - np.min(all_pixels[:, 0])
        g_range = np.max(all_pixels[:, 1]) - np.min(all_pixels[:, 1])
        b_range = np.max(all_pixels[:, 2]) - np.min(all_pixels[:, 2])

        largest_range_channel = np.argmax([r_range, g_range, b_range])

        # Sort pixels by the channel with the highest range and split
        all_pixels = all_pixels[all_pixels[:, largest_range_channel].argsort()]
        median_index = len(all_pixels) // 2

        # Apply the procedure recursively to the found blocks
        self._split_into_buckets(all_pixels[:median_index], depth-1)
        self._split_into_buckets(all_pixels[median_index:], depth-1)
    
    def _apply_quantization(self):
        """
        Quantize each image based on the color palette and store the result.
        """
        for image, image_name in self.images:
            print(image_name)
            quantizied_image = np.zeros_like(image)
            for i, row in enumerate(image):
                for j, pixel in enumerate(row):
                    # Find the closest color in the palette
                    distances = np.sqrt(np.sum((self.color_palette - pixel) ** 2, axis=1 ))
                    nearest_color = self.color_palette[np.argmin(distances)]

                    # Assign the quantizied pixel color to the output image
                    quantizied_image[i, j] = nearest_color
            self.output_images.append((quantizied_image, image_name))

    def median_cut_quantize(self):
        """
        Run the complete median cut quantization process on the database.
        """
        print("Starting quantization...")
        print("Collecting pixels...")
        self._collect_all_pixels()
        print("Collected all pixels")
        print(self.all_pixels.shape)
        print("Generating color palette...")
        self._split_into_buckets(self.all_pixels, self.colors)
        print("Color palette generated")
        print("Applying color quantization to input images...")
        self._apply_quantization()
        print("Color quantization applied")
    
    def save_palette_image(self, row_height=100, image_width=300):
        # Determine the total height of the palette image based on the number of colors
        palette_height = row_height * len(self.color_palette)
        
        # Initialize a blank image for the palette
        palette = np.zeros((palette_height, image_width, 3), dtype=np.uint8)

        # Fill each row with the corresponding color
        for i, color in enumerate(self.color_palette):
            start_y = i * row_height
            end_y = start_y + row_height
            palette[start_y:end_y, :] = color  # Set the color for this row
        output_path = os.path.join(self.output_folder, "qt_palette" + str(self.colors) + ".jpg")
        palette = np.pad(palette, pad_width=((200, 200), (800, 800), (0, 0)), mode='constant', constant_values=255)
        palette = cv2.cvtColor(palette, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, palette)
        
        


    def save_output_images(self):
        """
        Save all quantized images to the specified output folder.
        """
        for image, image_name in self.output_images:
            output_path = os.path.join(self.output_folder, "qt_" + image_name)
            cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            print(f"Saved quantized image to {output_path}")