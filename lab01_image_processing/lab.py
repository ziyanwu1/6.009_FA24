#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col):
    return image["pixels"][image["width"] * row + col]


def set_pixel(image, row, col, color):
    image["pixels"][image["width"] * row + col] = color


def apply_per_pixel(image, func):
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0 for _ in range(image["width"]*image["height"])],
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255-color)


# HELPER FUNCTIONS

def is_in_bounds(width, height, raw_row, raw_col):
    return (raw_row >= 0) and (raw_row < height) and (raw_col >= 0) and (raw_col < width)


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    """
    
    if (boundary_behavior != "zero") and (boundary_behavior != "extend") and (boundary_behavior != "wrap"):
        return None

    kernel_size = kernel["width"]
    offset = kernel_size // 2

    out = {
        "width": image["width"],
        "height": image["height"],
        "pixels": [0 for _ in range(image["width"] * image["height"])]
    }

    for r in range(image["height"]):
        for c in range(image["width"]):
            temp = 0
            for kernel_r in range(kernel_size):
                for kernel_c in range(kernel_size):
                    if is_in_bounds(image["width"], image["height"], r + kernel_r - offset, c + kernel_c - offset):
                        temp += get_pixel(image, r + kernel_r - offset, c + kernel_c - offset) * get_pixel(kernel, kernel_r, kernel_c)
                    else:
                        if boundary_behavior == "zero":
                            continue
                        elif boundary_behavior == "extend":
                            raw_r = r + kernel_r - offset
                            correct_r = max(0, raw_r)
                            correct_r = min(image["height"] - 1, correct_r)

                            raw_c = c + kernel_c - offset
                            correct_c = max(0, raw_c)
                            correct_c = min(image["width"] - 1, correct_c)

                            temp += get_pixel(image, correct_r, correct_c) * get_pixel(kernel, kernel_r, kernel_c)
                        elif boundary_behavior == "wrap":
                            raw_r = r + kernel_r - offset
                            correct_r = raw_r % image["height"]

                            raw_c = c + kernel_c - offset
                            correct_c = raw_c % image["width"]

                            temp += get_pixel(image, correct_r, correct_c) * get_pixel(kernel, kernel_r, kernel_c)

            set_pixel(out, r, c, temp)

    return out



def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    out = {
        "width": image["width"],
        "height": image["height"],
        "pixels": []
    }

    for p in image["pixels"]:
        new_p = round(p)
        if new_p > 255:
            out["pixels"].append(255)
        elif new_p < 0:
            out["pixels"].append(0)
        else:
            out["pixels"].append(new_p)

    return out


# FILTERS

def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.

    kernel = {
        "width": kernel_size,
        "height": kernel_size,
        "pixels": [1/(kernel_size**2) for _ in range(kernel_size**2)]
    }

    return round_and_clip_image(correlate(image, kernel, "extend"))

def sharpened(image, kernel_size):
    out = {
        "width": image["width"],
        "height": image["height"],
        "pixels": []
    }

    blurred_image = blurred(image, kernel_size)

    for i in range(len(image["pixels"])):
        out["pixels"].append(2*image["pixels"][i] - blurred_image["pixels"][i])

    return round_and_clip_image(out)
    

def edges(image):
    k1 = {
        "width": 3,
        "height": 3,
        "pixels": [
            -1, -2, -1,
            0, 0, 0,
            1, 2, 1
        ]
    }

    k2 = {
        "width": 3,
        "height": 3,
        "pixels": [
            -1, 0, 1,
            -2, 0, 2,
            -1, 0, 1
        ]
    }

    out = {
        "width": image["width"],
        "height": image["height"],
        "pixels": []
    }

    k1_correlated = correlate(image, k1, "extend")
    k2_correlated = correlate(image, k2, "extend")

    for i in range(len(image["pixels"])):
        out["pixels"].append(round(math.sqrt(k1_correlated["pixels"][i]**2 + k2_correlated["pixels"][i]**2)))

    return round_and_clip_image(out)

# HELPER FUNCTIONS FOR DISPLAYING, LOADING, AND SAVING IMAGES

def print_greyscale_values(image):
    """
    Given a greyscale image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that pixel values that are floats will be rounded to the nearest int.
    """
    out = f"Greyscale image with {image['height']} rows"
    out += f" and {image['width']} columns:\n "
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        val = str(round(pixel))
        space_vals.append((col, val))
        space_sizes[col] = max(len(val), space_sizes.get(col, 2))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for (col, val) in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"]-1:
            out += "\n "
    print(out)


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    image = load_greyscale_image("test_images/centered_pixel.png")

    print(image)

    kernel_pixels = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]

    kernel = {
        "width": 13,
        "height": 13,
        "pixels": kernel_pixels
    }

    out = correlate(image, kernel, "wrap")

    save_greyscale_image(out, "test_wrap.png")