import math
import re
import tkinter as tk
import winsound
from PIL import Image, ImageTk
import pyttsx3
import speech_recognition as sr
import webbrowser
import requests
import os
import time
import pyautogui
from docx import Document
from bs4 import BeautifulSoup
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import pygetwindow as gw
import google.generativeai as genai
import subprocess
import screen_brightness_control as sbc


# API_NEWS_KEY = ""  

TEMAS_POPULARES = ["tecnología", "salud", "deportes", "ciencia", "negocios", "entretenimiento", "política"]

# API key de OpenWeather 
# API_KEY = ''

# API = ""
genai.configure(api_key=API)

# Configuración de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad de la voz
engine.setProperty('volume', 1)  # Volumen de la voz
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 para voz masculina, 1 para voz femenina

# Función para que el asistente hable
def hablar(mensaje):
    engine.say(mensaje)
    engine.runAndWait()

# Función para emitir un pitido
def emitir_pitido():
    winsound.Beep(500, 500)
    
def escuchar_comando():
    """Función para escuchar la voz del usuario y convertirla en texto."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        
        try:
            r.adjust_for_ambient_noise(source, duration=1)  # Ajusta el ruido de fondo
            audio = r.listen(source, timeout=6, phrase_time_limit=6)  # Espera máximo 6 segundos
            comando = r.recognize_google(audio, language='es-ES')
            print(f"Comando recibido: {comando}")
            return comando.lower()
        
        except sr.UnknownValueError:
            hablar("No entendí el comando, por favor repítelo.")
            return None
        
        except sr.RequestError:
            hablar("No se pudo conectar con el servicio de reconocimiento de voz.")
            return None
        
        except Exception as e:
            print(f"Error inesperado: {e}")
            hablar("Ocurrió un error inesperado. Por favor, intenta de nuevo.")
            return None




# Función para obtener la ubicación del usuario
def obtener_ubicacion():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        ciudad = data['city']
        return ciudad
    except Exception as e:
        hablar("No pude obtener tu ubicación.")
        print(f"Error al obtener la ubicación: {e}")
        return None

# Función para consultar el clima usando la API de OpenWeather
def consultar_clima(ciudad=""):
    if not ciudad:
        ciudad = obtener_ubicacion()  # Obtener la ubicación automáticamente
        if not ciudad:
            hablar("No se pudo determinar la ubicación para consultar el clima.")
            return
    
    hablar(f"Consultando el clima en {ciudad}.")
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["cod"] == 200:  # Si la respuesta es exitosa
            temperatura = data["main"]["temp"]
            descripcion = data["weather"][0]["description"]
            humedad = data["main"]["humidity"]
            viento = data["wind"]["speed"]
            
            mensaje_clima = f"En {ciudad}, la temperatura es de {temperatura} grados Celsius, con {descripcion}. La humedad es del {humedad}% y el viento sopla a {viento} metros por segundo."
            hablar(mensaje_clima)
        else:
            hablar("No pude obtener la información del clima en este momento.")
    except Exception as e:
        hablar("Hubo un error obteniendo el clima.")
        print(f"Error al consultar el clima: {e}")


# Función para buscar en Google y abrir el navegador
def buscar_en_google(consulta):
    hablar(f"Buscando {consulta} en Google.")
    query = consulta.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    hablar(f"He abierto Google para buscar: {consulta}")

# Función para leer el contenido de la primera página de resultados de Google
def leer_google_resultados(consulta):
    hablar(f"Leyendo los resultados de la búsqueda en Google para {consulta}.")
    query = consulta.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    resultados = soup.find_all('h3')  # Extraer los títulos de los resultados de búsqueda
    
    for i, resultado in enumerate(resultados[:5]):  # Leer los primeros 5 resultados
        hablar(f"Resultado {i+1}: {resultado.get_text()}")

# Función para buscar en YouTube y reproducir la canción
def reproducir_cancion(nombre_cancion):
    hablar(f"Buscando {nombre_cancion} en YouTube.")
    query = nombre_cancion.replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    
    time.sleep(5)  # Espera a que cargue la página de resultados
    
def seleccionar_opcion(opcion):
    # Diccionario para mapear palabras a números
    opciones = {
    "1": 1, "uno": 1, "Uno" :1,
    "2": 2, "dos": 2, "Dos": 2,
    "3": 3, "tres": 3,"Tres": 3,
    "4": 4, "cuatro": 4, "Cuatro": 4
}

    # Interpretar la opción, devolviendo None si no es válida
    numero = opciones.get(str(opcion).strip(), None)
    # Realizar acción basada en el número
    if numero == 1:
        pyautogui.moveTo(477, 371, duration=1)
        pyautogui.click()
    elif numero == 2:
        pyautogui.moveTo(454, 644, duration=1)
        pyautogui.click()
    elif numero == 3:
        pyautogui.moveTo(485, 574, duration=1)
        pyautogui.click()
    elif numero == 4:
        pyautogui.moveTo(479, 555, duration=1)
        pyautogui.click()
    else:
        hablar("Lo siento, solo puedo abrir las opciones de uno a cuatro.")

# Función para abrir un archivo específico en el escritorio
def abrir_archivo(nombre_archivo):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    archivo_path = os.path.join(desktop_path, nombre_archivo)
    
    if os.path.exists(archivo_path):
        hablar(f"Abriendo el archivo {nombre_archivo}.")
        os.startfile(archivo_path)
    else:
        hablar(f"No encontré el archivo {nombre_archivo} en el escritorio.")

# Función para abrir y leer el PDF en Microsoft Edge
def leer_pdf_en_edge(nombre_archivo):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    archivo_path = os.path.join(desktop_path, nombre_archivo)

    if os.path.exists(archivo_path):
        hablar(f"Abriendo el archivo PDF {nombre_archivo} en Microsoft Edge.")
        os.startfile(archivo_path)  # Abrir el PDF con el programa predeterminado (Edge)

        time.sleep(3)  # Esperar a que Edge abra el archivo

        # iniciar la lectura automática
        pyautogui.hotkey('ctrl', 'shift', 'u')
        hablar("Iniciando la lectura del PDF.")

    else:
        hablar(f"No encontré el archivo PDF {nombre_archivo} en el escritorio.")

# Función para pausar la lectura del PDF
def pausar_lectura_pdf():
    pyautogui.hotkey('ctrl', 'shift', 'u')

# Función para cerrar el PDF
def cerrar_pdf():
    hablar("Cerrando el archivo PDF.")
    pyautogui.moveTo(358, 17, duration=1)  # Mover a la coordenada de cierre
    pyautogui.click()  # Hacer clic para cerrar el archivo

# Función para leer archivos Word
def leer_word(nombre_archivo):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    archivo_path = os.path.join(desktop_path, nombre_archivo)
    
    if os.path.exists(archivo_path):
        hablar(f"Leyendo el archivo de Word {nombre_archivo}.")
        doc = Document(archivo_path)
        texto = ''
        for para in doc.paragraphs:
            texto += para.text + '\n'
        hablar(texto[:500])  # Leer solo los primeros 500 caracteres
    else:
        hablar(f"No encontré el archivo de Word {nombre_archivo} en el escritorio.")
    
def apagar_sistema():
    hablar("Apagando el equipo.")
    os.system("shutdown /s /t 1")

def reiniciar_sistema():
    hablar("Reiniciando el equipo.")
    os.system("shutdown /r /t 1")

def suspender_sistema():
    hablar("Suspendiendo el equipo.")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def abrir_spotify():
    hablar("Abriendo Spotify.")
    os.startfile("spotify.exe")

def pausar_reproducir_video():
    hablar("Ok.")
    pyautogui.moveTo(234, 419, duration=1)  
    pyautogui.click()  


def iniciar_lectura_pdf():
    hablar("Iniciando la lectura del PDF.")
    pyautogui.hotkey('ctrl', 'shift', 'u')  # Ejemplo de atajo para lectura en voz alta (ajusta según el software)

# Función para obtener el control del volumen
def obtener_control_volumen():
    dispositivos = AudioUtilities.GetSpeakers()
    interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
    return volumen

# Función para ajustar el volumen
def ajustar_volumen_porcentaje(porcentaje):
    volumen = obtener_control_volumen()
    rango_min, rango_max, _ = volumen.GetVolumeRange()

    # Mapear el porcentaje de manera lineal en el rango del volumen del sistema
    if porcentaje < 0:
        porcentaje = 0
    elif porcentaje > 100:
        porcentaje = 100
    
    # Ajustamos utilizando la fórmula logarítmica para mayor precisión
    nivel_volumen = rango_min + (porcentaje / 100) * (rango_max - rango_min)

    # Aplicamos el nivel de volumen calculado
    volumen.SetMasterVolumeLevel(nivel_volumen, None)
    hablar(f"El volumen se ha ajustado al {porcentaje}%.")



# Función para subir el volumen a un porcentaje dado
def subir_volumen_porcentaje(porcentaje):
    hablar(f"Subiendo el volumen al {porcentaje} por ciento.")
    ajustar_volumen_porcentaje(porcentaje)

# Función para bajar el volumen a un porcentaje dado
def bajar_volumen_porcentaje(porcentaje):
    hablar(f"Bajando el volumen al {porcentaje} por ciento.")
    ajustar_volumen_porcentaje(porcentaje)

# Función para obtener el volumen actual
def obtener_volumen_actual():
    volumen = obtener_control_volumen()
    rango_min, rango_max, _ = volumen.GetVolumeRange()
    nivel_actual = volumen.GetMasterVolumeLevel()
    # Convertir el nivel actual de volumen en porcentaje
    porcentaje = ((nivel_actual - rango_min) / (rango_max - rango_min)) * 100
    return math.ceil(porcentaje)

def abrir_calculadora():
    hablar("Abriendo la calculadora.")
    os.system("calc")

# Función para abrir el Bloc de notas
def abrir_bloc_de_notas():
    # Abre el Bloc de notas sin bloquear el flujo de ejecución
    subprocess.Popen("notepad.exe")
    time.sleep(2)  # Espera para que el Bloc de notas se abra
    
    # Busca y activa la ventana del Bloc de notas
    ventana_notepad = gw.getWindowsWithTitle("Bloc de notas")
    if ventana_notepad:
        ventana_notepad[0].activate()  # Trae la ventana al frente
        time.sleep(1)  # Espera adicional para asegurar que la ventana esté activa
        return True
    else:
        hablar("No pude encontrar la ventana del Bloc de notas.")
        return False

# Función para escribir en el Bloc de notas
def escribir_en_bloc_de_notas():
    if abrir_bloc_de_notas():  # Solo continúa si el Bloc de notas se abrió correctamente
        hablar("¿Qué quieres que anote?")
        
        # Escuchar lo que el usuario quiere que se escriba
        texto = escuchar_comando()  # Asegúrate de que escuchar_comando esté bien implementado
        
        if texto:
            hablar(f"Voy a anotar: {texto}")
            time.sleep(1)  # Pausa para asegurar que el Bloc de notas esté activo
            
            # Asegúrate de que el Bloc de notas esté en primer plano antes de escribir
            pyautogui.write(texto, interval=0.1)
            hablar(f"He anotado: {texto}")
        else:
            hablar("No entendí lo que querías que anotara.")
    else:
        hablar("Hubo un problema al abrir el Bloc de notas.")

def ask_gemini(question):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        print(f"Error al usar Gemini: {e}")
        return "Hubo un error obteniendo la respuesta de Gemini."

def crear_carpeta(nombre_carpeta):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    carpeta_path = os.path.join(desktop_path, nombre_carpeta)
    
    if not os.path.exists(carpeta_path):
        os.mkdir(carpeta_path)
        hablar(f"Carpeta {nombre_carpeta} creada en el escritorio.")
    else:
        hablar(f"La carpeta {nombre_carpeta} ya existe en el escritorio.")

def abrir_explorador_archivos():
    try:
        os.startfile("shell:::{679f85cb-0220-4080-b29b-5540cc05aab6}")  # Abre la raíz del disco C:
        hablar("He abierto el explorador de archivos")
    except Exception as e:
        hablar("Lo siento, no puedo abrir el explorador de archivos en este momento.")
        print(f"Error al abrir el explorador de archivos: {e}")

# Función para abrir WhatsApp Desktop
def abrir_whatsapp():
    """Abre WhatsApp Desktop."""
    try:
        import subprocess
        subprocess.run("start whatsapp:", shell=True)  # Abre WhatsApp Desktop
        hablar("He abierto WhatsApp.")
    except Exception as e:
        hablar("No puedo abrir WhatsApp en este momento. Por favor, asegúrate de que esté instalado.")
        print(f"Error: {e}")

def enviar_mensaje(numero, mensaje):
    """Envía un mensaje de WhatsApp a un número en formato internacional."""
    try:
        # Limpia el número y asegúrate de que solo tenga dígitos
        numero = re.sub(r'\D', '', numero)  # Elimina caracteres no numéricos
        
        if len(numero) == 10:  # Si tiene 10 dígitos (número local), le agregamos el prefijo de Colombia
            numero = '57' + numero

        if not numero.startswith('57'):  # Asegúrate de que tenga el prefijo correcto
            hablar("El número no parece ser válido para Colombia. Por favor, verifica e intenta de nuevo.")
            return

        url = f"https://wa.me/{numero}?text={mensaje.replace(' ', '%20')}"
        webbrowser.open(url)  # Abre el enlace en el navegador o en WhatsApp
        pyautogui.moveTo(724, 247, duration=2)
        pyautogui.click()
        pyautogui.write(mensaje, interval=0.1)
        pyautogui.press('enter')  # Presiona enter para enviar el mensaje
        hablar(f"Enviando mensaje al número {numero}.")
    except Exception as e:
        hablar("No he podido enviar el mensaje. Por favor, inténtalo de nuevo.")
        print(f"Error: {e}")

def procesar_comando_mensaje():
    """Realiza todo el flujo para enviar un mensaje de WhatsApp."""
    try:
        abrir_whatsapp()  # Abre WhatsApp Desktop
        hablar("Dime el número de teléfono al que deseas enviar el mensaje. Por favor, dilo solo con números, sin el prefijo +57.")
        numero = escuchar_comando()  # El usuario dice el número
        if not numero:
            hablar("No entendí el número, por favor intenta de nuevo.")
            return
        
        hablar("Ahora dime el mensaje que deseas enviar.")
        mensaje = escuchar_comando()  # El usuario dice el mensaje
        if not mensaje:
            hablar("No entendí el mensaje, por favor intenta de nuevo.")
            return
        
        # Confirmación con el usuario
        hablar(f"Vas a enviar el mensaje: '{mensaje}' al número: {numero}. ¿Es correcto? Responde es correcto o no.")
        confirmacion = escuchar_comando()
        
        if confirmacion and "correcto" in confirmacion.lower():
            enviar_mensaje(numero, mensaje)
        else:
            hablar("Entendido. Cancelo el envío del mensaje.")
    except Exception as e:
        hablar("Algo salió mal mientras procesaba tu solicitud.")
        print(f"Error: {e}")

# Función para convertir palabras de números a dígitos
NUMEROS_PALABRAS = {
    "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
}

def palabra_a_numero(palabra):
    palabra = palabra.lower().strip()
    return NUMEROS_PALABRAS.get(palabra, None)

# Función para listar temas
def listar_temas():
    temas_disponibles = ", ".join(TEMAS_POPULARES)
    hablar(f"Los temas populares son: {temas_disponibles}. ¿Sobre cuál tema te gustaría escuchar?")

# Función para leer noticias
def leer_noticias(tema=None):
    if not tema:
        listar_temas()
        tema = escuchar_comando()
        if not tema:
            return

    hablar(f"Buscando noticias sobre {tema}.")
    url = f"https://newsapi.org/v2/everything?q={tema}&sortBy=publishedAt&apiKey={API_NEWS_KEY}&language=es"
    try:
        response = requests.get(url)
        noticias = response.json()
        if noticias["status"] == "ok":
            articles = noticias["articles"][:5]  # Leer las primeras 5 noticias
            if articles:
                hablar("Encontré estas noticias:")
                for i, articulo in enumerate(articles):
                    titulo = articulo["title"]
                    fuente = articulo["source"]["name"]
                    hablar(f"Noticia {i + 1}: {titulo}, de {fuente}.")
                
                hablar("Por favor, di el número o el nombre del número de la noticia que quieres que lea en detalle.")
                seleccion = escuchar_comando()

                # Convertir palabras a números o verificar si es un dígito válido
                if seleccion:
                    if seleccion.isdigit():
                        numero = int(seleccion)
                    else:
                        numero = palabra_a_numero(seleccion)

                    if numero and 1 <= numero <= len(articles):
                        seleccionado = articles[numero - 1]
                        detalles = seleccionado["description"] or "Descripción no disponible."
                        url = seleccionado["url"]
                        hablar(f"Aquí está la noticia completa: {seleccionado['title']}. {detalles}. Puedes leer más en {url}")
                    else:
                        hablar("Selección inválida. Por favor intenta nuevamente.")
            else:
                hablar(f"No encontré noticias sobre el tema {tema}. ¿Deseas probar con otro tema?")
                tema_alternativo = escuchar_comando()
                if tema_alternativo:
                    leer_noticias(tema_alternativo)
        else:
            hablar("No pude obtener las noticias en este momento.")
    except Exception as e:
        hablar("Hubo un error obteniendo las noticias.")
        print(f"Error al obtener noticias: {e}")

#Funcion ajustar brillo
def ajustar_brillo(nivel):
    try:
        # Ajustar el brillo al nivel especificado (0-100)
        sbc.set_brightness(nivel)
        print(f"El brillo se ha ajustado al {nivel}%.")
    except Exception as e:
        print(f"Error al ajustar el brillo: {e}")



#Ejecución de comandos del asistente
def ejecutar_comando(comando):
    if "clima" in comando:
        if "en" in comando:
            ciudad = comando.split("en")[-1].strip()  # Extraer la ciudad del comando
            consultar_clima(ciudad)
        else:
            consultar_clima()  # Consultar clima según ubicación actual
    elif "busca en google" in comando:
        consulta = comando.replace("busca en google", "").strip()
        buscar_en_google(consulta)
    elif "lee los resultados de google" in comando:
        consulta = comando.replace("lee los resultados de google", "").strip()
        leer_google_resultados(consulta)
    elif "abre youtube" in comando:
        hablar("YouTube ha sido abierto. ¿Qué deseas buscar?")
        busqueda = escuchar_comando()  # Escuchar el comando para buscar
        if busqueda:
            reproducir_cancion(busqueda)
            hablar("¿Qué opción deseas abrir? Dime el número de la opción .")
            opcion = escuchar_comando().strip().lower()  # Escuchar el número de la opción y normalizar
            seleccionar_opcion(opcion)
    elif "abre el archivo" in comando:
        nombre_archivo = comando.replace("abre el archivo", "").strip()
        abrir_archivo(nombre_archivo)
    elif "lee el archivo" in comando:
        nombre_archivo = comando.replace("lee el archivo pdf", "").strip()
        leer_pdf_en_edge(nombre_archivo)
    elif "pausar lectura" in comando:
        pausar_lectura_pdf()
    elif "pausar video" in comando:
        pausar_reproducir_video()
    elif "reanudar video" in comando:
        pausar_reproducir_video()
    elif "cerrar pdf" in comando:
        cerrar_pdf()
    elif "lee el archivo word" in comando:
        nombre_archivo = comando.replace("lee el archivo word", "").strip()
        leer_word(nombre_archivo)
    elif "apagar equipo" in comando:
        apagar_sistema()
    elif "abrir bloc de notas" in comando:
        escribir_en_bloc_de_notas()  # Llamamos a la nueva función que maneja el bloc de notas
    elif "reiniciar equipo" in comando:
        reiniciar_sistema()
    elif "suspender equipo" in comando:
        suspender_sistema()
    elif "abrir spotify" in comando:
        abrir_spotify()
    elif "abrir calculadora" in comando:
        abrir_calculadora()
    elif "subir volumen" in comando:
        try:
            # Extraer el número del comando para el porcentaje
            porcentaje = int(comando.split("subir volumen al")[-1].strip())
            if 0 <= porcentaje <= 100:
                subir_volumen_porcentaje(porcentaje)
            else:
                hablar("Por favor, proporciona un número entre 0 y 100.")
        except ValueError:
            hablar("No pude entender el valor del porcentaje.")
    elif "bajar volumen" in comando:
        try:
            # Extraer el número del comando para el porcentaje
            porcentaje = int(comando.split("bajar volumen al")[-1].strip())
            if 0 <= porcentaje <= 100:
                bajar_volumen_porcentaje(porcentaje)
            else:
                hablar("Por favor, proporciona un número entre 0 y 100.")
        except ValueError:
            hablar("No pude entender el valor del porcentaje.")
    elif "volumen actual" in comando:
        volumen_actual = obtener_volumen_actual()
        hablar(f"El volumen actual es del {volumen_actual} por ciento.")
    elif "oye" in comando:
        pregunta = comando.replace("oye olivia", "").strip()
        respuesta = ask_gemini(pregunta)
        hablar(f"Esto es lo que encontré: {respuesta}")
    elif "crear carpeta" in comando:
        nombre_carpeta = comando.replace("crear carpeta", "").strip()
        crear_carpeta(nombre_carpeta)
    elif "abrir el explorador de archivos" in comando:
        abrir_explorador_archivos()
    elif  "abre whatsapp" in comando:
        procesar_comando_mensaje()
    elif "noticias" in comando:
        leer_noticias()
    elif "ajustar brillo al" in comando:
        try:
            nivel_brillo = int(comando.split("ajustar brillo al")[-1].strip())
            if 0 <= nivel_brillo <= 100:
                ajustar_brillo(nivel_brillo)
            else:
                hablar("Por favor, proporciona un nivel de brillo entre 0 y 100.")
        except ValueError:
            hablar("No pude entender el nivel de brillo que mencionaste.")
    else:
        hablar("Lo siento, no entendí el comando.")
    



# Clase para la interfaz de Olivia
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class VirtualAssistantUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Asistente Virtual Olivia")
        self.root.geometry("400x400")
        self.root.config(bg="#282c34")  # Color de fondo moderno

        # Hacer que la ventana esté siempre encima
        self.root.attributes("-topmost", True)

        # Cargar y redimensionar imagen del asistente
        self.image = Image.open("olivia.png")
        self.image = self.image.resize((200, 200), Image.LANCZOS)
        self.assistant_img = ImageTk.PhotoImage(self.image)

        # Crear un label para mostrar la imagen del asistente
        self.avatar_label = tk.Label(self.root, image=self.assistant_img, bg="#282c34")
        self.avatar_label.pack(pady=20)

        # Botón de estado del asistente
        self.status_label = tk.Label(self.root, text="Presiona Ctrl + J para activar", 
        font=("Arial", 14), bg="#282c34", fg="white")
        self.status_label.pack(pady=20)

        # Asignar evento de teclado para Ctrl + J
        self.root.bind('<Control-j>', self.activar_asistente)

        # Posicionar la ventana en la parte inferior derecha
        self.position_window()

    def position_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 400
        y = screen_height - 450
        self.root.geometry(f"+{x}+{y}")

    def activar_asistente(self, event=None):
        hablar("Hola, soy Olivia, en qué puedo ayudarte ")  # Presentación del asistente
        self.status_label.config(text="Respondiendo...", fg="green")  # Actualiza la etiqueta de estado

        comando_usuario = escuchar_comando()  # Escuchar el comando del usuario
        if comando_usuario:  # Verifica si hay un comando
            ejecutar_comando(comando_usuario)  # Ejecuta el comando
        else:
            hablar("No he entendido el comando, por favor intenta de nuevo.")  # Mensaje de error si no se recibe comando

        self.status_label.config(text="Presiona Ctrl + J para activar", fg="White")  # Restablece el estado


# Configuración de la ventana principal de Tkinter
root = tk.Tk()
app = VirtualAssistantUI(root)
root.mainloop()








