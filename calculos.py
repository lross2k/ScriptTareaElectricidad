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
    socs = np.array([])
    corrientes = np.array([])

    # Constructor define algunos datos constantes
    def __init__(self):
        self.cap_nominal = 3250
        self.resistor = 0.0001
        self.z_soc = 0.2
        self.d_tiempo = 1
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

    def cap(self, n):
        return (self.corriente * n * (0.5/ 3600)) / (soc[ int(self.k) ] - soc[ int(self.k - 1) ])

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

                # Almacenar los datos de cada iteración
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total)
                self.corrientes = np.append(self.corrientes, self.corriente)
                self.socs = np.append(self.socs, self.z_soc)

                self.k += self.d_tiempo
                self.k_total += 1
            self.k = int(self.k - self.d_tiempo)
            #self.cap_nominal = self.cap(self.nc)   ############
        else:
            while (self.corriente > limite):
                corriente = self.corr(limite)
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.k -= self.d_tiempo
                self.k_total += 1
                
                # Almacenar los datos de cada iteración
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total)
                self.corrientes = np.append(self.corrientes, self.corriente)
                self.socs = np.append(self.socs, self.z_soc)

                if corriente < limite:
                    break
                else:
                    self.corriente = corriente
            self.k += self.d_tiempo

    def descargar(self, limite, const, tasa_c):
        if const == "CC":
            self.corriente = self.cap_nominal * tasa_c
            # Se detiene con v(t) == 3.2 porque ocv no llega más abajo
            while (True):
                self.z_soc = soc[int(self.k)]
                if interpolar(self.z_soc) != self.ocv_de_z:
                    self.ocv_de_z = interpolar(self.z_soc)
                self.voltaje = self.volt()
                
                # Almacenar los datos de cada iteración
                self.voltajes = np.append(self.voltajes, self.voltaje)
                self.tiempos = np.append(self.tiempos, self.k_total)
                self.corrientes = np.append(self.corrientes, self.corriente)
                self.socs = np.append(self.socs, self.z_soc)

                self.k -= self.d_tiempo
                self.k_total += 1
                if self.voltaje <= limite: break
            self.k = int(self.k + self.d_tiempo)
        # Celda se descarga a 1C hasta que V(t) = 3.2V, n = nd
        #n = self.nd  ##########

    def get_resultados(self):
        # Retorna voltajes, k's, corrientes, socs
        return np.array([self.voltajes, self.tiempos, self.corrientes, self.socs])

# Correr el proceso de carga/descarga
celda1 = Celdas()
celda1.cargar(4.2, "CC", 0.5)
celda1.cargar(500, "CV", 0)
celda1.descargar(3.2, "CC", 1)

# Implementar un menú para facilitar la revisión de resultados
while(True):
    x = input("\nMenú que se vea lindo:\n0. Terminar programa\n1. Interpolar dato ingresado\n2. Gráfica Voltaje/t\n3. Gráfica Corriente/t\n4. Gráfica SOC/t\n5. Valores de SOC inicio, fin,etc\nIngresar un número:\n>> ")
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
        # Grafica V/t
        # Retorna voltajes, k's, corrientes, socs
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[0]
        plt.ylabel('Voltaje (V)')
        plt.xlabel('Tiempo (k)')
        plt.step(x, y) # , label = 'awebo'
        plt.grid(axis='x', color='0.95')
        plt.title('Gráfica de Voltaje en función del tiempo')
        plt.show()
        continue
    elif x=="3":
        # Grafica i/t
        # Retorna voltajes, k's, corrientes, socs
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[2]
        plt.ylabel('Corriente (mA)')
        plt.xlabel('Tiempo (k)')
        plt.step(x, y) # , label = 'awebo'
        plt.grid(axis='x', color='0.95')
        plt.title('Gráfica de Corriente en función del tiempo')
        plt.show()
        continue
    elif x=="4":
        # Grafica z/t
        # Retorna voltajes, k's, corrientes, socs
        datos = celda1.get_resultados()
        x = datos[1]
        y = datos[3]
        plt.ylabel('SOC (?)')
        plt.xlabel('Tiempo (k)')
        plt.step(x, y) # , label = 'awebo'
        plt.grid(axis='x', color='0.95')
        plt.title('Gráfica del SOC en función al tiempo')
        plt.show()
        continue
    elif x == "5":
        #datos = celda1.get_resultados()
        # Ejemplo de como imprimir los resultados de la celda
        #print("\nDato 1: %.2f\nDato 2: %.2f\n" % (datos[0], datos[1]))
        print("Falta implementar esta función")
