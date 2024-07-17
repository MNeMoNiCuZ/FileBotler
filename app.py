import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QLabel, QSplitter, QListWidgetItem, QComboBox
from PyQt5.QtCore import Qt, QDate

class DropLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            print(f"DropLabel: Dropped path {path}")  # Debug print
            try:
                self.parent().parent().parent().handle_dropped_path(path)
            except AttributeError as e:
                print(f"Error: {e}")
                parent = self.parent()
                hierarchy = []
                while parent:
                    hierarchy.append(parent)
                    parent = parent.parent()
                print(f"Parent widget hierarchy: {hierarchy}")

class FileOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Organizer')
        self.setGeometry(100, 100, 1200, 800)  # Larger window size

        # Main layout
        self.main_layout = QVBoxLayout()

        # Top row of buttons
        self.top_row_layout = QHBoxLayout()
        
        # Reset button
        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_list)
        self.top_row_layout.addWidget(self.reset_button)

        # Placeholder drop-down menu
        self.model_selector = QComboBox(self)
        self.model_selector.addItems(['Local LLM', 'Groq API', 'OpenAI API', 'Mistral API'])
        self.top_row_layout.addWidget(self.model_selector)

        self.main_layout.addLayout(self.top_row_layout)

        # Splitter for left and right panels
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left panel
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.splitter.addWidget(self.left_panel)
        
        # Right panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.splitter.addWidget(self.right_panel)
        
        # Drop area
        self.drop_label = DropLabel("Drop files and folders here", self.left_panel)
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("QLabel { border: 2px dashed gray; }")
        self.drop_label.setFixedHeight(100)
        self.left_layout.addWidget(self.drop_label)
        
        # List view for dropped files and folders
        self.list_widget = QListWidget()
        self.left_layout.addWidget(self.list_widget)

        # Filter bar
        self.filter_bar = QLineEdit(self)
        self.filter_bar.setPlaceholderText('Filter files...')
        self.filter_bar.textChanged.connect(self.filter_files)
        self.left_layout.addWidget(self.filter_bar)

        # Prompt input
        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText('Enter your command...')
        self.prompt_input.returnPressed.connect(self.apply_changes)
        self.right_layout.addWidget(self.prompt_input)

        # Preview pane
        self.preview_pane = QTextEdit(self)
        self.preview_pane.setReadOnly(True)
        self.right_layout.addWidget(self.preview_pane)

        # Control buttons
        self.button_layout = QHBoxLayout()
        self.apply_button = QPushButton('Apply', self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.undo_button = QPushButton('Undo', self)
        self.undo_button.clicked.connect(self.undo_changes)
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.refresh_view)
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.undo_button)
        self.button_layout.addWidget(self.refresh_button)
        self.right_layout.addLayout(self.button_layout)

        self.previous_operations = []

        self.main_layout.addWidget(self.splitter)
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def filter_files(self, text):
        fuzzy_search_terms = text.lower().split()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_text = item.text().lower()
            item.setHidden(not all(term in item_text for term in fuzzy_search_terms))

    def apply_changes(self):
        command = self.prompt_input.text()
        # TODO: Integrate with AI model to parse and execute command
        # Example: self.execute_command(command)
        print(f"Applying changes: {command}")  # Debug print
        self.log_operation(command)
        self.preview_pane.append(f"Executed: {command}")

    def undo_changes(self):
        if self.previous_operations:
            last_operation = self.previous_operations.pop()
            # TODO: Undo the last operation
            print(f"Undoing operation: {last_operation}")  # Debug print
            self.preview_pane.append(f"Undid: {last_operation}")
        else:
            self.preview_pane.append("No operations to undo")
            print("No operations to undo")  # Debug print

    def refresh_view(self):
        # This method can be used to refresh the view if needed
        print("Refreshing view")  # Debug print

    def reset_list(self):
        self.list_widget.clear()
        print("List reset")  # Debug print

    def log_operation(self, operation):
        log_filename = f"log_{str(QDate.currentDate().toString('yyyyMMdd'))}.txt"
        logging.basicConfig(filename=log_filename, level=logging.INFO)
        logging.info(operation)
        print(f"Logged operation: {operation}")  # Debug print

    def handle_dropped_path(self, path):
        print(f"Handling dropped path: {path}")  # Debug print
        if not any(self.list_widget.item(i).text() == path for i in range(self.list_widget.count())):
            item = QListWidgetItem(path)
            self.list_widget.addItem(item)
            print(f"Added path: {path}")  # Debug print
        else:
            print(f"Path already exists: {path}")  # Debug print

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileOrganizer()
    ex.show()
    sys.exit(app.exec_())
