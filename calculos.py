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
def interpolar(z):
    if z in soc:
        return ocv[ np.where( soc == z )[0][0] ]
    else:
        # Implementación de algoritmo para optimizar la búsqueda de x_0 y x_1
        if len(soc) >= 2:
            i = int(len(soc) / 2) - 1
        while(True):
            if soc[i] < z and soc[i + 1] > z or soc[i - 1] < z and soc[i] > z:
                # Se almacenan x_0, x_1, y_0, y_1 en orden correcto
                if soc[i] < z:
                    x_0 = soc[i]
                    y_0 = ocv[i]
                    x_1 = soc[i + 1]
                    y_1 = ocv[i + 1]
                else:
                    x_0 = soc[i - 1]
                    y_0 = ocv[i - 1]
                    x_1 = soc[i]
                    y_1 = ocv[i]
                break
            elif soc[i] > z and soc[i - 1] > z:
                i = int(i / 2)
                continue
            else:
                if i * 1.5 < len( soc ):
                    if soc[ int(i * 1.5) ] < z and int(i * 1.05) != i:
                        i = int (i * 1.5)
                    elif soc[ int( i * 1.25 ) ] < z and int(i * 1.05) != i:
                        i = int (i * 1.25)
                    elif soc[ int( i * 1.05 ) ] < z and int(i * 1.05) != i:
                        i = int (i * 1.05)
                    else:
                        i += 1
                else:
                    i += 1
                continue
        # Retornar valor interpolado
        return ( y_0 + (z - x_0) * (y_1 - y_0) / (x_1 - x_0) )

# Clase facilita manejar múltiples celdas al tratar cada una como referencias de un objeto
class Celdas:
    
    # Inicializar varibles
    cap_nominal = 0
    voltaje = 0
    corriente = 0
    ocv_de_z = 0
    z_soc = 0
    d_tiempo = 0
    resistor = 0
    nc = 0
    nd = 0
    k_total = 0
    k = 0

    voltajes = np.array([])
    tiempos = np.array([])

    # Constructor define algunos datos constantes
    def __init__(self):
        self.cap_nominal = 3250
        self.resistor = 0.0001
        self.z_soc = 0.2
        self.d_tiempo = 1 #0.5
        self.nc = 0.99
        self.nd = 1
        self.k = 1

    def volt(self):
        return(self.ocv_de_z - self.resistor * self.corriente)

    def corr(self, limite):
        #return(soc[self.k - 1] - soc[self.k]) * (self.cap_nominal / (n * self.d_tiempo))
        a = self.ocv_de_z - self.voltaje
        b = a / self.resistor
        b = float('%.4f'%(b))
        return(b)   

    # ----------------------------------------------------------------------------------
    # IMPORTANTE, hay que guardar el SOC, SOC cargado y descargado de múltiples momentos
    # porque el profe pide que el programa pueda dar estos datos
    # ----------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------
    # IMPORTANTE, hay que guardar datos importantes para las gráficas que se piden, ej
    # los puntos de cambio en SOC, V, i, etc SIMILAR A LO DE ARRIBA ^^^^^^^^
    # ----------------------------------------------------------------------------------

    # Se definen métodos capaces de correr el proceso de carga/descarga
    def cargar(self, limite, const, tasa_c):
        if const == "CC":
            self.corriente = self.cap_nominal * tasa_c
            # Se detiene con ocv == 4.2 porque V(t) no llega a 4.2
            while (self.ocv_de_z < limite):
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.voltaje = self.volt()
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total)
                self.k += self.d_tiempo
                self.k_total += 1
            self.k -= self.d_tiempo
            print("OCV fin de primer periodo")
            print(self.ocv_de_z) # Para pruebas
        else:
            while (self.corriente > limite):
                corriente = self.corr(limite)
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.k -= self.d_tiempo
                self.k_total += 1
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total)
                if corriente < limite:
                    break
                else:
                    self.corriente = corriente
            self.k += self.d_tiempo
            print("Corriente fin de segundo periodo:")
            print(self.corriente) # Para pruebas
            print("K total")
            print(self.k_total) # Más pruebas

    def descargar(self):
        print("Falta implementar este método")

    def get_resultados(self):
        return np.array([self.voltajes, self.tiempos])

# Correr el proceso de carga/descarga
# Intentar no agregar toda la lógica aquí si no, hacer funciones dentro de la clase Celdas ^^^^^^
celda1 = Celdas()
celda1.cargar(4.2, "CC", 0.5)
celda1.cargar(500, "CV", 0)

# Implementar un menú para facilitar la revisión de resultados
while(True):
    x = input("\nMenú que se vea lindo:\n0. Terminar programa\n1. Interpolar dato ingresado\n2. Imprimir gráfica V/t\n . . .\n5. Valores de SOC inicio, fin,etc\nIngresar un número:\n>> ")
    print("")
    if x == "0":
        print("Programa finalizado")
        break
    elif x == "1":
        while(True):
            try:
                num = float( input("Ingresar valor de z entre 0.2 y 1:\n>> ") )
                num =  float( '%.4f'%(num) )
                if num >= 0.2 and num <= 1:
                    print(interpolar(num))
                    break
                else:
                    print("Por favor ingresar un número dentro del rango especificado")
                continue
            except ValueError:
                print("Por favor sólo ingresar números")
    elif x=="2":
        print("Llamar grafica de Mathplotlib")
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[0]
        plt.step(x, y, label = 'awebo')
        plt.plot(x, y)
        plt.grid(axis='x', color='0.95')
        plt.legend(title='Parameter where:')
        plt.title('plt.step(where=...)')
        plt.show()
        continue
    elif x == "5":
        datos = celda1.get_resultados()
        # Ejemplo de como imprimir los resultados de la celda
        print("\nDato 1: %.2f\nDato 2: %.2f\n" % (datos[0], datos[1]))
        continue
