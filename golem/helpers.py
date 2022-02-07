import random
import string


def random_float(min=1.0, max=100.0, decimals=None):
    """Generate a random float between min and max.

    `decimals` is the maximum amount of decimal places
    the generated float should have.
    """
    randomfloat = random.uniform(min, max)
    if decimals is not None:
        randomfloat = round(randomfloat, decimals)
    return randomfloat


def random_int(min=1, max=100):
    """Generate a random integer between min and max"""
    return random.randint(min, max)


def random_str(length=10, sample=None, prefix='', suffix=''):
    """Generate a random string

    Sample should be a string or a list of strings/characters to
    choose from. The default sample is lowercase ascii letters.
    A few presets can be used:
     - 'LOWERCASE': lower case ascii letters
     - 'UPPERCASE': uppercase ascii letters
     - 'DIGITS': digit characters
     - 'SPECIAL': Special characters
    Example:
     random_str(sample=['LOWERCASE', '!@#$%'])

    prefix: A string to be prepended to the generated string

    suffix: A string to be appended to the generated string
    """
    sample_match = {
        'LOWERCASE': string.ascii_lowercase,
        'UPPERCASE': string.ascii_uppercase,
        'DIGITS': string.digits,
        'SPECIAL': string.punctuation
    }

    sample_ = ''
    if sample is None:
        sample_ = string.ascii_lowercase
    else:
        if isinstance(sample, list):
            for s in sample:
                sample_ += sample_match.get(s, str(s))
        elif isinstance(sample, str):
            sample_ += sample_match.get(sample, str(sample))

    random_string = ''.join(random.choice(sample_) for _ in range(length))
    random_string = prefix + random_string + suffix
    return random_string
