import os
from io import BytesIO

from golem import execution
from golem.browser import get_browser


def save_screenshot(reportdir, image_name, format='PNG', quality=None, width=None,
                    height=None, resize=None):
    """Modify screenshot format, size and quality before saving.
    Pillow must be installed.

    - format must be 'PNG' or 'JPEG'
    - quality must be an int in 1..95 range.
        Default is 75. Only applies to JPEG.
    - width and height must be int greater than 0
    - resize must be an int greater than 0.
        Str in the format '55' or '55%' is also allowed.
    """
    try:
        from PIL import Image
    except ModuleNotFoundError:
        execution.logger.warning('Pillow must be installed in order to modify'
                                 ' screenshot format, size or quality')
        return

    extension = 'png'
    resample_filter = Image.BOX  # for PNG

    # validate format
    if format not in ['JPEG', 'PNG']:
        raise ValueError("settings screenshots format should be 'jpg' or 'png'")
    # validate quality
    if quality is not None:
        try:
            quality = int(quality)
        except ValueError:
            raise ValueError('settings screenshots quality should be int')
        if format == 'JPEG' and not 1 <= quality <= 95:
            raise ValueError('settings screenshots quality should be in 1..95 range for jpg files')
    # validate width
    if width is not None:
        try:
            width = int(width)
        except ValueError:
            raise ValueError('settings screenshots width should be int')
        if width < 0:
            raise ValueError('settings screenshots width should be greater than 0')
    # validate height
    if height is not None:
        try:
            height = int(height)
        except ValueError:
            raise ValueError('settings screenshots height should be int')
        if height < 0:
            raise ValueError('settings screenshots height should be greater than 0')
    # validate resize
    if resize is not None:
        if resize is str:
            resize = resize.replace('%', '')
        try:
            resize = int(resize)
        except ValueError:
            raise ValueError('settings screenshots resize should be int')
        if resize < 0:
            raise ValueError('settings screenshots resize should be greater than 0')

    base_png = get_browser().get_screenshot_as_png()
    pil_image = Image.open(BytesIO(base_png))

    if format == 'JPEG':
        pil_image = pil_image.convert('RGB')
        extension = 'jpg'
        resample_filter = Image.BICUBIC

    if any([width, height, resize]):
        img_width, img_height = pil_image.size
        if width and height:
            new_width = width
            new_height = height
        elif width:
            new_width = width
            # maintain aspect ratio
            new_height = round(new_width * img_height / img_width)
        elif height:
            new_height = height
            # maintain aspect ratio
            new_width = round(new_height * img_width / img_height)
        else:  # resize by %
            new_width = round(pil_image.size[0] * resize / 100)
            new_height = round(pil_image.size[1] * resize / 100)
        pil_image = pil_image.resize((new_width, new_height), resample=resample_filter)

    screenshot_filename = '{}.{}'.format(image_name, extension)
    screenshot_path = os.path.join(reportdir, screenshot_filename)
    if format == 'PNG':
        pil_image.save(screenshot_path, format=format, optimize=True)
    elif format == 'JPEG':
        if quality is None:
            pil_image.save(screenshot_path, format=format, optimize=True)
        else:
            pil_image.save(screenshot_path, format=format, optimize=True,
                           quality=quality)

    return screenshot_filename
