import os
import time
from colorama import init, Fore, Style
from utils import (
    verificar_key_com_fingerprint, login, API_URL, inject_account, set_api_url
)

init(autoreset=True)

VERSION = "1.0.0"
DEV_LINK = "aydnqx"  # artık hiçbir dış linke işaret etmiyor

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
    base_len = side_len + 1 + len(title_str) + 1 + side_len
    extra = max(0, total_len - base_len)
    right = " " + Fore.CYAN + ("=" * (side_len + extra))
    print(left + center + right + Style.RESET_ALL)

def print_info(label, value, color=Fore.WHITE):
    print(color + f"{label:<12} : {value}")

def executar_servico(func, token, chave, email, password, pedir_valor=False):
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

        if isinstance(resp, dict) and (resp.get("status_code") == 200 or resp.get("status") == "ok" or resp.get("success")):
            print(Fore.LIGHTGREEN_EX + "Sucesso")
        else:
            msg = None
            if isinstance(resp, dict):
                msg = resp.get("message") or str(resp)
            else:
                msg = str(resp)
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
        print_info("Name", "aydnqx")
        print_info("ID", dados.get("id"))
        print_info("Key", dados.get("key"))
        print_info("Validade", dados.get("valid_until"))

        print_title_inside_line("Menu")
        print(Fore.WHITE + "[" + Fore.CYAN + "01" + Fore.WHITE + "] Inject Account In Generator.")
        print(Fore.WHITE + "[" + Fore.CYAN + "00" + Fore.WHITE + "] Exit Tool.")

        print(Fore.CYAN + "=" * 59)
        opt = input(Fore.WHITE + "Input Number Menu " +
                    Fore.CYAN + "[" + Fore.WHITE + "00 - 01" + Fore.CYAN + "]" + Style.RESET_ALL + ": ").strip()

        if opt in ("0", "00"):
            print(Fore.CYAN + "Bye Bye...")
            return False
        elif opt in ("1", "01"):
            return executar_servico(inject_account, token, chave, email, password)
        else:
            print(Fore.RED + "Opção Inválida. Recarregando Menu Em 3 Segundos...")
            time.sleep(3)

def login_e_menu(key, email, password):
    key_result = verificar_key_com_fingerprint(key, api_url=API_URL)
    if key_result.get("status") != "ok":
        print(Fore.RED + key_result.get("message", "Erro desconhecido.") + Style.RESET_ALL)
        time.sleep(3)
        return False

    token = key_result.get("token")
    if not token:
        print(Fore.RED + "❌ Token não retornado." + Style.RESET_ALL)
        time.sleep(3)
        return False

    login_result = login(chave=key, email=email, password=password, token=token, api_url=API_URL)
    if not login_result.get("success"):
        print(Fore.RED + login_result.get("message", "Erro desconhecido no login.") + Style.RESET_ALL)
        time.sleep(3)
        return False

    dados_para_menu = {
        "id": key_result.get("id"),
        "key": key,
        "valid_until": key_result.get("valid_until")
    }

    return menu_loop(dados_para_menu, token, key, email, password)

def main():
    try:
        clear()
        header()

        # API URL: önce ortam değişkenine bak; yoksa kullanıcıdan sor
        env_api = os.environ.get("CUSTOM_API") or os.environ.get("API_URL")
        if env_api:
            set_api_url(env_api)
        else:
            api_input = input(Fore.WHITE + "• API Base URL (ör. https://your-bot-api.example): " + Style.RESET_ALL).strip()
            if not api_input:
                print(Fore.RED + "API URL boş. Çıkılıyor.")
                time.sleep(2)
                return
            set_api_url(api_input)

        key = input(Fore.WHITE + "• Informe Sua Key: " + Style.RESET_ALL).strip()
        if not key:
            print(Fore.RED + "Key vazia.")
            time.sleep(3)
            return

        email = input(Fore.WHITE + "• Informe Seu E-mail: " + Style.RESET_ALL).strip()
        if not email:
            print(Fore.RED + "E-mail vazio.")
            time.sleep(3)
            return

        password = input(Fore.WHITE + "• Informe Sua Senha: " + Style.RESET_ALL).strip()
        if not password:
            print(Fore.RED + "Senha vazia.")
            time.sleep(3)
            return

        print(Fore.WHITE + "• Verificando Key: " + Style.RESET_ALL, end="")
        key_result = verificar_key_com_fingerprint(key, api_url=API_URL)
        if key_result.get("status") != "ok":
            print(Fore.RED + key_result.get("message", "Erro desconhecido.") + Style.RESET_ALL)
            time.sleep(3)
            return
        print(Fore.LIGHTGREEN_EX + "Sucesso")

        token = key_result.get("token")
        if not token:
            print(Fore.RED + "❌ Token não retornado.")
            time.sleep(3)
            return

        print(Fore.WHITE + "• Fazendo Login: " + Style.RESET_ALL, end="")
        login_result = login(chave=key, email=email, password=password, token=token, api_url=API_URL)
        if not login_result.get("success"):
            print(Fore.RED + login_result.get("message", "Erro desconhecido no login.") + Style.RESET_ALL)
            time.sleep(3)
            return
        print(Fore.LIGHTGREEN_EX + "Sucesso")
        time.sleep(1)

        dados_para_menu = {
            "id": key_result.get("id"),
            "key": key,
            "valid_until": key_result.get("valid_until")
        }

        recarregar = menu_loop(dados_para_menu, token, key, email, password)

        while recarregar:
            recarregar = login_e_menu(key, email, password)
            if not recarregar:
                break

    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Bye Bye...")

if __name__ == "__main__":
    main()
