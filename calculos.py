import csv
import numpy as np
import matplotlib.pyplot as plt

# Abrir y leer archivo CSV
with open('OCV(z).csv', mode = 'r' ) as read_file:

    content = csv.reader(read_file)
    cond_first = True
    soc = np.array([])
    ocv = np.array([])

    for row in content:

        if cond_first: title = row; cond_first = False; continue

        soc = np.append(soc, float(row[0]))
        ocv = np.append(ocv, float(row[1]))

    # Se almacenan ambas columnas de datos en un array multidimensional
    data = np.array([soc, ocv])

# OCV(z) 'open circuit voltage' con z desde 0.2 hasta 1
# n 'eficiencia de Coulomb'

# Implementación para retornar el OCV de cualquier SOC dado mediante interpolación lineal
def Interpolar():
    print("\nFalta implementar esta función\n")

# Clase facilita manejar múltiples celdas al tratar cada una como referencias de un objeto
class Celdas:

    # Q 'capacidad nominal' carga que se puede entregar en [Ah]
    cap_nominal = 0
    voltaje = 0
    coriente = 0
    # SOC[ z(t) ] 'state of charge', z(t) = 0 celda descargada, z(t) = 1 celda cargada
    z_soc = 0.2
    d_tiempo = 0.5

    resultados = np.array([69,420])

    def __init__(self, cap_nominal):
        self.cap_nominal = cap_nominal

    # ----------------------------------------------------------------------------------
    # IMPORTANTE, hay que guardar el SOC, SOC cargado y descargado de múltiples momentos
    # porque el profe pide que el programa pueda dar estos datos
    # ----------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------
    # IMPORTANTE, hay que guardar datos importantes para las gráficas que se piden, ej
    # los puntos de cambio en SOC, V, i, etc SIMILAR A LO DE ARRIBA ^^^^^^^^
    # ----------------------------------------------------------------------------------

    # Se definen métodos capaces de correr el proceso de carga/descarga
    def cargar(self):
        print("Falta implementar este método")

    def descargar(self):
        print("Falta implementar este método")

    def get_resultados(self):
        return self.resultados

# Correr el proceso de carga/descarga
# Intentar no agregar toda la lógica aquí si no, hacer funciones dentro de la clase Celdas ^^^^^^
celda1 = Celdas(3250)

# Implementar un menú para facilitar la revisión de resultados
while(True):
    x = input("Menú que se vea lindo:\n1. Interpolar dato ingresado\n2. Imprimir gráfica V/t\n . . .\n5. Valores de SOC inicio, fin,etc\nIngresar un número: ")
    if x == "0":
        print("Programa finalizado")
        break
    elif x == "1":
        Interpolar()
        continue
    elif x == "5":
        datos = celda1.get_resultados()
        # Ejemplo de como imprimir los resultados de la celda
        print("\nDato 1: %.2f\nDato 2: %.2f\n" % (datos[0], datos[1]))
        continue
