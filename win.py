import webview
import subprocess
import threading
import time
import requests
import os
import sys
import ctypes

# Crear un evento para detener el hilo
stop_event = threading.Event()

ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)


webview.settings['ALLOW_DOWNLOADS'] = True

user_version = False

if "--from-bat" in sys.argv:
    user_version = True
    # Puedes hacer alguna acción específica aquí

def start_streamlit():
    """Inicia el servidor Streamlit en un hilo separado y muestra las salidas."""
    print("Iniciando Streamlit...")
    ruta_main = "app/Dashboard.py"
    streamlit_cmd = ["python","-m","streamlit", "run", "Dashboard.py", "--server.port=8501", "--server.headless=true", "--client.toolbarMode=auto"]
    if user_version:
        streamlit_cmd = [os.path.join("python","pythonw.exe"),"-m","streamlit", "run", "Dashboard.py", "--server.port=8501", "--server.headless=true", "--client.toolbarMode=minimal"]
        
    process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(ruta_main)
    )

    def stream_output(pipe):
        """Lee y muestra la salida del proceso en tiempo real."""
        for line in iter(pipe.readline, ''):
            if line:  # Imprime solo si hay contenido
                print(line.strip())

    # Crear hilos para leer stdout y stderr
    stdout_thread = threading.Thread(target=stream_output, args=(process.stdout,))
    stderr_thread = threading.Thread(target=stream_output, args=(process.stderr,))
    stdout_thread.start()
    stderr_thread.start()

    stop_event.wait()  # Espera hasta que se establezca el evento para detenerse
    print("Deteniendo Streamlit...")
    process.terminate()
    process.wait()  # Asegura que el proceso termine antes de salir

def wait_for_streamlit():
    """Verifica continuamente si Streamlit está listo."""
    url = "http://localhost:8501"
    for _ in range(30):  # Máximo de 30 intentos (30 segundos)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

# Iniciar Streamlit en un hilo separado
thread = threading.Thread(target=start_streamlit)
thread.daemon = True
thread.start()
# Leer el contenido del archivo HTML
with open("app/static/loading.html", "r") as file:
    loading_html = file.read()

# Crear el WebView con la pantalla de "loading"
window = webview.create_window("Xungungo Stocks Analtycs", html=loading_html)

def load_streamlit():
    """Cambia a la URL de Streamlit cuando esté listo."""
    if wait_for_streamlit():
        window.load_url("http://localhost:8501")
    else:
        print("Streamlit no se inicializó a tiempo.")

# Iniciar un hilo para cambiar la URL cuando Streamlit esté listo
thread = threading.Thread(target=load_streamlit)
thread.daemon = True
thread.start()

def on_webview_close():
    """Acción a realizar cuando se cierra el WebView."""
    print("Cerrando la aplicación...")
    stop_event.set()


window.events.closed += on_webview_close

webview.start(debug=False, icon="app/static/xungungo.png")
