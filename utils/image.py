import base64

from utils.http_client import fetch

def get_image(image_url: str):
    image_bytes = fetch(image_url)
    return image_bytes
        
def image_to_data_url(image_bytes: bytes, mime_type="image/jpeg"):
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"