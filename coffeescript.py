#!/usr/bin/env python3.7
"""
# todo
"""

__author__ = "Christian Ost"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import math
from os import path, listdir, makedirs
from PIL import Image


def get_image_files(input_folder, file_endings=None):
    if file_endings is None:
        file_endings = ["JPG"]

    def is_image_file(file_path=""):
        return path.isfile(file_path) and any(
            (file_path.lower().endswith(fe.lower()) for fe in file_endings)
        )

    image_file_list = [
        f for f in listdir(input_folder) if is_image_file(path.join(input_folder, f))
    ]
    # TODO: can be removed when sorting happens in main
    image_file_list.sort()
    return image_file_list


def create_output_folder_if_not_exists(output_folder):
    if not path.exists(output_folder):
        makedirs(output_folder)
    elif not path.isdir(output_folder):
        raise EnvironmentError(
            "a file at the path {0} exists, path cannot be used for the output folder".format(
                output_folder
            )
        )


def get_cropped_image_to_centered_square(input_image):
    height = input_image.height
    width = input_image.width
    is_portrait = height > width

    if is_portrait:
        margin = (height - width) / 2
        box = (0, margin, width, height - margin)
    else:
        margin = (width - height) / 2
        box = (margin, 0, width - margin, height)

    return input_image.crop(box)


def get_next_grid_position(layout, current_grid):
    current_column = current_grid[0]
    current_row = current_grid[1]

    return (
        current_column + 1 if current_column + 1 <= layout[0] else 0,
        current_row + 1 if current_column == layout[0] else current_row,
    )


def calculate_brightness(image):
    # https://gist.github.com/kmohrf/8d4653536aaa88965a69a06b81bcb022
    greyscale_image = image.convert("L")
    histogram = greyscale_image.histogram()
    pixels = sum(histogram)
    img_brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        img_brightness += ratio * (-scale + index)

    return 1 if img_brightness == 255 else img_brightness / scale


def map_path_to_analysed_img(input_folder, img_name, target_size, verbose):
    if verbose:
        print("\tprocessing {0}".format(img_name))
    else:
        print(".", end="", flush=True)

    img = get_cropped_image_to_centered_square(
        Image.open(path.join(input_folder, img_name))
    )
    return {
        "name": img_name,
        "img": img.resize((target_size, target_size)),
        "data": {
            "brightness": calculate_brightness(img),
            "date_time": img.getexif()[36867],
        },
    }


def main(args):
    """ todo """
    if args.verbose:
        print(str(args))

    create_output_folder_if_not_exists(args.output)

    img_size = int(args.size)
    img_margin = int(args.margin)

    print("-> load input images and run basic analysis:")
    input_image_files = list(
        map(
            lambda img_path: map_path_to_analysed_img(
                args.input, img_path, img_size, args.verbose
            ),
            get_image_files(args.input),
        )
    )
    print("\n")

    input_image_files.sort(
        key=lambda img_info: img_info["data"][args.key], reverse=args.reverse
    )

    columns = (
        math.ceil(math.sqrt(len(input_image_files)))
        if args.columns is None
        else int(args.columns)
    )
    rows = math.ceil(len(input_image_files) / columns)
    grid_layout = (columns - 1, rows - 1)

    print("-> create final image")
    if args.verbose:
        print(
            "\tlayout of compilation (columns x rows): {0} x {1}\n".format(
                columns, rows
            )
        )

    final_image_size = (
        int(((img_size + img_margin) * columns) + img_margin),
        int(((img_size + img_margin) * rows) + img_margin),
    )

    grid_position = (0, 0)
    final_image = Image.new("RGB", final_image_size, "#ffffff")
    for img_with_data in input_image_files:
        if args.verbose:
            print("\tprocessing {0}".format(img_with_data["name"]))
        else:
            print(".", end="", flush=True)
        final_image.paste(
            img_with_data["img"],
            (
                int(img_margin + grid_position[0] * (img_size + img_margin)),
                int(img_margin + grid_position[1] * (img_size + img_margin)),
            ),
        )
        grid_position = get_next_grid_position(grid_layout, grid_position)

        if args.thumb:
            img_with_data["img"].save(
                path.join(args.output, img_with_data["name"]), "JPEG"
            )

    print("\n")
    final_image_name = "compilation_{0}x{0}_{1}.jpg".format(img_size, args.key)
    print("-> save compilation image to '{0}'".format(final_image_name))
    final_image.save(path.join(args.output, final_image_name), "JPEG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a collage out of a collection of images."
    )
    parser.add_argument(
        "-i", "--input", default="input", help="the folder with the input images"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="the folder for storing the output images",
    )
    parser.add_argument(
        "--thumb",
        action="store_true",
        help="save thumbnails used for the compilation in output folder",
    )
    parser.add_argument(
        "-k",
        "--key",
        default="date_time",
        help="key to sort the images by, date_time or brightness",
    )
    parser.add_argument("-r", "--reverse", action="store_true", help="reverse sorting")
    parser.add_argument(
        "-c",
        "--columns",
        help="number of columns used for layout, defaults to square layout",
    )
    parser.add_argument(
        "-s", "--size", default=1000, help="width/height for each image in compilation"
    )
    parser.add_argument(
        "-m", "--margin", default=50, help="margin between two images in compilation"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show verbose output"
    )

    main(parser.parse_args())
