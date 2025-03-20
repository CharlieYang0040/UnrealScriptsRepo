from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from .widgets.image_preview import ImagePreview
from .widgets.converter_panel import ConverterPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texture Converter")
        self.setMinimumSize(800, 600)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # 위젯 추가
        self.image_preview = ImagePreview()
        self.converter_panel = ConverterPanel()
        
        layout.addWidget(self.image_preview)
        layout.addWidget(self.converter_panel)
        
        # 시그널 연결
        self.converter_panel.image_loaded.connect(self.image_preview.update_preview)
        self.converter_panel.conversion_complete.connect(self.image_preview.update_preview)