import numpy as np
from PIL import Image
import os
import tempfile
from PySide6.QtCore import QObject, Signal

class HeightToNormal(QObject):
    progress_updated = Signal(int)
    
    def convert(self, image_path: str, strength: float = 2.0) -> str:
        img = Image.open(image_path).convert('L')
        img_array = np.array(img, dtype=np.float32) / 255.0
        
        height, width = img_array.shape
        dx = np.zeros((height, width))
        dy = np.zeros((height, width))
        
        total_pixels = (height - 2) * (width - 2)
        pixels_processed = 0
        
        # Sobel 필터 적용
        x_kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) * strength
        y_kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]) * strength

        for i in range(1, height-1):
            for j in range(1, width-1):
                dx[i, j] = np.sum(img_array[i-1:i+2, j-1:j+2] * x_kernel)
                dy[i, j] = np.sum(img_array[i-1:i+2, j-1:j+2] * y_kernel)
                
                pixels_processed += 1
                if pixels_processed % 1000 == 0:  # 1000픽셀마다 진행률 업데이트
                    progress = int((pixels_processed / total_pixels) * 100)
                    self.progress_updated.emit(progress)

        normal = np.zeros((height, width, 3))
        normal[:,:,0] = dx * 0.5 + 0.5
        normal[:,:,1] = dy * 0.5 + 0.5
        normal[:,:,2] = 1.0
        
        normal = np.clip(normal * 255, 0, 255).astype(np.uint8)
        
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, 'normal_map.png')
        Image.fromarray(normal).save(output_path)
        
        self.progress_updated.emit(100)
        return output_path
