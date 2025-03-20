from PIL import Image
import numpy as np

def load_image(path: str) -> np.ndarray:
    """이미지를 로드하고 numpy 배열로 변환"""
    return np.array(Image.open(path))

def save_image(path: str, image: np.ndarray):
    """numpy 배열을 이미지로 저장"""
    Image.fromarray(image).save(path)

def resize_image(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """이미지 크기 조정"""
    img = Image.fromarray(image)
    return np.array(img.resize((width, height), Image.LANCZOS))
