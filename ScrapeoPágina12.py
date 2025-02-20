import random
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configurar las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--incognito")  # Modo incógnito
chrome_options.add_argument("--headless")  # Modo sin interfaz gráfica
chrome_options.add_argument("--disable-gpu")  # Para mejorar la compatibilidad en modo headless
chrome_options.add_argument("--window-size=1920x1080")  # Para asegurar que las páginas se vean correctamente

# Crear el servicio de Chrome
service = Service('______') ruta al chromedriver.exe

fecha_inicio = "AAAA-MM-DD"
fecha_final = "AAAA-MM-DD"
términos_búsqueda = "términos a buscar"


# Inicializar el navegador con el servicio y las opciones
driver = webdriver.Chrome(service=service, options=chrome_options)

# Esperar explícita
wait = WebDriverWait(driver, 12)

# Función para intentar localizar un elemento usando varios métodos con espera explícita
def encontrar_elemento(driver, metodos):
    for metodo, valor in metodos:
        try:
            elemento = wait.until(EC.presence_of_element_located((metodo, valor)))
            return elemento  # Si encuentra el elemento, lo retorna
        except Exception as e:
            print(f"No se pudo encontrar el elemento con {metodo} y valor {valor}. Probando con el siguiente...")
    return None  # Si ninguno funciona, retorna None

# Función para cerrar todas las pestañas excepto la principal
def cerrar_pestanas_excepto_principal():
    # Mantener la primera pestaña abierta (índice 0)
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    # Volver a la pestaña principal
    driver.switch_to.window(driver.window_handles[0])

