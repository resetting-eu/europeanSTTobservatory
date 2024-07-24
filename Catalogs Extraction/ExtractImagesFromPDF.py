import os
import fitz  # PyMuPDF library
from PIL import Image, ImageOps
from tqdm import tqdm  # tqdm library for progress tracking


def convert_jpx_to_jpeg(jpx_path, jpeg_path):
    with Image.open(jpx_path) as jpx_img:
        # Convert and save as JPG
        jpx_img.save(jpeg_path, 'JPEG')
    os.remove(jpx_path)


def get_pixels_width_height(img_path):
    with Image.open(img_path) as img_open:
        # Get the pixels
        pixels = list(img_open.getdata())

    return pixels


def is_image_almost_black(pixels):
    number_of_pixels = len(pixels)
    black_pixeis = 0
    for pixel in pixels:
        r, g, b = pixel
        if (r + g + b) / 765 < 0.1:
            black_pixeis += 1

    return black_pixeis / number_of_pixels > 0.55


# Extract Images from PDF and returns the directory containing the Images
def extract_images_from_pdf(pdf_path):
    # pdf_name = pdf_path.split("/")[2][:-4]  # Remove ".pdf" extension
    pdf_name = pdf_path[:-4]  # Remove ".pdf" extension

    doc = fitz.Document(pdf_path)  # Open the PDF document

    image_count = 0  # Counter for extracted Images

    for i in range(len(doc)):
        if i != 0: continue  # page number
        for image in doc.get_page_images(i):
            print("IMAGE FOUND!")
            img = doc.extract_image(image[0])
            image_ext = img["ext"]
            image_data = img["image"]
            image_path = f"{pdf_name}_{image_count}.{image_ext}"
            # image_path = os.path.join(pdf_image_dir, f"{pdf_name}_{image_count}.{image_ext}")
            with open(image_path, 'wb') as f:
                f.write(image_data)
            image_count += 1

            if image_ext == "jpx":
                new_img_path = image_path.replace("jpx", "jpg")
                convert_jpx_to_jpeg(image_path, new_img_path)
