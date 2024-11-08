import argparse
import math
from mc_quantizier import MedianCutQuantizier

parser = argparse.ArgumentParser(description='Perform Median Cut Color Quantization on an image database.')
parser.add_argument('-c', '--colors', type=int,
                    help='Number of colors needed in power of 2, ex: for 16 colors pass 4 because 2^4 = 16')
parser.add_argument('-i', '--input', type=str, help='path of the image folder to be quantized')
parser.add_argument('-o', '--output', type=str, help='output folder to save quantizied images to')

# Get the arguments
args = parser.parse_args()

# Get the values from the arguments
colors = args.colors
print("Reducing the image to {} color palette".format(int(math.pow(2, colors))))

output_folder = args.output
input_folder = args.input

quantizer = MedianCutQuantizier(input_folder=input_folder, output_folder=output_folder, colors=colors)
quantizer.median_cut_quantize()
quantizer.save_palette_image()
quantizer.save_output_images()