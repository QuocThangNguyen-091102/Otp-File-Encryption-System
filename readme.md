# OTP-Based File Encryption System

A web-based file encryption and decryption application that combines One-Time Pad (OTP), AES password protection, and optional Huffman compression for secure key representation.

## Features

- File encryption and decryption using OTP
- AES-based password protection
- Optional Huffman compression for OTP key representation
- Secure random key generation using `os.urandom()`
- File upload, preview, and download support
- Real-time encryption and decryption logs

## Tech Stack

**Backend**
- Python
- Flask
- PyCryptodome

**Frontend**
- HTML5
- CSS3
- JavaScript
- Tailwind CSS

**Algorithms**
- One-Time Pad (OTP)
- AES
- Huffman Coding

## Project Structure

```text
otp-file-encryption-system/
├── api/
│   └── app.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── huffman.py
├── requirements.txt
├── vercel.json
├── README.md
└── .gitignore
```

## Installation

```bash
git clone https://github.com/your-username/otp-file-encryption-system.git
cd otp-file-encryption-system

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python api/app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Usage

### Encrypt
1. Upload a file.
2. Enter a password.
3. (Optional) Enable Huffman compression.
4. Click Encrypt.
5. Download the encrypted file and save the generated key.

### Decrypt
1. Upload the encrypted file.
2. Enter the password.
3. Provide the OTP key if required.
4. Click Decrypt.
5. Download the restored file.

## Security Notes

- OTP keys are generated using `os.urandom()`.
- Passwords are protected using AES encryption.
- OTP is secure only when keys are truly random, never reused, and kept secret.

## Author

**Nguyễn Quốc Thắng**  
Information Security Student

GitHub: # OTP-Based File Encryption System

A web-based file encryption and decryption application that combines One-Time Pad (OTP), AES password protection, and optional Huffman compression for secure key representation.

## Features

- File encryption and decryption using OTP
- AES-based password protection
- Optional Huffman compression for OTP key representation
- Secure random key generation using `os.urandom()`
- File upload, preview, and download support
- Real-time encryption and decryption logs

## Tech Stack

**Backend**
- Python
- Flask
- PyCryptodome

**Frontend**
- HTML5
- CSS3
- JavaScript
- Tailwind CSS

**Algorithms**
- One-Time Pad (OTP)
- AES
- Huffman Coding

## Project Structure

```text
otp-file-encryption-system/
├── api/
│   └── app.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── huffman.py
├── requirements.txt
├── vercel.json
├── README.md
└── .gitignore
```

## Installation

```bash
git clone https://github.com/your-username/otp-file-encryption-system.git
cd otp-file-encryption-system

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python api/app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Usage

### Encrypt
1. Upload a file.
2. Enter a password.
3. (Optional) Enable Huffman compression.
4. Click Encrypt.
5. Download the encrypted file and save the generated key.

### Decrypt
1. Upload the encrypted file.
2. Enter the password.
3. Provide the OTP key if required.
4. Click Decrypt.
5. Download the restored file.

## Security Notes

- OTP keys are generated using `os.urandom()`.
- Passwords are protected using AES encryption.
- OTP is secure only when keys are truly random, never reused, and kept secret.

## Author

**Nguyễn Quốc Thắng**  
Information Security Student

GitHub: https://github.com/QuocThangNguyen-091102
Vercel: https://one-time-pad.vercel.app/