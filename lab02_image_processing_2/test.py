#!/usr/bin/env python3

import os
import lab
import types
import pickle
import hashlib
import collections

import pytest


TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()

qx = '\n'  # separator value for long assert statement messages

def compare_greyscale_images(result, expected):
    assert set(result.keys()) == {'height', 'width', 'pixels'}, f'Incorrect keys in dictionary'
    assert result['height'] == expected['height'], 'Heights must match'
    assert result['width'] == expected['width'], 'Widths must match'
    emsg = f"Incorrect number of pixels, expected {result['height']*result['width']}"
    assert len(result['pixels']) == result['height']*result['width'], emsg
    num_incorrect_val = 0
    first_incorrect_val = None
    num_bad_type = 0
    first_bad_type = None

    row, col = 0, 0
    correct_image = True
    for index, (res, exp) in enumerate(zip(result['pixels'], expected['pixels'])):
        emsg = f'{qx}Pixel had value {res} at index {index} (row {row}, col {col}).'
        if not isinstance(res, int):
            correct_image = False
            num_bad_type += 1
            if not first_bad_type:
                first_bad_type = 'Pixels must all be integers!'
                first_bad_type += emsg
        if res != exp:
            correct_image = False
            num_incorrect_val += 1
            if not first_incorrect_val:
                first_incorrect_val = 'Pixels must match'
                first_incorrect_val += f'{qx}Pixel had value {res} but expected {exp} at index {index} (row {row}, col {col}).'

        if col + 1 == result["width"]:
            col = 0
            row += 1
        else:
            col += 1

    msg = "Image is correct!"
    if first_bad_type:
        msg = first_bad_type
        msg += f"{qx}{num_bad_type} pixel{'s'*(num_bad_type>1)} had this problem."
    elif first_incorrect_val:
        msg = first_incorrect_val
        msg += f"{qx}{num_incorrect_val} pixel{'s'*(num_incorrect_val>1)} had incorrect value{'s'*int(num_incorrect_val>1)}."

    assert correct_image, msg

def compare_color_images(result, expected):
    assert set(result.keys()) == {'height', 'width', 'pixels'}, f'Incorrect keys in dictionary'
    assert result['height'] == expected['height'], 'Heights must match'
    assert result['width'] == expected['width'], 'Widths must match'
    emsg = f"Incorrect number of pixels, expected {result['height']*result['width']}"
    assert len(result['pixels']) == result['height']*result['width'], emsg
    num_incorrect_val = 0
    first_incorrect_val = None
    num_bad_type = 0
    first_bad_type = None
    num_bad_range = 0
    first_bad_range = None

    row, col = 0, 0
    correct_image = True
    for index, (res, exp) in enumerate(zip(result['pixels'], expected['pixels'])):
        emsg = f'{qx}Pixel had value {res} at index {index} (row {row}, col {col}).'
        if not isinstance(res, tuple) or len(res) != 3:
            correct_image = False
            num_bad_type += 1
            if not first_bad_type:
                first_bad_type = f'Color pixels must all be length 3 tuples!'
                first_bad_type += emsg
        elif not all(isinstance(pix, int) for pix in res):
            correct_image = False
            num_bad_type += 1
            if not first_bad_type:
                first_bad_type = f'Color pixel tuple values must all be integers!'
                first_bad_type += emsg
        elif any(pix < 0 or pix > 255 for pix in res):
            num_bad_range += 1
            correct_image = False
            if not first_bad_range:
                first_bad_range = f'Color pixel values must all be in the range from [0, 255]!'
                first_bad_range += emsg
        if res != exp:
            correct_image = False
            num_incorrect_val += 1
            if not first_incorrect_val:
                first_incorrect_val = f'Pixels must match'
                first_incorrect_val += f'{qx}Pixel had value {res} but expected {exp}'
                first_incorrect_val += f'{qx} at index {index} (row {row}, col {col}).'

        if col + 1 == result["width"]:
            col = 0
            row += 1
        else:
            col += 1

    msg = "Image is correct!"
    if first_bad_type:
        msg = first_bad_type
        msg += f"{qx}{num_bad_type} pixel{'s'*(num_bad_type>1)} had this problem."
    elif first_bad_range:
        msg = first_bad_range
        msg += f"{qx}{num_bad_range} pixel{'s'*(num_bad_range>1)} had this problem."
    elif first_incorrect_val:
        msg = first_incorrect_val
        msg += f"{qx}{num_incorrect_val} pixel{'s'*(num_incorrect_val>1)} had incorrect value{'s'*int(num_incorrect_val>1)}."

    assert correct_image, msg

def test_load_color():
    result = load_color_image("test_images/centered_pixel.png")
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [(244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (253, 253, 149), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198)]
    }
    compare_color_images(result, expected)


