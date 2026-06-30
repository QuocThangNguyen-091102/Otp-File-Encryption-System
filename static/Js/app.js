
function validatePassword() {
    const password = document.getElementById("password").value;
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{6,}$/;

    if (!regex.test(password)) {
        alert("❌ Mật khẩu phải có ít nhất 6 ký tự, gồm chữ hoa, chữ thường và ký tự đặc biệt!");
        return false; // chặn gửi form
    }
    return true;
}
const modeRadios = document.querySelectorAll('input[name="mode"]');
const encryptInputs = document.getElementById('encryptInputs');
const decryptInputs = document.getElementById('decryptInputs');
const keyHexPre = document.getElementById('keyHex');
const encPassHexPre = document.getElementById('encPassHex');
const logDiv = document.getElementById('log');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');

function log(msg) {
  logDiv.innerText += msg + "\n";
  logDiv.scrollTop = 1e9;
}

function clearLog() {
  logDiv.innerText = '';
}

function base64ToUint8Array(b64) {
  const binStr = atob(b64);
  const len = binStr.length;
  const arr = new Uint8Array(len);
  for (let i=0; i<len; i++) arr[i] = binStr.charCodeAt(i);
  return arr;
}

function downloadBinaryFromBase64(b64, filename) {
  const arr = base64ToUint8Array(b64);
  const blob = new Blob([arr], {type: 'application/octet-stream'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function downloadTextFile(text, filename) {
  const blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function showPreviewIfImage(b64, ext) {
  ext = ext.toLowerCase();
  if (ext === "png" || ext === "jpg" || ext === "jpeg") {
    previewImage.src = `data:image/${ext};base64,${b64}`;
    previewContainer.classList.remove("hidden");
  } else {
    previewContainer.classList.add("hidden");
    previewImage.src = '';
  }
}

function toggleBlur(element) {
  if (element.classList.contains('blurred')) {
    element.classList.remove('blurred');
  } else {
    element.classList.add('blurred');
  }
}

modeRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    clearLog();
    keyHexPre.innerText = '';
    encPassHexPre.innerText = '';
    previewContainer.classList.add('hidden');
    previewImage.src = '';

    if (mode === 'encrypt') {
      encryptInputs.classList.remove('hidden');
      decryptInputs.classList.add('hidden');
      document.getElementById('btnAction').innerText = 'Mã Hóa';
      document.getElementById('outExt').value = 'bin';
    } else {
      encryptInputs.classList.add('hidden');
      decryptInputs.classList.remove('hidden');
      document.getElementById('btnAction').innerText = 'Giải Mã';
      document.getElementById('outExt').value = 'png';
    }
  });
});

// Toggle khóa hex và AES hex mờ/hiện
document.getElementById('toggleKey').addEventListener('click', () => {
  toggleBlur(keyHexPre);
});
document.getElementById('toggleEncPass').addEventListener('click', () => {
  toggleBlur(encPassHexPre);
});

// Xuất file key + log
document.getElementById('btnExport').addEventListener('click', () => {
  const key = keyHexPre.innerText.trim() || '(empty)';
  const encPass = encPassHexPre.innerText.trim() || '(empty)';
  const logText = logDiv.innerText.trim() || '';
  const content = `Key (hex):\n${key}\n\nAES enc_pass (hex):\n${encPass}\n\nLog:\n${logText}\n`;
  downloadTextFile(content, 'key_and_log.txt');
  log('✅ Đã xuất file key_and_log.txt');
});

// Mã hóa
document.getElementById('btnAction').addEventListener('click', async () => {
  const mode = document.querySelector('input[name="mode"]:checked').value;
  if (mode === 'encrypt') {
    const file = document.getElementById('fileInput').files[0];
    const password = document.getElementById('passwordInput').value;
    const compress = document.getElementById('compression').checked;
    const outName = document.getElementById('outName').value || 'result';
    const outExt = document.getElementById('outExt').value || 'bin';

    if (!file) return log("⚠️ Chưa chọn file.");
    if (!password) return log("⚠️ Chưa nhập mật khẩu.");

    const b64 = await readFileAsBase64(file);
    log("🔐 Gửi request mã hóa...");
    try {
      const res = await fetch('/encrypt', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({file: b64, password, compress, outExt})
      });
      const data = await res.json();
      if (data.error) { log("❌ " + data.error); return; }
      if (data.key_hex) keyHexPre.innerText = data.key_hex;
      if (data.enc_pass_hex) encPassHexPre.innerText = data.enc_pass_hex;

      const filename = `${outName}.${outExt}`;
      downloadBinaryFromBase64(data.encrypted_data, filename);

  // 🔹 Hiển thị log chi tiết từ server (có nén/không nén + mã hóa)
      if (data.log) log(data.log);
      log(`✅ Mã hóa xong — file đã tải về (${filename}).`);

    } catch (e) {
      log(`❌ Lỗi: ${e.message}`);
    }
  }
});

