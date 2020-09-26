import csv
import numpy as np
import matplotlib.pyplot as plt
#1
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

    data = np.array([soc, ocv])
