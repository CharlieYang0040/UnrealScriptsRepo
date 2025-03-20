from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QSlider, QLabel, QFileDialog, QProgressBar, QComboBox, QFrame)
from PySide6.QtCore import Signal, Qt, QThread
from core.height_to_normal import HeightToNormal

class ConversionThread(QThread):
    finished = Signal(str)
    progress = Signal(int)
    
    def __init__(self, converter, image_path, strength):
        super().__init__()
        self.converter = converter
        self.image_path = image_path
        self.strength = strength
        
    def run(self):
        result = self.converter.convert(self.image_path, self.strength)
        self.finished.emit(result)

class ConverterPanel(QWidget):
    image_loaded = Signal(str)
    conversion_complete = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.current_image_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 구분선 추가 함수
        def add_separator():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("background-color: #555555;")
            layout.addWidget(line)
        
        # 변환 타입 선택
        type_layout = QHBoxLayout()
        type_layout.setContentsMargins(0, 0, 0, 0)
        self.conversion_type = QComboBox()
        self.conversion_type.addItems([
            "Height to Normal",
            "Normal to Height",
            "Diffuse to AO",
            "Roughness Generator"
        ])
        type_layout.addWidget(QLabel("Conversion Type:"))
        type_layout.addWidget(self.conversion_type, stretch=1)
        layout.addLayout(type_layout)
        
        add_separator()
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("Load Image")
        self.convert_btn = QPushButton("Convert")
        self.save_btn = QPushButton("Save")
        
        self.load_btn.clicked.connect(self.load_image)
        self.convert_btn.clicked.connect(self.convert_image)
        self.save_btn.clicked.connect(self.save_image)
        
        self.convert_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.convert_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        add_separator()
        
        # 파라미터 컨트롤
        params_frame = QFrame()
        params_frame.setStyleSheet("QFrame { background-color: #333333; border-radius: 5px; padding: 10px; }")
        params_layout = QVBoxLayout(params_frame)
        
        strength_header = QHBoxLayout()
        strength_header.addWidget(QLabel("Strength Control"))
        
        params_layout.addLayout(strength_header)
        params_layout.addLayout(self.create_slider_layout())
        
        layout.addWidget(params_frame)
        
        # 프로그레스바
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
    def create_slider_layout(self):
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(10, 0, 10, 0)
        
        self.strength_label = QLabel("Strength:")
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(1, 50)
        self.strength_slider.setValue(20)
        self.strength_value = QLabel("2.0")
        self.strength_value.setMinimumWidth(40)
        
        self.strength_slider.valueChanged.connect(self.update_strength_value)
        
        slider_layout.addWidget(self.strength_label)
        slider_layout.addWidget(self.strength_slider)
        slider_layout.addWidget(self.strength_value)
        
        return slider_layout
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Height Map", "",
            "Image Files (*.png *.jpg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.current_image_path = file_path
            self.image_loaded.emit(file_path)
            self.convert_btn.setEnabled(True)

    def convert_image(self):
        if not self.current_image_path:
            return
            
        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        strength = self.strength_slider.value() / 10.0
        converter = HeightToNormal()
        converter.progress_updated.connect(self.update_progress)
        
        self.conversion_thread = ConversionThread(converter, self.current_image_path, strength)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.start()
    
    def conversion_finished(self, result_path):
        self.converted_path = result_path
        self.conversion_complete.emit(result_path)
        self.save_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.progress_bar.setValue(100)
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def save_image(self):
        if not hasattr(self, 'converted_path'):
            return
            
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Normal Map", "",
            "PNG Files (*.png);;All Files (*.*)"
        )
        if save_path:
            if not save_path.lower().endswith('.png'):
                save_path += '.png'
            # 파일 복사
            import shutil
            shutil.copy2(self.converted_path, save_path)

    def update_strength_value(self, value):
        strength = value / 10.0
        self.strength_value.setText(f"{strength:.1f}")