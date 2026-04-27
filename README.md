


***

# Asymmetric File Encryptor
Application for secure file encryption using asymmetric cryptography.

## Programming Environment

| Element | Selected Technology | Reason for selection |
| :--- | :--- | :--- |
| **Language** | **Python 3.10+** | The team has the most experience in this language; it ensures high code readability. |
| **Interface (GUI)** | **Flet (Flutter for Python)** | Provides a modern look (Material Design 3) and native support for Dark Mode. |
| **Cryptography** | **PyCa/Cryptography** | Industry standard; provides secure implementations of RSA and AES algorithms. |
| **IDE** | **PyCharm** | Excellent support for Python projects, advanced code analysis, and great virtual environment management. |

# Project Structure

```text
.
├── keys/                   # Directory for storing keys (Ignored by git)
│   ├── public/             # Generated public keys
│   └── private/            # Generated private keys
├── src/                    # Main source code of the application
│   ├── main.py             # Entry point script to launch the GUI
[cite_start]│   ├── gui/                # User interface code using Flet
│   │   ├── app.py          # Main application window
│   │   └── components.py   # Reusable UI elements (buttons, inputs)
│   ├── crypto/             # Core cryptographic logic
[cite_start]│   │   ├── asymmetric.py   # Asymmetric algorithms operations
[cite_start]│   │   ├── symmetric.py    # Symmetric algorithms and block modes 
[cite_start]│   │   └── key_manager.py  # Key generation and formatting
│   └── utils/              # Helper functions
[cite_start]│       └── file_handler.py # File I/O and metadata formatting logic
[cite_start]├── tests/                  # Unit tests for encryption and decryption flow 
├── .gitignore              # Files excluded from version control (e.g., keys/)
├── requirements.txt        # Project dependencies (flet, cryptography)
└── README.md               # Project overview and setup instructions
```