// Giải mã
document.getElementById('btnDecrypt').addEventListener('click', async () => {
  const decryptFile = document.getElementById('decryptFileInput').files[0];
  const password = document.getElementById('decryptPasswordInput').value;
  const keyHexText = document.getElementById('decryptKeyHex').value.trim();
  const encPassHexText = document.getElementById('decryptEncPassHex').value.trim();
  const outName = document.getElementById('outName').value || 'result';
  const outExt = document.getElementById('outExt').value || 'bin';

  if (!decryptFile) return log("⚠️ Chưa chọn file mã hóa.");
  if (!keyHexText || !encPassHexText) {
    return log("⚠️ Vui lòng nhập đầy đủ key hex và AES enc_pass hex.");
  }
  if (!password) return log("⚠️ Chưa nhập mật khẩu.");

  // Đọc file mã hóa
  const decryptFileB64 = await readFileAsBase64(decryptFile);

  log("🔓 Gửi request giải mã...");
  try {
    const res = await fetch('/decrypt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        file: decryptFileB64,
        password,
        key_hex: keyHexText,
        enc_pass_hex: encPassHexText,
        outExt
      })
    });
    const data = await res.json();
    if (data.error) {
    log("❌ " + data.error);
    return;
    }
    const filename = `${outName}.${outExt}`;
    downloadBinaryFromBase64(data.original_file, filename);
    if (data.log) log(data.log);
    log(`✅ Giải mã xong — file đã tải về (${filename}).`);
    showPreviewIfImage(data.original_file, outExt);

  } catch (e) {
    log(`❌ Lỗi: ${e.message}`);
  }
});

// Clear cả mã hóa và giải mã
document.getElementById('btnClearDecrypt').addEventListener('click', () => {
  clearLog();
  keyHexPre.innerText = '';
  encPassHexPre.innerText = '';
  previewContainer.classList.add('hidden');
  previewImage.src = '';
  // Xóa luôn input giải mã
  document.getElementById('decryptFileInput').value = '';
  document.getElementById('decryptPasswordInput').value = '';
  document.getElementById('decryptKeyHex').value = '';
  document.getElementById('decryptEncPassHex').value = '';
});
// Clear log trong tab Mã hóa
document.getElementById('btnClear').addEventListener('click', () => {
  clearLog();
  keyHexPre.innerText = '';
  encPassHexPre.innerText = '';
  previewContainer.classList.add('hidden');
  previewImage.src = '';
  // Xóa input mã hóa
  document.getElementById('fileInput').value = '';
  document.getElementById('passwordInput').value = '';
});
// Hàm đọc file base64 (dùng chung)
async function readFileAsBase64(file) {
  const ab = await file.arrayBuffer();
  let binary = '';
  const bytes = new Uint8Array(ab);
  for (let i=0; i<bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}
  const passwordInput = document.getElementById("passwordInput");
const passwordError = document.getElementById("passwordError");

passwordInput.addEventListener("input", () => {
  const password = passwordInput.value;
  const regexLower = /[a-z]/;
  const regexUpper = /[A-Z]/;
  const regexSpecial = /[^a-zA-Z0-9]/;

  if (password.length < 6) {
    passwordError.innerText = "❌ Mật khẩu phải có ít nhất 6 ký tự.";
    passwordError.classList.remove("hidden");
  } else if (!regexLower.test(password)) {
    passwordError.innerText = "❌ Mật khẩu phải chứa ít nhất 1 chữ thường.";
    passwordError.classList.remove("hidden");
  } else if (!regexUpper.test(password)) {
    passwordError.innerText = "❌ Mật khẩu phải chứa ít nhất 1 chữ hoa.";
    passwordError.classList.remove("hidden");
  } else if (!regexSpecial.test(password)) {
    passwordError.innerText = "❌ Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt.";
    passwordError.classList.remove("hidden");
  } else {
    passwordError.classList.add("hidden");
    passwordError.innerText = "";
  }
});

