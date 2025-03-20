import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
import os

def main():
    app = QApplication(sys.argv)
    
    # 스타일시트 로드
    style_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'styles', 'style.qss')
    with open(style_path, 'r') as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())