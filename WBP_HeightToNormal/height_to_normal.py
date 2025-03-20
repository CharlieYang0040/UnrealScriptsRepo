from PIL import Image
import numpy as np

def create_normal_map(height_map_path, output_path, strength=1.0):
    # 높이 맵 로드 및 그레이스케일로 변환
    height_map = Image.open(height_map_path).convert('L')
    width, height = height_map.size
    
    # numpy 배열로 변환
    height_data = np.array(height_map)
    
    # normal map을 저장할 배열 생성 (RGB)
    normal_map = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Sobel 필터를 사용하여 x,y 방향의 기울기 계산
    for y in range(1, height-1):
        for x in range(1, width-1):
            # x 방향 기울기
            dx = (int(height_data[y, x+1]) - int(height_data[y, x-1])) * strength
            # y 방향 기울기
            dy = (int(height_data[y+1, x]) - int(height_data[y-1, x])) * strength
            
            # normal vector 계산
            length = np.sqrt(dx*dx + dy*dy + 1)
            nx = -(dx/length)
            ny = -(dy/length)
            nz = 1.0/length
            
            # normal vector를 RGB로 변환 (범위: 0-255)
            normal_map[y,x] = [
                int((nx + 1.0) * 127.5),
                int((ny + 1.0) * 127.5),
                int((nz + 1.0) * 127.5)
            ]
    
    # 이미지로 변환하여 저장
    normal_image = Image.fromarray(normal_map)
    normal_image.save(output_path)

# 사용 예시
if __name__ == "__main__":
    create_normal_map("height_map.png", "normal_map.png", strength=2.0)