import sys

import pandas as pd
import geocoder
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor


def main(args):
    if not args[1]:
        print("You must input a .csv file")
        quit()
    else:
        data_rents = str(args[1])

    special_places = []

    add_special_places = True if input("Do you want to add a special reference place? (y/n): ").lower() == 'y' else False
    # Add at least one special place in the city so you can orient yourself
    while add_special_places:
        name_special_place = input("Enter name of a special place in the city: ")
        address_special_place = input("Enter address of the special place: ")
        lng_special_place, lat_special_place = find_lng_and_lat_of_place(address_special_place)
        special_places.append([lng_special_place, lat_special_place, name_special_place])
        add_special_places = True if input("Add another place? (y/n): ").lower() == 'y' else False

    # Open the file
    df = pd.read_csv(data_rents, sep=";", encoding="utf-8", index_col="Rent")
    df.sort_index(inplace=True)

    # See if the file has the needed information
    if not pd.Series(["Area", "Name", "Address"]).isin(df.columns).all():
        print("Please make sure that you have the columns: Rent, Area, Name and Address")
        quit()

    # If there is no lng and lat in the file find them
    if not {"Lat", "Lng"}.issubset(df.columns):
        print("Finding the lat and lng of the places")
        lat_list = []
        lng_list = []
        for place in df["Address"].tolist():
            lng_temp, lat_temp = find_lng_and_lat_of_place(place)
            lat_list.append(lat_temp)
            lng_list.append(lng_temp)
        df["Lat"] = pd.Series(lat_list).values
        df["Lng"] = pd.Series(lng_list).values

    # If there is no rent for 3 years in the file calculate it
    if "Rent3Years" not in df.columns:
        print("Calculating the rent for 3 years")
        rent3years = []
        # Given that the first column of the data should be the rent we can use the index
        for rent in df.index.tolist():
            rent_temp = str(rent).replace(",", ".")  # Sometimes rent is given in the file with a ',' instead of '.'
            rent3years.append(float(rent_temp) * 36)  # 36 beacuse 3 years are 36 months (standard bachelor study time)

        df["Rent3Years"] = pd.Series(rent3years).values

    # Save the file
    print("Saving data")
    df.to_csv(data_rents,encoding="utf-8", sep=";")

    # I take the rent from the 3 years column because I already replaced ',' with '.'
    median_rent = df["Rent3Years"].median() / 36

    # Calculate the average area size
    area_list = []
    for area in df["Area"].tolist():
        area_list.append(float(str(area).replace(",", ".")))
    median_area = np.mean(area_list)

    # Assigning a color to every place based on how expensive they are relative to the average rent
    color = []
    min_rent = df["Rent3Years"].min() / 36
    max_rent = df["Rent3Years"].max() / 36
    lower_boundary = min_rent-median_rent
    upper_boundary = max_rent-median_rent
    limits = [lower_boundary + x*(upper_boundary-lower_boundary)/(6-1) for x in range(6)]
    for rent in df["Rent3Years"].tolist():
        rent = rent / 36
        relative_rent = rent - median_rent
        if relative_rent <= limits[0]:
            color.append("g")
        elif limits[1] >= relative_rent >= limits[0]:
            color.append("lime")
        elif limits[2] >= relative_rent >= limits[1]:
            color.append("gold")
        elif limits[3] >= relative_rent >= limits[2]:
            color.append("orange")
        elif limits[4] >= relative_rent >= limits[3]:
            color.append("red")
        elif limits[5] >= relative_rent >= limits[4]:
            color.append("black")

    # Assigning a size to every place based on how much bigger/smaller they are relative to the average area
    size = []
    for area_value in df["Area"].tolist():
        points = 80.00  # Chosen arbitrarily
        area_value = str(area_value).replace(",", ".")
        points += (float(area_value) - median_area) * 10  # *10 chose arbitrarily
        if points < 80.00:
            points = 80.00
        size.append(round(points, 2))

    # Move the places a tiny bit so that if they happened to have the same address or be to close to each other
    # you can still select them if you zoom in
    lat = []
    for lat_value in df["Lat"].tolist():
        lat_value = float(lat_value)
        lat_value += np.random.uniform(0, 0.000025)
        lat.append(lat_value)

    lng = []
    for lng_value in df["Lng"].tolist():
        lng_value = float(lng_value)
        lng_value += np.random.uniform(0, 0.000025)
        lng.append(lng_value)

    _ = plt.figure(figsize=cm2inch(22, 22), dpi=100)

    # Create identifiers for the places you can rent
    for i in range(0, len(lng)):
        label = "Address: " + df["Address"].tolist()[i] + "\nName: " + str(df["Name"].tolist()[i]) + "\nArea: " \
            + str(df["Area"].tolist()[i]) + " qm\nRent: " + str(df.index.tolist()[i]) + "€ (average: " \
            + str(median_rent) + " €)\nRent for 3 years: " + str(df["Rent3Years"].tolist()[i]) + " €"

        plt.scatter(lng[i], lat[i], c=color[i], s=size[i], marker="o", alpha=0.5, label=label)

    # Add the special places
    for place in special_places:
        plt.scatter(place[0], place[1], c="violet", s=200, marker="X", label=place[2])

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.tight_layout()

    datacursor(formatter='{label}'.format)

    plt.show()


def cm2inch(*tupl):
    """Calculates cm in inches"""
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i / inch for i in tupl[0])
    else:
        return tuple(i / inch for i in tupl)


def find_lng_and_lat_of_place(address):
    """Returns longitude and latitude of an address"""
    g = geocoder.arcgis(address)
    while g.lat is None:
        g = geocoder.google(address)
    return g.lng, g.lat


if __name__ == '__main__':
    main(sys.argv)
