import pickle
from pprint import pprint

f = open('USA Map with annotations.svg', 'r')

inStations = False
stationLocations = {}

for l in f:
   # viewBox="0 0 1052.3622 744.09448"

    if l.find('viewBox=') != -1:
        i = l.find('viewBox=') + 9
        j = l[i:].find('"') + i
        nums = l[i:j]
        k = 0
        dims = []
        while k < 4:
            if k >= 2:
                dims.append(float(nums[0:nums.find(' ')]))
            nums = nums[nums.find(' ')+1:]
            k += 1

    elif l.find('label="Stations"') != -1:
        inStations = True

    elif inStations and l.find('</g>') != -1:
        inStations = False

    elif inStations:
        if l.find('translate') != -1:
            transform="translate(0,-61.094493)"
            i = l.find('translate(') + 10
            j = i + l[i:].find(',')
            k = j + l[j:].find(')')
            translate_x = float(l[i:j])/dims[0]
            translate_y = float(l[j+1:k])/dims[1]

        if l.find('<circle') != -1:
            name = ''
            cx = 0
            cy = 0

        elif l.find('</circle>') != -1:
            radius = (rx, ry)
            stationLocations[name] = (cx - translate_x, cy - translate_y)

        elif l.find('cx=') != -1:
            i = l.find('cx=') + 4
            j = i + l[i:].find('"')
            cx = float(l[i:j])/dims[0]

        elif l.find('cy=') != -1:
            i = l.find('cy=') + 4
            j = i + l[i:].find('"')
            cy = 1 - float(l[i:j])/dims[1]

        elif l.find('Station:') != -1:
            i = l.find('Station:') + 8
            j = l.find('</title>')
            name = l[i:j]

        elif l.find('r=') != -1:
            i = l.find('r=') + 3
            j = i + l[i:].find('"')
            rx = float(l[i:j])/dims[0]
            ry = float(l[i:j])/dims[1]

pprint(stationLocations)
print('radius = ', radius)
print('translate = ', translate_x, translate_y)

f.close()

with open('stationLocations.dictionary', 'wb') as stations_dictionary_file:
    pickle.dump(stationLocations, stations_dictionary_file)
