# utils.py (key-free)
import subprocess
import uuid
import platform
import requests
import os
import sys
import time

# API_URL bırakılabilir ama artık key kontrolü istemezsen mock davranış veriyoruz
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")
TIMEOUT = 20

CODES = {
    101: "❌ Key Não Encontrada.",
    102: "🚫 Usuário Banido.",
    103: "🔒 Key Bloqueada.",
    104: "⌛ Key Expirada.",
    105: "⚠️ Formato Da Key Inválido.",
    106: "🚫 Acesso Bloqueado Por Tentativas Excessivas.",
    107: "📄 Fingerprint Incompleta.",
    108: "🔍 Dispositivo Não Corresponde Ao Cadastrado.",
    109: "🚫 Token Inválido.",
    110: "❌ Email Incorreto.",
    111: "❌ Senha Incorreta.",
    500: "💥 Erro Interno No Servidor."
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
        return {"error": "❌ Sistema IOS Detectado, Impossível Utilização."}

    device_id = get_machine_id()
    os_version = get_os_version()
    model = platform.node()
    manufacturer = "Desconhecido"

    if plat == "android":
        model = get_android_prop("ro.product.model")
        manufacturer = get_android_prop("ro.product.manufacturer") or "Desconhecido"
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
        return "❓ Resposta vazia da API."
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
    return f"❓ Erro não mapeado: {data}"


# --- KEY-FREE BEHAVIOR: tüm doğrulamalar bypass edilir ---

def verificar_key_com_fingerprint(chave: str, api_url: str = None):
    """
    Key kontrolü KALDIRILDI: her zaman başarılı döner.
    (Eğer istersen gerçek API'ye gidip doğrulama yapılacak şekilde değiştirebilirsin)
    """
    return {
        "status": "ok",
        "message": "✅ Acesso Permitido (bypassed).",
        "id": "no-0000",
        "key": chave,
        "valid_until": "∞",
        "token": "no-token",
        "raw": {"mock": True}
    }


def login(chave: str, email: str, password: str, token: str, api_url: str = None):
    """
    Login doğrulaması KALDIRILDI: her zaman başarılı döner.
    """
    return {"success": True, "message": "Login bypassed", "user": {"email": email or "no-email", "id": "no-0000"}}


def inject_account(chave: str, token: str, api_url: str = None):
    """
    Inject işlemi mock başarılı dönüş yapar. Eğer gerçek API kullanmak istersen
    api_url verip HTTP isteği yaptırabilirsin.
    """
    # small simulated delay
    time.sleep(0.15)
    return {"status_code": 200, "success": True, "message": "Inject simulated success", "raw": {"mock": True}}
