import subprocess
import time
import socket
import requests
import os
import signal

# Configuración
SSH_USER = "root"
SSH_HOST = "netsim.octupus.com"
SOCKS_PORT = 1080
SSH_CMD = f"ssh -N -D {SOCKS_PORT} -f {SSH_USER}@{SSH_HOST}"

def start_socks5_tunnel():
    """Inicia el túnel SOCKS5 mediante SSH."""
    try:
        subprocess.run(SSH_CMD, shell=True, check=True)
        print(f"Túnel SOCKS5 iniciado en el puerto {SOCKS_PORT}")
    except subprocess.CalledProcessError as e:
        print(f"Error al iniciar el túnel: {e}")

def is_socks5_tunnel_active():
    """Verifica si el túnel SOCKS5 está activo probando la conexión."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", SOCKS_PORT)) == 0

def check_ip_through_proxy():
    """Verifica la IP pública usando el túnel SOCKS5."""
    proxies = {
        "http": f"socks5h://127.0.0.1:{SOCKS_PORT}",
        "https": f"socks5h://127.0.0.1:{SOCKS_PORT}"
    }
    try:
        ip = requests.get("https://api64.ipify.org", proxies=proxies, timeout=5).text
        print(f"Tu IP pública a través del proxy SOCKS5 es: {ip}")
    except requests.RequestException:
        print("No se pudo obtener la IP a través del proxy SOCKS5.")

def stop_socks5_tunnel():
    """Cierra el túnel SOCKS5 terminando el proceso SSH."""
    try:
        subprocess.run("pkill -f 'ssh -N -D'", shell=True)
        print("Túnel SOCKS5 detenido.")
    except Exception as e:
        print(f"Error al detener el túnel: {e}")

# Uso
if __name__ == "__main__":
    start_socks5_tunnel()
    time.sleep(2)  # Espera un poco para que el túnel se inicie

    if is_socks5_tunnel_active():
        print("El túnel SOCKS5 está activo.")
        check_ip_through_proxy()
    else:
        print("El túnel SOCKS5 no está activo.")

    # Detener el túnel después de la verificación
    #stop_socks5_tunnel()