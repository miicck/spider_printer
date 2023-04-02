from spider_printer.paths.generation.crosshatch import image_to_crosshatch_path
import sys

path = image_to_crosshatch_path(
    sys.argv[1], 
    downsampling=int(input("Downsampling (integer): ")),
    max_hatch=int(input("Maximum hatching (integer): ")),
    rotate90=input("Would you like to rotate the source image by 90 degrees? y/n: ") == "y",
    plot=input("Would you like to see the result now? y/n: ") == "y", 
)