def test_color_filter_inverted():
    im = load_color_image("test_images/centered_pixel.png")
    color_inverted = lab.color_filter_from_greyscale_filter(lab.inverted)
    assert callable(
        color_inverted
    ), "color_filter_from_greyscale_filter should return a function."
    result = color_inverted(im)
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [(11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),  (2, 2, 106), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                   (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57)]
    }
    compare_color_images(result, expected)


def test_color_filter_edges():
    im = load_color_image("test_images/centered_pixel.png")
    color_edges = lab.color_filter_from_greyscale_filter(lab.edges)
    assert callable(
        color_edges
    ), "color_filter_from_greyscale_filter should return a function."
    result = color_edges(im)
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (13, 113, 69), (18, 160, 98), (13, 113, 69), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (18, 160, 98), (0, 0, 0), (18, 160, 98), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (13, 113, 69), (18, 160, 98), (13, 113, 69), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                   (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    }
    compare_color_images(result, expected)


@pytest.mark.parametrize("fname", ["frog", "tree"])
@pytest.mark.parametrize("filter_name", ["edges", "inverted"])
def test_color_filter_images(fname, filter_name):
    filter_ = getattr(lab, filter_name)
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", f"{fname}.png")
    expfile = os.path.join(TEST_DIRECTORY, "test_results", f"{fname}_{filter_name}.png")
    im = load_color_image(inpfile)
    oim = object_hash(im)
    color_filter = lab.color_filter_from_greyscale_filter(filter_)
    assert callable(
        color_filter
    ), "color_filter_from_greyscale_filter should return a function."
    result = color_filter(im)
    expected = load_color_image(expfile)
    assert object_hash(im) == oim, "Be careful not to modify the original image!"
    compare_color_images(result, expected)


def test_blur_filter_small():
    blur_filter = lab.make_blur_filter(3)
    assert callable(blur_filter), "make_blur_filter should return a function."
    color_blur = lab.color_filter_from_greyscale_filter(blur_filter)
    im = load_color_image("test_images/centered_pixel.png")
    result = color_blur(im)
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [(244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (245, 182, 193), (245, 182, 193), (245, 182, 193), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (245, 182, 193), (245, 182, 193), (245, 182, 193), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (245, 182, 193), (245, 182, 193), (245, 182, 193), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                   (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198)]
    }
    compare_color_images(result, expected)


@pytest.mark.parametrize("ker_size", [3, 5])
@pytest.mark.parametrize("fname", ["cat", "mushroom"])
def test_blur_filter_images(fname, ker_size):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", f"{fname}.png")
    expfile = os.path.join(
        TEST_DIRECTORY, "test_results", f"{fname}_blurred{ker_size}.png"
    )
    im = load_color_image(inpfile)
    oim = object_hash(im)
    blur_filter = lab.make_blur_filter(ker_size)
    assert callable(blur_filter), "make_blur_filter should return a function."
    color_blur = lab.color_filter_from_greyscale_filter(blur_filter)
    result = color_blur(im)
    expected = load_color_image(expfile)
    assert object_hash(im) == oim, "Be careful not to modify the original image!"
    compare_color_images(result, expected)


@pytest.mark.parametrize("ker_size", [3, 5])
@pytest.mark.parametrize("fname", ["construct", "bluegill"])
def test_sharpen_filter_images(fname, ker_size):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", f"{fname}.png")
    expfile = os.path.join(
        TEST_DIRECTORY, "test_results", f"{fname}_sharpened{ker_size}.png"
    )
    im = load_color_image(inpfile)
    oim = object_hash(im)
    sharpen_filter = lab.make_sharpen_filter(ker_size)
    assert callable(sharpen_filter), "make_sharpen_filter should return a function."
    color_sharpen = lab.color_filter_from_greyscale_filter(sharpen_filter)
    result = color_sharpen(im)
    expected = load_color_image(expfile)
    assert object_hash(im) == oim, "Be careful not to modify the original image!"
    compare_color_images(result, expected)


