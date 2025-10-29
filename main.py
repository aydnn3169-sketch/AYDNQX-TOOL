# main.py (key-free)
import os
import time
from colorama import init, Fore, Style
from utils import (
    verificar_key_com_fingerprint, login, API_URL, inject_account
)

init(autoreset=True)

VERSION = "1.0.0"
DEV_LINK = "https://t.me/Cpm_traderbot"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def header():
    print(Fore.CYAN + "=" * 59)
    print(Fore.WHITE + f"• Car Parking Multiplayer 2 - Version: {VERSION} || Dev: {DEV_LINK}")
    print(Fore.CYAN + "=" * 59)

def print_title_inside_line(title, width=59):
    title_str = f"[ {title} ]"
    total_len = width
    side_len = max(0, (total_len - len(title_str) - 2) // 2)

    left = Fore.CYAN + ("=" * side_len) + " "

    center = Fore.CYAN + "[" + Fore.WHITE + f" {title} " + Fore.CYAN + "]"

    base_len = side_len + 1 + len(title_str) + 1 + side_len  # sem contar códigos de cor
    extra = max(0, total_len - base_len)
    right = " " + Fore.CYAN + ("=" * (side_len + extra))

    print(left + center + right + Style.RESET_ALL)

def print_info(label, value, color=Fore.WHITE):
    print(color + f"{label:<12} : {value}")

def executar_servico(func, token, chave, email, password, pedir_valor=False):
    """Executa um serviço chamando a função do utils e mostra resultado na mesma linha"""
    amount = None
    if pedir_valor:
        try:
            amount = int(input(Fore.YELLOW + "• Insira o Novo Valor: " + Style.RESET_ALL).strip())
        except ValueError:
            print(Fore.RED + "• Executando Serviço: Valor inválido.")
            time.sleep(2)
            return None

    print(Fore.WHITE + "• Executando Serviço: " + Style.RESET_ALL, end="")

    try:
        if pedir_valor:
            resp = func(chave=chave, token=token, amount=amount, api_url=API_URL)
        else:
            resp = func(chave=chave, token=token, api_url=API_URL)

        # aceitar hem mock hem gerçek formatları
        status_ok = False
        if isinstance(resp, dict):
            if resp.get("status_code") == 200 or resp.get("status") == "ok" or resp.get("success") == True:
                status_ok = True

        if status_ok:
            print(Fore.LIGHTGREEN_EX + "Sucesso")
        else:
            msg = resp.get("message") or str(resp)
            print(Fore.RED + f"Erro: {msg}")

    except Exception as e:
        print(Fore.RED + f"Erro inesperado: {e}")
        return None

    while True:
        opt = input(Fore.WHITE + "• Retornar Ao Menu Principal? (Y/N): " + Style.RESET_ALL).strip().lower()
        if opt == "y":
            return True
        elif opt == "n":
            print(Fore.CYAN + "Bye Bye...")
            exit(0)
        else:
            print(Fore.RED + "❌ Opção inválida! Digite apenas Y ou N.")
            time.sleep(2)

def menu_loop(dados, token, chave, email, password):
    while True:
        clear()
        header()

        print_title_inside_line("User Detail")
        print_info("ID", dados.get("id"))
        print_info("Key", dados.get("key"))
        print_info("Validade", dados.get("valid_until"))

        print_title_inside_line("Menu")
        print(Fore.WHITE + "[" + Fore.CYAN + "01" + Fore.WHITE + "] Inject Account In Generator.")
        print(Fore.WHITE + "[" + Fore.CYAN + "00" + Fore.WHITE + "] Exit Tool.")

        print(Fore.CYAN + "=" * 59)
        opt = input(
            Fore.WHITE + "Input Number Menu " +
            Fore.CYAN + "[" + 
            Fore.WHITE + "00 - 01" + 
            Fore.CYAN + "]" + 
            Style.RESET_ALL + ": "
        ).strip()

        if opt in ("0", "00"):
            print(Fore.CYAN + "Bye Bye...")
            return False
        elif opt in ("1", "01"):
            return executar_servico(inject_account, token, chave, email, password)
        else:
            print(Fore.RED + "Opção Inválida. Recarregando Menu Em 3 Segundos...")
            time.sleep(3)

def login_e_menu(key, email, password):
    """Mocked: direto para menu sem pedir validação"""
    token = "local_dummy_token"
    dados_para_menu = {
        "id": "0000",
        "key": key or "no-key",
        "valid_until": "∞"
    }
    return menu_loop(dados_para_menu, token, key, email, password)

def main():
    try:
        clear()
        header()

        # Buradan itibaren kullanıcı girişleri KALDIRILDI — doğrudan çalışacak
        # Eğer istersen başlatma bilgisi ekle
        print(Fore.LIGHTGREEN_EX + "Starting tool without key checks...")

        # Varsayılan/basit kullanıcı bilgileri
        key = "no-key"
        email = "no-email"
        password = "no-password"

        time.sleep(1)

        dados_para_menu = {
            "id": "0000",
            "key": key,
            "valid_until": "∞"
        }

        recarregar = menu_loop(dados_para_menu, "fake_token", key, email, password)

        while recarregar:
            recarregar = menu_loop(dados_para_menu, "fake_token", key, email, password)
            if not recarregar:
                break

    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Bye Bye...")

if __name__ == "__main__":
    main()
