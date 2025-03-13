from PIL import Image
import io
from django.core.files.base import ContentFile
from pathlib import Path

def compress_and_convert_image(image_field, max_size=(800, 800), quality=70):
    """
    Compress image and convert PNG to JPEG
    - Resizes large images
    - Converts PNG to JPEG
    - Compresses JPEG quality
    - Preserves original aspect ratio
    """
    if not image_field:
        return image_field

    # Open image
    img = Image.open(image_field)
    
    # Convert to RGB if PNG
    if img.format == 'PNG':
        img = img.convert('RGB')

    # Calculate new size maintaining aspect ratio
    orig_width, orig_height = img.size
    ratio = min(max_size[0]/orig_width, max_size[1]/orig_height)
    
    if ratio < 1:  # Only resize if image is larger than max_size
        new_size = (int(orig_width * ratio), int(orig_height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Save compressed JPEG
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)

    # Generate filename
    original_name = Path(image_field.name).stem
    new_name = f"{original_name}.jpg"

    # Return compressed image
    return ContentFile(output.read(), name=new_name)

def process_product_image(image_field):
    """
    Process product images with specific settings
    """
    return compress_and_convert_image(
        image_field,
        max_size=(1200, 1200),  # Max dimension for product images
        quality=85  # Higher quality for product images
    )

def process_thumbnail(image_field):
    """
    Process thumbnail images with specific settings
    """
    return compress_and_convert_image(
        image_field,
        max_size=(400, 400),  # Smaller size for thumbnails
        quality=70  # Lower quality acceptable for thumbnails
    )