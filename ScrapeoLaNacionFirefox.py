import csv
import random
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time

# COMPLETAR FECHA
fecha_inicial = datetime.datetime.strptime("01/01/2023", "%d/%m/%Y")
fecha_final = fecha_inicial
términos_búsqueda = "seguridad"
output_file = f"resultados_lanacion_{términos_búsqueda}_{fecha_inicial}.csv"

#me falta: ultima pagina de resultados de 4/1/2022 -desde ventana 2 18/02/2022 - 21/12 en seguridad
#falta 30/06/22 en inseguridad
#Búsquedas realizadas: seguridad 2022, inseguridad 2022

service = Service(r'C:\Users\marti\Documents\Facu\Beca Maestría\Scraping\Selenium\geckodriver-v0.35.0-win64\geckodriver.exe')
options = webdriver.FirefoxOptions()
options.add_argument("-private")
options.add_argument('--ignore-certificate-errors')
#options.add_argument("--headless")  # Modo sin interfaz gráfica
options.set_preference("permissions.default.image", 2)  # Desactiva la carga de imágenes
options.add_argument("--disable-gpu")  # Para mejorar la compatibilidad en modo headless
options.add_argument('--disk-cache-size=4096')  
options.add_argument('--enable-application-cache')  # Activa el uso de caché
#options.page_load_strategy = 'eager' 

def espera_aleatoria(min_seconds=1, max_seconds=2): # Función para agregar esperas aleatorias
    tiempo_espera = random.uniform(min_seconds, max_seconds)
    time.sleep(tiempo_espera)

def abrir_nueva_ventana(link): # Función para iniciar una nueva ventana de incógnito para cada resultado
    # Crear una nueva instancia del navegador en modo incógnito
    new_driver = webdriver.Firefox(options=options)
    new_driver.get(link)
    return new_driver
def nueva_ventana_reintentando(link, max_reintentos=3): #función nueva ventan reintentando por si error
    intentos = 0
    while intentos < max_reintentos:
        try:
            print(f"Intentando abrir nueva ventana: intento {intentos + 1}")
            nueva_ventana = abrir_nueva_ventana(link)
            WebDriverWait(nueva_ventana, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            print(f"Ventana abierta exitosamente en el intento {intentos + 1}")
            return nueva_ventana  # Si se abre exitosamente, retornamos la nueva ventana
        except (TimeoutException, WebDriverException) as e:
            print(f"Error al abrir la ventana en el intento {intentos + 1}: {e}")
            intentos += 1
            espera_aleatoria(2, 4)  # Espera aleatoria antes de intentar de nuevo
            if intentos == max_reintentos:
                print("Superado el número máximo de reintentos para abrir la ventana.")
                return None  # Si no se logra abrir después de los reintentos, retornamos None
def reiniciar_navegador(ultima_fecha_inicio_str, ultima_fecha_fin_str): # COMPLETAR LINK - Función reiniciar navegador usando última fecha 

    global driver
    driver.quit()
    espera_aleatoria(1, 2)
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.lanacion.com.ar/buscador/?query=seguridad')
    espera_aleatoria(1, 2)

    # Rellenar nuevamente las fechas después del reinicio
    fecha_inicio = driver.find_element(By.XPATH, '//*[@id="datepicker_from"]')
    fecha_inicio.clear()
    espera_aleatoria()
    fecha_inicio.send_keys(ultima_fecha_inicio_str)

    fecha_fin = driver.find_element(By.XPATH, '//*[@id="datepicker_to"]')
    fecha_fin.clear()
    espera_aleatoria()
    fecha_fin.send_keys(ultima_fecha_fin_str)

    # Aplicar las fechas nuevamente
    estos_resultados = driver.find_element(By.TAG_NAME, "h1")
    estos_resultados.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pubDate_filter > div:nth-child(7) > button')))
    boton_aplicar = driver.find_element(By.CSS_SELECTOR, '#pubDate_filter > div:nth-child(7) > button')
    driver.execute_script("arguments[0].click();", boton_aplicar)
def ir_a_siguiente_pagina(max_intentos=1): # Función siguiente página

    intentos = 0
    while intentos < max_intentos:
        try:
            siguiente_boton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.next_btn')))
            siguiente_boton.click()
            espera_aleatoria(1, 2)
            return True
        except Exception as e:
            print(f"Intento {intentos + 1} fallido con CSS_SELECTOR: {e}")
        
        # Intentar con XPath
        try:
            siguiente_boton_xpath = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/main/div/article/div/div[2]/a')))
            siguiente_boton_xpath.click()
            espera_aleatoria(1, 2)
            return True
        except Exception as e:
            print(f"Intento {intentos + 1} fallido con XPath: {e}")
        
        # Intentar con la clase "next_btn"
        try:
            siguiente_boton_class = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'next_btn')))
            siguiente_boton_class.click()
            espera_aleatoria(1, 2)
            return True
        except Exception as e:
            print(f"Intento {intentos + 1} fallido con CLASS_NAME: {e}")

        # Aumentar el contador de intentos
        intentos += 1
        espera_aleatoria(1, 2)
    
    print("No se pudo avanzar a la siguiente página después de varios intentos.")
    return False
def incrementar_fecha(fecha): # FUNCIÓN INCREMENTAR FECHA
    nueva_fecha = fecha + datetime.timedelta(days=1)
    return nueva_fecha


