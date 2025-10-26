# utils.py
import subprocess
import uuid
import platform
import requests
import os
import sys
# API URL hâlen aynı, değişmedi
API_URL = os.environ.get("API_URL", "https://elsedev.squareweb.app")
TIMEOUT = 20
# Hata kodları İngilizce + Türkçe açıklamalarla
CODES = {
    101: "❌ Key not found / Anahtar bulunamadı",
    102: "🚫 User banned / Kullanıcı yasaklı",
    103: "🔒 Key locked / Anahtar kilitli",
    104: "⌛ Key expired / Anahtar süresi dolmuş",
    105: "⚠️ Invalid key format / Geçersiz anahtar formatı",
    106: "🚫 Access blocked due to too many attempts / Çok fazla deneme nedeniyle erişim engellendi",
    107: "📄 Incomplete fingerprint / Eksik fingerprint",
    108: "🔍 Device does not match registered one / Cihaz kayıtlı cihazla eşleşmiyor",
    109: "🚫 Invalid token / Geçersiz token",
    110: "❌ Incorrect email / Yanlış email",
    111: "❌ Incorrect password / Yanlış şifre",
    500: "💥 Internal server error / Sunucu hatası"
}
def _run_cmd(cmd: str):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except Exception:
        return None

def get_android_prop(prop):
    return _run_cmd(f"getprop {prop}")

def detect_platform():
    android_model = get_android_prop("ro.product.model")
    if android_model:
        return "android"

    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        if sys.platform == "ios":
            return "ios"
        return "macos"
    return "unknown"

def get_machine_id():
    plat = detect_platform()
    if plat in ["android", "linux", "macos"]:
        try:
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
        except Exception:
            return str(uuid.getnode())
    elif plat == "windows":
        out = _run_cmd("wmic csproduct get uuid")
        if out:
            lines = out.splitlines()
            if len(lines) > 1:
                return lines[1].strip()
        return str(uuid.getnode())
    return str(uuid.getnode())

def get_os_version():
    try:
        return platform.platform()
    except Exception:
        return None

def get_public_ip():
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout=3)
        return resp.json().get("ip")
    except Exception:
        return None

def get_fingerprint():
    plat = detect_platform()

    if plat == "ios":
        return {"error": "❌ IOS system detected, cannot use / IOS sistemi tespit edildi, kullanılamaz."}

    device_id = get_machine_id()
    os_version = get_os_version()
    model = platform.node()
    manufacturer = "Unknown / Bilinmiyor"

    if plat == "android":
        model = get_android_prop("ro.product.model")
        manufacturer = get_android_prop("ro.product.manufacturer") or "Unknown / Bilinmiyor"
    elif plat == "windows":
        manu_out = _run_cmd("wmic computersystem get manufacturer")
        if manu_out:
            lines = manu_out.splitlines()
            if len(lines) > 1:
                manufacturer = lines[1].strip()
    elif plat == "linux":
        sys_vendor_path = "/sys/devices/virtual/dmi/id/sys_vendor"
        if os.path.exists(sys_vendor_path):
            try:
                with open(sys_vendor_path, "r") as f:
                    manufacturer = f.read().strip()
            except Exception:
                pass
    elif plat == "macos":
        manufacturer = "Apple"

    return {
        "device_id": device_id,
        "os_version": os_version,
        "model": model,
        "manufacturer": manufacturer,
    }

def _parse_api_error(data):
    if not data:
        return "❓ Empty API response / Boş API cevabı."
    if isinstance(data, dict) and "detail" in data:
        detail = data["detail"]
        if isinstance(detail, dict):
            code = detail.get("code")
            if code and code in CODES:
                return CODES[code]
            if detail.get("message"):
                return f"❌ {detail.get('message')}"
        elif isinstance(detail, str):
            return f"❌ {detail}"
    if isinstance(data, dict):
        code = data.get("code")
        if code and code in CODES:
            return CODES[code]
        if data.get("message"):
            return f"❌ {data.get('message')}"
    return f"❓ Unmapped error / Haritalanmamış hata: {data}"

def verificar_key_com_fingerprint(chave: str, api_url: str = None):
    api = api_url or API_URL
    fingerprint = get_fingerprint()
    if "error" in fingerprint:
        return {"status": "error", "message": fingerprint["error"]}

    public_ip = get_public_ip()
    headers = {
        "Authorization": chave,
        "Content-Type": "application/json"
    }
    if public_ip:
        headers["X-Forwarded-For"] = public_ip

    try:
        resp = requests.post(f"{api}/key", json=fingerprint, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        return {"status": "error", "message": f"🌐 Connection error / Bağlantı hatası: {e}"}

    try:
        data = resp.json()
    except ValueError:
        return {"status": "error", "message": f"❌ Invalid API response (status {resp.status_code}) / Geçersiz API cevabı."}

    if 200 <= resp.status_code < 300:
        if data.get("success"):
            return {
                "status": "ok",
                "message": "✅ Access granted / Erişim izin verildi.",
                "id": data.get("id"),
                "key": chave,
                "valid_until": data.get("valid_until"),
                "token": data.get("token"),
                "raw": data
            }
        return {"status": "error", "message": _parse_api_error(data), "raw": data}

    return {"status": "error", "message": _parse_api_error(data), "http_status": resp.status_code, "raw": data}

def login(chave: str, email: str, password: str, token: str, api_url: str = None):
    api = api_url or API_URL
    fingerprint = get_fingerprint()
    if "error" in fingerprint:
        return {"status": "error", "message": fingerprint["error"]}

    public_ip = get_public_ip()
    payload = {
        "email": email,
        "password": password,
        "token": token,
        **fingerprint
    }

    headers = {
        "Authorization": chave,
        "Content-Type": "application/json"
    }
    if public_ip:
        headers["X-Forwarded-For"] = public_ip

    try:
        resp = requests.post(f"{api}/login", json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        return {"status": "error", "message": f"🌐 Connection error / Bağlantı hatası: {e}"}

    try:
        data = resp.json()
    except ValueError:
        return {"status": "error", "message": f"❌ Invalid API response (status {resp.status_code}) / Geçersiz API cevabı."}

    if 200 <= resp.status_code < 300:
        return data

    return {"status": "error", "message": _parse_api_error(data), "http_status": resp.status_code, "raw": data}

def inject_account(chave: str, token: str, api_url: str = None):
    api = api_url or API_URL
    fingerprint = get_fingerprint()
    if "error" in fingerprint:
        return {"status": "error", "message": fingerprint["error"]}

    public_ip = get_public_ip()
    payload = {
        "token": token,
        **fingerprint
    }

    headers = {
        "Authorization": chave,
        "Content-Type": "application/json"
    }
    if public_ip:
        headers["X-Forwarded-For"] = public_ip

    try:
        resp = requests.post(f"{api}/inject_account", json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        return {"status": "error", "message": f"🌐 Connection error / Bağlantı hatası: {e}"}

    try:
        data = resp.json()
    except ValueError:
        return {"status": "error", "message": f"❌ Invalid API response (status {resp.status_code}) / Geçersiz API cevabı."}

    if 200 <= resp.status_code < 300:
        return {"status_code": resp.status_code, **data}
    return {"status": "error", "message": _parse_api_error(data), "http_status": resp.status_code, "raw": data}
