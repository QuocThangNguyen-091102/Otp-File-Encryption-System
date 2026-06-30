from pickle import dumps, loads
from flask import Flask, render_template, request, jsonify
import base64, os, re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Xác định thư mục gốc dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    static_url_path='/static',
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# OTP XOR
def otp_xor(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# AES protect password
def aes_encrypt(password: str, secret: bytes) -> bytes:
    cipher = AES.new(secret, AES.MODE_ECB)
    return cipher.encrypt(pad(password.encode("utf-8"), AES.block_size))

def aes_decrypt(enc_password: bytes, secret: bytes) -> str:
    cipher = AES.new(secret, AES.MODE_ECB)
    return unpad(cipher.decrypt(enc_password), AES.block_size).decode("utf-8")

# Check password strength
def validate_password(password: str) -> bool:
    if len(password) < 6: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[^a-zA-Z0-9]", password): return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

# --- Encrypt endpoint ---
@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        data = request.json
        file_b64 = data['file']
        password = data.get('password', '')
        compress_key = bool(data.get('compress', False))
        out_ext = data.get('outExt', 'bin')

        if not validate_password(password):
            return jsonify({'error': 'Mật khẩu không hợp lệ, vui lòng đặt lại pass theo ràng buộc: >= 6 ký tự, viết hoa, viết thường và ký tự đặt biệt.'}), 400

        file_bytes = base64.b64decode(file_b64)
        original_size = len(file_bytes)

        # Tạo OTP key gốc
        key = os.urandom(original_size)
        key_hex = key.hex()
        log_msg = f"🔑 Key HEX gốc: {len(key_hex)} chars.\n"

        # --- Xử lý nén Huffman ---
        if compress_key:
            from huffman import huffman_compress

            key_bytes_for_compress = key_hex.encode()
            comp_data, codes, padbits = huffman_compress(
                key_bytes_for_compress
            )

            if (
                len(comp_data)
                + len(dumps((codes, padbits)))
                >= len(key_bytes_for_compress)
            ):
                compressed_key_info = b''
                displayed_key = key_hex

                log_msg += (
                    "📦 Đã áp dụng Huffman.\n"
                    "⚠️ Khóa OTP có entropy cao "
                    "nên việc nén không hiệu quả.\n"
                )

            else:
                compressed_key_info = dumps(
                    (codes, padbits)
                )

                displayed_key = (
                    base64
                    .b64encode(comp_data)
                    .decode()
                )

                original_bytes = len(
                    key_bytes_for_compress
                )

                compressed_bytes = len(
                    comp_data
                )

                percent_saved = (
                    100
                    * (
                        original_bytes
                        - compressed_bytes
                    )
                    / original_bytes
                )

                log_msg += (
                    f"📦 Đã áp dụng Huffman.\n"
                    f"📊 Kích thước gốc: "
                    f"{original_bytes} bytes\n"
                    f"📊 Sau nén: "
                    f"{compressed_bytes} bytes\n"
                    f"✅ Giảm "
                    f"{percent_saved:.2f}% "
                    "dung lượng.\n"
                )

        else:
            compressed_key_info = b''
            displayed_key = key_hex

            log_msg += (
                "📦 Không áp dụng Huffman.\n"
            )
        # OTP encrypt
        cipher_data = otp_xor(file_bytes, key)

        # AES bảo vệ password
        SECRET = b'SECRET_16_BYTE__'
        enc_pass = aes_encrypt(password, SECRET)
        log_msg += "🔒 Password đã được bảo vệ AES.\n"

        # Pack layout
        packed = (
            len(enc_pass).to_bytes(2, 'big') + enc_pass +
            len(key).to_bytes(4, 'big') + key +
            len(compressed_key_info).to_bytes(4, 'big') + compressed_key_info +
            cipher_data
        )
        encrypted_data = base64.b64encode(packed).decode()

        return jsonify({
            'encrypted_data': encrypted_data,
            'key_hex': displayed_key,  # key hiển thị cho ô input / tải file
            'enc_pass_hex': enc_pass.hex(),
            'log': log_msg + f"✅ Mã hóa hoàn tất ({original_size} bytes dữ liệu)."
        })

    except Exception as e:
        return jsonify({'error': f'Lỗi mã hóa: {str(e)}'}), 500


# --- Decrypt endpoint ---
@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        data = request.json
        file_b64 = data['file']
        password = data.get('password', '')
        user_key_input = data.get('key_hex', '').strip()  # có thể là base64 nếu nén Huffman
        out_ext = data.get('outExt', 'bin')

        SECRET = b'SECRET_16_BYTE__'

        raw = base64.b64decode(file_b64)
        idx = 0

        enc_len = int.from_bytes(raw[idx:idx+2], 'big'); idx += 2
        enc_pass = raw[idx:idx+enc_len]; idx += enc_len

        key_len = int.from_bytes(raw[idx:idx+4], 'big'); idx += 4
        key_bytes = raw[idx:idx+key_len]; idx += key_len

        info_len = int.from_bytes(raw[idx:idx+4], 'big'); idx += 4
        compressed_key_info = raw[idx:idx+info_len] if info_len > 0 else b''; idx += info_len

        cipher_data = raw[idx:]

        # AES password check
        try:
            dec_pass = aes_decrypt(enc_pass, SECRET)
        except Exception:
            return jsonify({'error': 'Sai mật khẩu gốc, vui lòng nhập lại mật khẩu.'}), 500
        if dec_pass != password:
            return jsonify({'error': 'Sai mật khẩu AES.'}), 403

        # --- Xử lý key nhập ---
        if user_key_input:
            if compressed_key_info:
                # Giải nén Huffman từ base64
                from huffman import huffman_decompress
                comp_bytes = base64.b64decode(user_key_input)
                codes, padbits = loads(compressed_key_info)
                key_hex_str = huffman_decompress(comp_bytes, codes, padbits)
                key = bytes.fromhex(key_hex_str.decode())
            else:
                key = bytes.fromhex(user_key_input)
        else:
            key = key_bytes

        # OTP decrypt
        decrypted_data = otp_xor(cipher_data, key)
        
        # Trả về Base64 để JS xử lý UTF-8-safe
        original_file_b64 = base64.b64encode(decrypted_data).decode()
        
        log_msg = "✅ Key đã xử lý thành công.\n"
        return jsonify({
            'original_file': original_file_b64,
            'log': log_msg + f"✅ Giải mã thành công ({len(decrypted_data)} bytes)."
        })

    except Exception as e:
        return jsonify({'error': f'Lỗi giải mã: {str(e)}'}), 500

@app.route('/clear_log', methods=['POST'])
def clear_log():
    return jsonify({"log": ""})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
