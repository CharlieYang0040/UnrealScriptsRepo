from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage

class ImagePreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 이미지 프리뷰 프레임
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 5px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        # 스크롤 영역 설정
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 이미지 라벨
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(self.image_label)
        
        preview_layout.addWidget(self.scroll_area)
        layout.addWidget(preview_frame)
        
    def update_preview(self, image_path):
        if not image_path:
            return
            
        pixmap = QPixmap(image_path)
        
        # 위젯 크기에 맞게 이미지 크기 조정
        scaled_pixmap = pixmap.scaled(
            self.scroll_area.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)