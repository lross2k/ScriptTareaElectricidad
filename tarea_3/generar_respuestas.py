import csv
import matplotlib.pyplot as plt
import numpy as np

# función usada para redondear valores reales a 3 decimales
def redondear(func):
    func = "%.3f" % func
    return func

# función encargada de calcular A, B, ..., H, I y retornar un array para el CSV
def valores(t_x):
    # constantes
    A = -20
    B = -2
    C = -30
    E = -5
    G = 4
    # dependientes de t_x
    D = (-20 * np.exp( -2 * (t_x + 0.5) ) + 30 ) * np.exp( 2 * (t_x + 0.5 ) )
    F = (-30 + (-20 * np.exp( -2 * (t_x + 0.5) ) + 30 ) * np.exp( -2 ) + 5) * np.exp( 2 * (t_x + 1.5) ) 
    H = H = -2 * 0.1 * D
    I = I = -2 * 0.1 * F
    t_x = "%0.1f" % t_x
    return [t_x, A, B, C, redondear(D), E, redondear(F), G, redondear(H), redondear(I)]

# generar archivo CSV e introducir los datos para cada t_x
with open("valores.csv", 'w', newline = '') as archivo:
    escribir = csv.writer(archivo)
    escribir.writerow(['tx','A','B','C','D','E','F','G','H','I'])
    for t_x in np.arange(0.1,1.1,0.1):
        escribir.writerow( valores(t_x) )

# gráficas
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
t = np.arange(0, 4.5, 1e-1)

# nombres para leyenda
def nombres(t_x):
    nombre = "$t_x$ = %0.1fs" % t_x
    return nombre

# gráfica de voltaje
for t_x in np.arange(0.1,1.1,0.1):
    v_t = (t < (t_x + 0.5)) * -20 * np.exp( -2 * t ) + (t >= (t_x + 0.5)) * (t < (t_x + 1.5)) * (-30 + (-20 * np.exp( -2 *(t_x + 0.5) ) + 30 ) * np.exp( -2 * ( t - t_x - 0.5 ) )  ) + (t >= (t_x + 1.5)) * ( -5 + ( -30 + (-20 * np.exp( -2 * (t_x + 0.5) -2 ) +30 * np.exp(-2) +5 )) * np.exp( 2* (t_x + 1.5)) * np.exp( - 2 * t) ) 
    ax1.plot(t,v_t,label = nombres(t_x))
ax1.set_ylabel('$V_C$ (V)')

# gráfica de corriente
for t_x in np.arange(0.1,1.1,0.1):
    i_t = (t < (t_x + 0.5)) * 4 * np.exp(-2 * t) + (t >= (t_x + 0.5)) * (t < (t_x + 1.5)) * -2 * 0.1 * (-20 * np.exp( -2 *(t_x + 0.5) ) + 30 ) * np.exp( -2 * t ) * np.exp( -2 * (- t_x - 0.5) ) + (t >= (t_x + 1.5)) * -2 * 0.1 * ( -5 + ( -30 + (-20 * np.exp( -2 * (t_x + 0.5) -2 ) +30 * np.exp(-2) +5 )) * np.exp( 2* (t_x + 1.5)) * np.exp( - 2 * t) )
    ax2.plot(t,i_t)
ax2.set_ylabel('$i_C$ (mA)')

# dar formato a los subplots
fig.legend(bbox_to_anchor=(0.17, 0.002, 0.7, 0.98),loc='upper left', fontsize = 'xx-small', ncol=5, mode="expand", borderaxespad=0.)
plt.xlabel('Tiempo (s)')
plt.savefig('graf.png')
plt.show()