# Extraer información resultados
def obtener_informacion():
    # Obtener los resultados de la búsqueda
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')

    # Lista para almacenar los datos
    datos = []

    # Abrir cada resultado en una nueva pestaña con tiempo aleatorio entre 4 y 6 segundos
    for index, result in enumerate(results):
        # Obtener el enlace del resultado
        link = result.find_element(By.TAG_NAME, "a").get_attribute("href")

        # Abrir una nueva pestaña
        driver.execute_script(f"window.open('{link}', '_blank');")

        # Reintentar hasta 3 veces si no se abre la pestaña
        max_reintentos = 3
        for intento in range(1, max_reintentos + 1):
            # Verificar si la pestaña realmente se abrió
            if len(driver.window_handles) > index + 1:
                # Cambiar a la nueva pestaña
                driver.switch_to.window(driver.window_handles[index + 1])
                break  # Salir del bucle si la pestaña se abrió correctamente
            else:
                # Si no se abrió, esperar más tiempo y reintentar
                tiempo_espera = intento * 3  # Incrementar el tiempo de espera en cada intento
                print(f"Reintento {intento}: No se pudo abrir la pestaña {index + 1}. Esperando {tiempo_espera} segundos.")
                time.sleep(tiempo_espera)
        else:
            # Si después de 10 intentos no se abre, continuar con el siguiente resultado
            print(f"No se pudo abrir la pestaña {index + 1} después de {max_reintentos} intentos. Saltando al siguiente resultado.")
            continue

        # Esperar que la página cargue
        time.sleep(random.uniform(4, 6))

        # Inicializar variables de los campos
        title, epigrafe, subtitulo, autor, link, seccion, fecha = '', '', '', '', '', '', ''

        try:
            title_element = driver.find_element(By.TAG_NAME, "h1")
            title = title_element.text
            print(f"Título extraído en pestaña {index + 1}: {title}")
        except Exception as e:
           print(f"No se pudo extraer el título en la pestaña {index + 1}: {e}")

        # Lista de métodos para encontrar el epígrafe
        metodos_epigrafe = [
            (By.CLASS_NAME, "h4"),
            (By.XPATH, "/html/body/div[2]/div[8]/div[1]/article/div[1]/div[2]/h2[1]"),
            (By.TAG_NAME, "h2"),
            (By.ID, "col2-col"),
            (By.CSS_SELECTOR, "body > div:nth-child(2) > div.row-content--sidebar--gutter--marginBottom.first-row.flex-on-mobile > div.content > article > div.section-2-col.article-header > div.col.\\32 -col > h2.h4.ff-16px-w700"),
        ]

        # Intentar obtener el epígrafe con diferentes métodos
        epigrafe_element = encontrar_elemento(driver, metodos_epigrafe)
        if epigrafe_element:
            epigrafe = epigrafe_element.text
            print(f"Epígrafe extraído: {epigrafe}")
        else:
            print(f"No se pudo extraer el epígrafe en la pestaña {index + 1}")

        # Lista de métodos para encontrar el subtítulo
        metodos_subtitulo = [
            (By.XPATH, "/html/body/div[2]/div[8]/div[1]/article/div[1]/div[2]/h2[2]"),
            (By.TAG_NAME, "h3 ff-20px-w400"),
            (By.ID, "subtitulo-id"),
            (By.NAME, "subtitulo-name"),  
            (By.LINK_TEXT, "Subtítulo del artículo"),
            (By.PARTIAL_LINK_TEXT, "Subtítulo")
        ]

        # Intentar obtener el subtítulo con diferentes métodos
        subtitulo_element = encontrar_elemento(driver, metodos_subtitulo)
        if subtitulo_element:
            subtitulo = subtitulo_element.text
            print(f"Subtítulo extraído: {subtitulo}")
        else:
            print(f"No se pudo extraer el subtítulo en la pestaña {index + 1}")

        # Obtener autor
        try:
            autor_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[8]/div[1]/article/div[1]/div[2]/div/div/a/div[2]")
            autor = autor_element.text
            print(f"Autor extraído: {autor}")
        except Exception as e:
            print(f"No se pudo extraer el autor en la pestaña {index + 1}: {e}")

        # intentar obtener sección
        try:
            seccion_element = driver.find_element(By.TAG_NAME, "h5")
            seccion = seccion_element.text
            print(f"Seccion extraída: {seccion}")
        except Exception as e:
            print(f"No se pudo extraer la sección en la pestaña {index +1}: {e}")
        
         # intentar obtener fecha
        try:
            fecha_element = driver.find_element(By.TAG_NAME, "time")
            fecha = fecha_element.text
            print(f"Fecha extraída: {fecha}")
        except Exception as e:
            print(f"No se pudo extraer la fecha en la pestaña {index +1}: {e}")
        
        #obtener link
        link_actual = driver.current_url
        print(f"Link de la pestaña {index + 1}: {link_actual}")

        # Guardar los datos en la lista
        datos.append([title, epigrafe, subtitulo, autor, link_actual, seccion, fecha])
     

        # Cambiar de vuelta a la primera pestaña
        driver.switch_to.window(driver.window_handles[0])
    cerrar_pestanas_excepto_principal()

    # Retornar los datos recopilados
    return datos

#Función para ir a la siguiente página de resultados de Google
def siguiente_pagina():
    try:
        next_button = driver.find_element(By.ID, "pnnext")
        next_button.click()
        time.sleep(2)
        return True  # Avanzó correctamente
    except Exception as e:
        print(f"No se pudo avanzar a la siguiente página: {e}")
        return False  # No pudo avanzar (final de los resultados)

# Abrir Google y realizar una búsqueda
driver.get("https://www.google.com")
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys(f"{términos_búsqueda} site:pagina12.com.ar after:{fecha_inicio} before:{fecha_final}")
search_box.send_keys(Keys.RETURN)

# Esperar un poco para que se carguen los resultados
time.sleep(2)

# Abrir un archivo CSV para guardar los resultados
with open(f'Página12{términosbúsqueda}_{fecha_inicio}_{fecha_final}.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Título', 'Epígrafe', 'Subtítulo', 'Autor', 'Link', 'Sección', 'Fecha'])

    # Recolectar la información de todas las páginas
    pagina = 1
    while True:
        print(f"Extrayendo datos de la página {pagina}")
        datos = obtener_informacion()
        writer.writerows(datos)

        #Intentar ir a la siguiente página de resultados de Google    
        if not siguiente_pagina():
            break  # Si no puede avanzar, terminar el bucle

        pagina += 1

# Cerrar el navegador
driver.quit()
