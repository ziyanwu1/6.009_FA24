"""
6.101 Lab:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """

    samples = sound["samples"]
    reversed_samples = samples[::-1]
    reversed_sound = {"rate": sound["rate"], "samples": reversed_samples}

    return reversed_sound


def mix(sound1, sound2, p):
    """
    Returns a new sound containing the mix of two different sounds.
    Mixes according to the given mixing paramter.

    Args:
        sound1:  a dictionary representing the first mono sound
        sound2: a dictionary representing the second mono sound

    Returns:
        A new mono sound dictionary with the mixed samples
    """

    # mix 2 good sounds
    if (("rate" not in sound1)
            or ("rate" not in sound2)
            or (sound1["rate"] != sound2["rate"])):
        print("no")
        return None

    r = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    if len(sound1) < len(sound2):
        length = len(sound1)
    elif len(sound2) < len(sound1):
        length = len(sound2)
    elif len(sound1) == len(sound2):
        length = len(sound1)
    else:
        print("whoops")
        return None

    samples = []
    x = 0
    while x <= length:
        s2, s1 = p * sound1[x], sound2[x] * (1 - p)
        samples.append(s1 + s2)  # add sounds
        x += 1
        if x == length:  # end
            break

    return {"rate": r, "samples": samples}  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """

    sample_delay = round(delay * sound['rate'])
    total_sample_delay = sample_delay * num_echoes
    original_samples = sound["samples"]
    original_samples_length = len(original_samples)
    new_total_length = total_sample_delay + original_samples_length
    output = [0 for _ in range(new_total_length)]

    # adds the scaled and shifted versions of the original song to the output
    for i in range(num_echoes+1):
        for j in range(original_samples_length):
            output[i*sample_delay+j] += (original_samples[j] * (scale ** i))

    new_sound = {
        "rate": sound["rate"],
        "samples": output
    }

    return new_sound


def pan(sound):
    """
    Pans a stereo sound from left to right.
    """

    left_samples = sound["left"].copy()
    right_samples = sound["right"].copy()
    sample_length = len(sound["left"])

    # sound goes left to right
    for sample in range(sample_length):
        left_samples[sample] *= (1-(sample/(sample_length-1)))
        right_samples[sample] *= (sample/(sample_length-1))

    new_sound = {
        "rate": sound["rate"],
        "left": left_samples,
        "right": right_samples
    }

    return new_sound


def remove_vocals(sound):
    """
    Removes vocals from a sound.
    """

    left_samples = sound["left"].copy()
    right_samples = sound["right"].copy()
    sample_length = len(sound["left"])
    output = []

    for sample in range(sample_length):
        output.append(left_samples[sample]-right_samples[sample])

    new_sound = {
        "rate": sound["rate"],
        "samples": output
    }

    return new_sound


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    t1 = load_wav("sounds/chord.wav")
    t2 = load_wav("sounds/water.wav")
    t3 = load_wav("sounds/car.wav", stereo=True)
    t4 = load_wav("sounds/lookout_mountain.wav", stereo=True)

    res = remove_vocals(t4)
    write_wav(res, "lookout_mountain_remove_vocals.wav")
