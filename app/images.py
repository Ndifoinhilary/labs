import os

from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)


URL_ENDPOINT = os.environ.get("IMAGEKIT_URL_ENDPOINT")