def test_small_cascade():
    color_edges = lab.color_filter_from_greyscale_filter(lab.edges)
    color_inverted = lab.color_filter_from_greyscale_filter(lab.inverted)
    color_blur_5 = lab.color_filter_from_greyscale_filter(lab.make_blur_filter(5))

    im = load_color_image("test_images/centered_pixel.png")
    expected = {
        "height": 11,
        "width": 11,
        "pixels": [(255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (254, 250, 252), (254, 244, 248), (253, 240, 246), (253, 240, 246), (253, 240, 246), (254, 244, 248), (254, 250, 252), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (254, 244, 248), (253, 238, 244), (252, 227, 238), (252, 227, 238), (252, 227, 238), (253, 238, 244), (254, 244, 248), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (253, 240, 246), (252, 227, 238), (250, 211, 228), (250, 211, 228), (250, 211, 228), (252, 227, 238), (253, 240, 246), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (253, 240, 246), (252, 227, 238), (250, 211, 228), (250, 211, 228), (250, 211, 228), (252, 227, 238), (253, 240, 246), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (253, 240, 246), (252, 227, 238), (250, 211, 228), (250, 211, 228), (250, 211, 228), (252, 227, 238), (253, 240, 246), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (254, 244, 248), (253, 238, 244), (252, 227, 238), (252, 227, 238), (252, 227, 238), (253, 238, 244), (254, 244, 248), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (254, 250, 252), (254, 244, 248), (253, 240, 246), (253, 240, 246), (253, 240, 246), (254, 244, 248), (254, 250, 252), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                   (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)]
    }
    f_cascade = lab.filter_cascade([color_edges, color_inverted, color_blur_5])
    assert callable(f_cascade), "filter_cascade should return a function."
    result = f_cascade(im)
    compare_color_images(result, expected)


@pytest.mark.parametrize("cascade", [0, 1, 2])
@pytest.mark.parametrize("image", ["tree", "stronger"])
def test_cascades(cascade, image):
    color_edges = lab.color_filter_from_greyscale_filter(lab.edges)
    color_inverted = lab.color_filter_from_greyscale_filter(lab.inverted)
    cascade0 = [
        color_edges,
        lab.color_filter_from_greyscale_filter(lab.make_sharpen_filter(3)),
    ]
    cascade1 = [
        lab.color_filter_from_greyscale_filter(lab.make_blur_filter(5)),
        color_edges,
        lab.color_filter_from_greyscale_filter(lab.make_sharpen_filter(3)),
        lambda im: {
            k: ([(i[1], i[0], i[2]) for i in v] if isinstance(v, list) else v)
            for k, v in im.items()
        },
    ]
    cascade2 = [color_edges] * 5 + [color_inverted]

    cascades = [cascade0, cascade1, cascade2]

    inpfile = os.path.join(TEST_DIRECTORY, "test_images", f"{image}.png")
    expfile = os.path.join(
        TEST_DIRECTORY, "test_results", f"{image}_cascade{cascade}.png"
    )
    im = load_color_image(inpfile)
    oim = object_hash(im)
    f_cascade = lab.filter_cascade(cascades[cascade])
    assert callable(f_cascade), "filter_cascade should return a function."
    result = f_cascade(im)
    expected = load_color_image(expfile)
    assert object_hash(im) == oim, "Be careful not to modify the original image!"
    compare_color_images(result, expected)


def seams_endtoend(inp_name, out_name, number):
    inpfile = os.path.join(TEST_DIRECTORY, "test_images", inp_name)

    im = load_color_image(inpfile)
    oim = object_hash(im)
    for i in range(1, number):
        result = lab.seam_carving(im, i)
        assert object_hash(im) == oim, "Be careful not to modify the original image!"

        expfile = os.path.join(TEST_DIRECTORY, "test_results", out_name, f"{i:02d}.png")
        compare_color_images(result, load_color_image(expfile))


def seams_one(images):
    for i in images:
        inpfile = os.path.join(TEST_DIRECTORY, "test_images", f"{i}.png")
        im = load_color_image(inpfile)

        oim = object_hash(im)
        result = lab.seam_carving(im, 1)
        assert object_hash(im) == oim, "Be careful not to modify the original image!"

        expfile = os.path.join(TEST_DIRECTORY, "test_results", f"{i}_1seam.png")
        compare_color_images(result, load_color_image(expfile))


def test_seamcarving_images_1():
    seams_one(("pattern", "smallfrog"))


def test_seamcarving_images_2():
    seams_one(("bluegill", "tree", "twocats"))


def test_seamcarving_centeredpixel():
    seams_endtoend("centered_pixel.png", "seams_centered_pixel", 11)


def test_seamcarving_pattern():
    seams_endtoend("pattern.png", "seams_pattern", 9)


def test_seamcarving_smallfrog():
    seams_endtoend("smallfrog.png", "seams_smallfrog", 31)


def test_seamcarving_mushroom():
    seams_endtoend("smallmushroom.png", "seams_mushroom", 47)

def test_presence_of_custom_feature():
    assert hasattr(lab, 'custom_feature'), "Custom feature code is not present!"
    assert callable(lab.custom_feature), "custom_feature should be a function"

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    from PIL import Image

    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError("Unsupported image mode: %r" % img.mode)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    from PIL import Image
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}