for _ in range(360):
    driver = webdriver.Firefox(options=options)
    driver.get(f'https://www.lanacion.com.ar/buscador/?query={términos_búsqueda}')
    espera_aleatoria(1, 2)

    fecha_inicio_str = fecha_inicial.strftime("%d/%m/%Y")
    fecha_final_str = fecha_final.strftime("%d/%m/%Y")

    # Completar las fechas en el buscador PONER MAS INTENTOS ACA
    try:
        fecha_inicio = WebDriverWait(driver,20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="datepicker_from"]'))
    )
        fecha_inicio.clear()
        espera_aleatoria()
        fecha_inicio.send_keys(fecha_inicio_str)
    except Exception as e:
        print(f"No se pudo cargar día {fecha_inicial}")
        continue
               
    fecha_fin = driver.find_element(By.XPATH, '//*[@id="datepicker_to"]')
    fecha_fin.clear()
    espera_aleatoria()
    fecha_fin.send_keys(fecha_final_str)

    boton_aplicar = driver.find_element(By.CSS_SELECTOR, '#pubDate_filter > div:nth-child(7) > button:nth-child(3)')
    driver.execute_script("arguments[0].click();", boton_aplicar)

       
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Título', 'Subtítulo', 'Autor', 'Link', 'Sección', 'Fecha'])

        try:
            resultados = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#resultdata > div > div > a')))
        
            for index, resultado in enumerate(resultados):
                    link = resultado.get_attribute("href")
                    
                     
                    if "https://www.lanacion.com.ar/tecnologia/" in link:
                        print(f"Saltando link de tecnología: {link}")
                        continue  # Saltar este resultado si es de la sección tecnología

                    nueva_ventana = nueva_ventana_reintentando(link)
                    if nueva_ventana:
                        # Extraer la información de cada noticia
                        try:
                            titulo = nueva_ventana.find_element(By.TAG_NAME, 'h1').text
                            print(f"Título extraído en ventana {index + 1}: {titulo}")
                        except Exception as e:
                            titulo = None
                            print(f"Error al extraer el título en la ventana {index + 1}: {e}")

                        try:
                            subtitulo = nueva_ventana.find_element(By.XPATH, '//*[@id="content"]/div[11]/div[1]/div/div/h2').text
                            print(f"Subtíulo extraído en ventana {index + 1}: {subtitulo}")
                        except Exception as e:
                            subtitulo = None
                            print(f"Error al extraer el subtítulo en la ventana {index + 1}: {e}")

                        try:
                            autor = nueva_ventana.find_element(By.XPATH, '//*[@id="content"]/div[5]/div[1]/section/div/div[2]/div/div/div[6]/div/section/div/div/span').text
                            print(f"Autor extraído en ventana {index + 1}: {autor}")
                        except Exception as e:
                            autor = None
                            print(f"Error al extraer el autor en la ventana {index + 1}: {e}")

                        try:
                            link_actual = nueva_ventana.current_url
                            print(f"Link extraído en ventana {index + 1}: {link}")
                        except Exception as e:
                            link_actual = None
                            print(f"Error al extraer el link en la ventana {index + 1}: {e}")

                        try:
                            seccion = nueva_ventana.find_element(By.XPATH, '/html/body/div[1]/div[3]/main/div[10]/div/div/nav/a[2]').text
                            print(f"Sección extraída en ventana {index + 1}: {seccion}")
                        except Exception as e:
                            seccion = None
                            print(f"Error al extraer la sección en la ventana {index + 1}: {e}")

                        try:
                            fecha = nueva_ventana.find_element(By.XPATH, '//*[@id="content"]/div[11]/div[1]/div/div/div[2]/ul/li[1]/time').get_attribute('datetime')
                            print(f"Fecha extraída en ventana {index + 1}: {fecha}")
                        except Exception as e:
                            fecha = None
                            print(f"Error al extraer la fecha en la ventana {index + 1}: {e}")

                        # Guardar los datos en el archivo CSV
                        writer.writerow([titulo, subtitulo, autor, link_actual, seccion, fecha])

                        # Cerrar la ventana actual
                        nueva_ventana.quit()
                        espera_aleatoria(1, 3)

                # Verificar si hay una página siguiente
            if not ir_a_siguiente_pagina():
                    print("No hay más páginas, avanzando a la siguiente fecha.")
                    
           

        except Exception as e:
            # Manejo de errores
            print(f"Error al obtener resultados: {e}")
            ultima_fecha_inicio_str = fecha_inicial.strftime("%d/%m/%Y")
            ultima_fecha_fin_str = fecha_final.strftime("%d/%m/%Y")
            
            # Incrementar las fechas antes de reiniciar el navegador
            fecha_inicial = incrementar_fecha(fecha_inicial)
            fecha_final = incrementar_fecha(fecha_final)
            
            reiniciar_navegador(ultima_fecha_inicio_str, ultima_fecha_fin_str)

    fecha_inicial = incrementar_fecha(fecha_inicial)
    print(f'Fecha aumentada a {fecha_inicial}')
    fecha_final = incrementar_fecha(fecha_final)
    print(f'Fecha aumentada a {fecha_final}')
    ventanas = driver.window_handles  # Obtener todas las ventanas abiertas
    for ventana in ventanas:
         driver.switch_to.window(ventana)
         driver.close()  # Cerrar todas las ventanas abiertas, una por una
         print("Todas las ventanas cerradas. Pasando a la siguiente fecha.")
    

# Cerrar el navegador al final
driver.quit()
