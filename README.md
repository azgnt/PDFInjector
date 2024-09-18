# PDF Injector

PDF Injector is a powerful Python application that allows users to inject malicious URLs, files, and JavaScript code into PDF documents. This tool is intended for educational purposes and should be used responsibly and ethically.

## Features

- **Inject Malicious URLs**: Embed a URL that will open automatically when the PDF is accessed.
- **Inject Files**: Add an embedded file within the PDF, which can be extracted later.
- **Inject JavaScript**: Insert JavaScript payloads to execute various actions when the PDF is opened.
- **User-Friendly GUI**: Built using PyQt5, providing an intuitive interface for easy interaction.

## JavaScript Payloads

The application comes with several predefined JavaScript payloads, including:

- Alert Box
- Denial of Service (DoS)
- Print Dialog
- Open Website
- Download File
- Remote Code Execution (RCE)
- Reverse Shell
- Remote Access
- Keylogger
- Clipboard Data Exfiltration

   ```markdown
   # 📄 PDF Injector

   A Python application to inject URLs, files, and JavaScript into PDF documents using PyPDF4 and PyQt5. 

   ## 🚀 Features
   - Inject URLs into PDFs 🌐
   - Embed files within PDFs 📁
   - Inject JavaScript payloads 💻
   - User-friendly GUI interface 🖥️

   ## ⚙️ Requirements
   - Python 3.x
   - PyPDF4
   - PyQt5

   ## 📦 Installation

   Clone the repository:
   ```bash
   git clone https://github.com/azgnt/PDFInjector.git
   cd PDFInjector
   ```

   Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

   ## 🎉 Usage

   Run the application:
   ```bash
   python pdfinjector.py
   ```

   Select the input PDF, specify the output PDF, and choose your action (inject URL, file, or JavaScript payload). 
   ```
    📝 License
    See the [LICENSE](LICENSE) file for 
   Copyright (c) 2024 Kdairatchi

   Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
   ...
   ```
