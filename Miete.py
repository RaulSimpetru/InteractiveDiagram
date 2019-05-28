import pandas as pd
import geocoder
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

dataRenting = 'Miete_Data.csv'

df = pd.read_csv(dataRenting, sep=";", encoding="windows-1252", index_col="Gesamtmiete")


def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i / inch for i in tupl[0])
    else:
        return tuple(i / inch for i in tupl)


def ortLatLng():
    lat = []
    lng = []
    for ort in df["Ort"].tolist():
        g = geocoder.arcgis(ort)
        while g.lat is None:
            g = geocoder.google(ort)

        lat.append(g.lat)
        lng.append(g.lng)
        print(ort, g.latlng)

    print(lat)
    df["Lat"] = pd.Series(lat).values
    df["Lng"] = pd.Series(lng).values


def Miete3Jahre():
    df = pd.read_csv(dataRenting, sep=";", encoding="windows-1252", index_col="Gesamtmiete")
    temp = []

    for nr in df.index.tolist():
        nr_temp = nr.replace(",", ".")
        temp.append(float(nr_temp) * 36)
    print(temp)
    df["Miete für 3 Jahren"] = pd.Series(temp).values
    df = df.sort_index()
    df.to_csv(dataRenting, encoding="windows-1252", sep=";")


midMiete = df["Miete fuer 3 Jahren"].median() / 36

midFlaeche = []
for value in df["Flaeche"].tolist():
    midFlaeche.append(value.replace(",", "."))

col = []

for value in df["Miete fuer 3 Jahren"].tolist():
    value = value / 36
    temp = value - midMiete
    if temp <= -25:
        col.append("g")
    elif 25 >= temp >= -25:
        col.append("lime")
    elif 75 >= temp >= 25:
        col.append("gold")
    elif 125 >= temp >= 75:
        col.append("orange")
    elif 200 >= temp >= 125:
        col.append("red")
    elif 300 >= temp >= 200:
        col.append("black")

size = []
for value in df["Flaeche"].tolist():
    points = 80.00
    value = value.replace(",", ".")
    points += (float(value) - 18.1) * 8
    size.append(round(points, 2))

lat = []
for value in df["Lat"].tolist():
    value = float(value)
    value += np.random.uniform(0, 0.00025)
    lat.append(value)

lng = []
for value in df["Lng"].tolist():
    value = float(value)
    value += np.random.uniform(0, 0.00025)
    lng.append(value)

fig = plt.figure(figsize=cm2inch(22, 22), dpi=100)

for i in range(1, len(lng)):
    label = "Wohntyp: " + df["Wohnobjekt"].tolist()[i] + "\nAdresse: " + df["Ort"].tolist()[i] + "\nName: " + str(
        df["Name"].tolist()[i]) + \
            "\nAnzahl: " + str(df["Anzahl"].tolist()[i]) + "\nFläche: " + str(
        df["Flaeche"].tolist()[i]) + " qm\nGesamtmiete: " + str(df.index.tolist()[i]) + \
            " €\nKaution: " + str(df["Kaution"].tolist()[i]) + " €\nMiete für 3 Jahren: " + str(
        df["Miete fuer 3 Jahren"].tolist()[i]) + " €"
    plt.scatter(lng[i], lat[i], c=col[i], s=size[i], marker="o", alpha=0.5, label=label)

plt.scatter(11.004670, 49.592582, c="violet", s=200, marker="X", label="Erlangen Arcaden")
plt.scatter(11.006850, 49.597317, c="violet", s=200, marker="X", label="Kollegienhaus")
plt.scatter(11.015438, 49.601690, c="violet", s=200, marker="X", label="Philosophische Fakultät")
plt.scatter(11.027492, 49.573809, c="violet", s=200, marker="X", label="Technische Fakultät")

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

datacursor(formatter='{label}'.format)

plt.show()
