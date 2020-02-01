#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
from shapely.geometry import Polygon
from lxml import etree
import markup3dmodule

# TODO osetrit fce
# TODO citovat pouzite casti skriptu
# --------------------------------------------------------------#
# dictionaries
roof_types = {}
num_storeys = {}
body_volume = {}
roof_volume = {}
building_volume = {}
building_height = {}
roof_height = {}
body_height = {}


# --------------------------------------------------------------#
# funcions

def remove_duplicate(duplicate_list):
    """Removes duplicates values in the input list"""
    final_list = []
    for num in duplicate_list:
        if num not in final_list:
            final_list.append(num)
    return final_list


def hight_of_object(coords):
    """Finding the high of the imput object and return it, return max z coordinates of object also"""
    zcoords_duplicate = []
    zcoords = []
    for i in coords:
        for c in i:
            zcoords_duplicate.append(c[2])
            zcoords = remove_duplicate(zcoords_duplicate)

    zcoords.sort()
    c = abs(zcoords[1] - zcoords[0])
    coords_max = zcoords[-1]
    return c, coords_max


def create_edges_from_list_of_connection(connection):
    edges = []
    for i in connection:

        for i[0] in i:
            for a in i:
                if i[0] != a:
                    pks = []
                    pks.append(i[0])
                    pks.append(a)
                    edges.append(pks)

    return (edges)


# --------------------------------------------------------------#
# IN OOP
def parameters_of_footprint(footprintcoords):
    """In the list of lists of foodprint coordinates return side a,b and its area"""
    # TODO ohlidat aby souradnice obsahovaly pouze hodnoty obdelniku, aby byli na vstupu v souradnicich duplicitni hodnoty - zaokrouhlovani
    # TODO z souřadnice
    # TODO osetrit ze x a y podstavy jsou rovnobezne s coord systemem, prozatim mam strany rovnobezne se sourad. systemem

    xcoords_duplicate = []
    for i in footprintcoords:
        xcoords_duplicate.append(i[0])
    xcoords = remove_duplicate(xcoords_duplicate)

    ycoords_duplicate = []
    for i in footprintcoords:
        ycoords_duplicate.append(i[1])
    ycoords = remove_duplicate(ycoords_duplicate)

    if len(xcoords) == 2 & len(ycoords) == 2:
        a = abs(xcoords[0] - xcoords[1])
        b = abs(ycoords[0] - ycoords[1])
        area = a * b
    elif 2 < len(xcoords) <= 4 or 2 < len(ycoords) <= 4:
        a1 = abs(xcoords[0] - xcoords[1])
        a2 = abs(xcoords[1] - xcoords[2])
        b1 = abs(ycoords[0] - ycoords[1])
        b2 = abs(ycoords[1] - ycoords[2])
        a = math.sqrt((a1 * a1) + (b1 * b1))
        b = math.sqrt((a2 * a2) + (b2 * b2))
        area = a * b
    else:
        print "Polygon contain more than 4 vertices, not valid"
        # TODO jak to zakoncit
        a = 0
        b = 0
        area = 0

    zcoords_duplicate = []
    for i in footprintcoords:
        zcoords_duplicate.append(i[2])
    zcoords = remove_duplicate(zcoords_duplicate)
    z = zcoords[0]
    return a, b, z, area


# par= parameters_of_foodprint(e)
# print par


def bodyvolume(wallcoords, footprintcoords):
    """Return a volume of body building"""
    c, coords_max = hight_of_object(wallcoords)
    a, b, z, area = parameters_of_footprint(footprintcoords)
    volume = a * b * c
    return volume


# roofvolume = 0
# rooftype = ['gabled']


def roofvolume(footprintcoords, rooftype, roofcoords):
    """Return a volume of the roof"""
    roofvolume = []
    list_coords = []
    roof_up = []
    roof_down = []
    c = 0
    for roof in rooftype:
        if roof == "Flat":
            roofvolume = 0
            c = 0
        elif roof == 'Shed' or 'Gabled':
            c, coords_max = hight_of_object(roofcoords)
            a, b, z, area = parameters_of_footprint(footprintcoords)
            roofvolume = (a * b * c) / 2
        elif roof == "Pyramidal":
            c, coords_max = hight_of_object(roofcoords)
            a, b, z, area = parameters_of_footprint(footprintcoords)
            roofvolume = (a * b * c) / 3
        elif roof == "Hipped":
            c, coords_max = hight_of_object(roofcoords)
            a, b, z, area = parameters_of_footprint(footprintcoords)
            for i in roofcoords:
                if len(i) == 4:
                    list_coords.append(i[0])
            if b in list_coords:
                if b[2] == coords_max:
                    roof_up.append(b)
                else:
                    roof_down.append(b)  # nedavala jsem i

            au = abs(roof_up[0][0] - roof_up[1][0])
            bu = abs(roof_up[0][1] - roof_up[1][1])
            a_smaller = math.sqrt((au * au) + (bu * bu))

            ad = abs(roof_down[0][0] - roof_down[1][0])
            bd = abs(roof_down[0][1] - roof_down[1][1])
            a_longer = math.sqrt((ad * ad) + (bd * bd))

            if not a_longer == a:
                b = a
                a = a_longer
            print a, b
            num = (2 * a + a_smaller)
            roofvolume = (1 / 6) * b * c * num

        else:
            print "unnamed roof type"
    return roofvolume, c


def allvolume(roofvolume, bodyvolume):
    """Return a volume of all building"""
    roofvolume, c = roofvolume(footprintcoords, rooftype, roofcoords)
    bodyvolume = bodyvolume(wallcoords, footprintcoords)
    return roofvolume + bodyvolume


def neighbour_buildings(footprintcoords, anotherbuild):
    """Try to find neighbours buildings and return their ID"""
    building_ID = []
    neighbours_ID = []
    for i in anotherbuild:
        building_ID = i[0][0]
        coord_build = i[1]

        a, b, z, area = parameters_of_footprint(footprintcoords)
        bv = (a + b) / 5
        ma = (a * b) / 1.5
        # print bv

        poly1 = Polygon(footprintcoords)
        poly2 = Polygon(coord_build)

        buffer_value = 0.5
        minimum_area = 1
        p1 = poly1.buffer(buffer_value)
        p2 = poly2.buffer(buffer_value)

        validate = p1.intersection(p2).area
        # print "val:",validate
        if validate > minimum_area:
            neighbours_ID.append(building_ID)
    return neighbours_ID


# --------------------------------------------------------------#
# importing xml files
# -- Name spaces
ns_citygml = "http://www.opengis.net/citygml/2.0"

ns_gml = "http://www.opengis.net/gml"
ns_bldg = "http://www.opengis.net/citygml/building/2.0"
ns_tran = "http://www.opengis.net/citygml/transportation/2.0"
ns_veg = "http://www.opengis.net/citygml/vegetation/2.0"
ns_gen = "http://www.opengis.net/citygml/generics/2.0"
ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
ns_xlink = "http://www.w3.org/1999/xlink"
ns_dem = "http://www.opengis.net/citygml/relief/2.0"
ns_frn = "http://www.opengis.net/citygml/cityfurniture/2.0"
ns_tun = "http://www.opengis.net/citygml/tunnel/2.0"
ns_wtr = "http://www.opengis.net/citygml/waterbody/2.0"
ns_brid = "http://www.opengis.net/citygml/bridge/2.0"
ns_app = "http://www.opengis.net/citygml/appearance/2.0"

nsmap = {
    None: ns_citygml,
    'gml': ns_gml,
    'bldg': ns_bldg,
    'tran': ns_tran,
    'veg': ns_veg,
    'gen': ns_gen,
    'xsi': ns_xsi,
    'xAL': ns_xAL,
    'xlink': ns_xlink,
    'dem': ns_dem,
    'frn': ns_frn,
    'tun': ns_tun,
    'brid': ns_brid,
    'app': ns_app
}
# calling xml
FULLPATH = "D:\Dokumenty\Diplomka\GML_OBJ\soubory\export_dogml_pokus22.xml"

CITYGML = etree.parse(FULLPATH)
root = CITYGML.getroot()
cityObjects = []
buildings = []

# -- Find all instances of cityObjectMember and put them in a list
for obj in root.getiterator('{%s}cityObjectMember' % ns_citygml):
    cityObjects.append(obj)

print "\tThere are", len(cityObjects), "cityObject(s) in this CityGML file"
# find only Building

for cityObject in cityObjects:
    for child in cityObject.getchildren():
        if child.tag == '{%s}Building' % ns_bldg:
            buildings.append(child)

    # -- Store the buildings as classes
FILENAME = 'export_dogml_pokus22_BD'

# create list with footprint and ID of building
anotherbuilding = []
for b in buildings:
    # establish variables
    anotherbuilding_pre = []
    footprintcoords1 = []
    ids = []
    id = b.attrib['{%s}id' % ns_gml]
    ids.append(id)
    ground_walls1 = []

    if any(FILENAME in s for s in ids):
        break

    for child in b.getiterator():
        if child.tag == '{%s}GroundSurface' % ns_bldg:
            ground_walls1.append(child)

    for surface in ground_walls1:
        for w in surface.findall('.//{%s}Polygon' % ns_gml):
            a = markup3dmodule.GMLpoints(w)
            footprintcoords1 = a

    anotherbuilding_pre.append(ids)
    anotherbuilding_pre.append(footprintcoords1)
    anotherbuilding.append(anotherbuilding_pre)

bld_nb = []
# finding parameters of building
for b in buildings:
    ground_walls = []
    walls = []
    roof_walls = []
    footprintcoords = []
    wallcoords = []
    roofcoords = []
    ids = []
    rooftype = []
    storeys = []
    id = b.attrib['{%s}id' % ns_gml]
    ids.append(id)

    if any(FILENAME in s for s in ids):
        break

    # finding and sorting surfaces
    for child in b.getiterator():
        if child.tag == '{%s}GroundSurface' % ns_bldg:
            ground_walls.append(child)
        elif child.tag == '{%s}WallSurface' % ns_bldg:
            walls.append(child)
        elif child.tag == '{%s}RoofSurface' % ns_bldg:
            roof_walls.append(child)
        elif child.tag == '{%s}roofType' % ns_bldg:
            rooftype.append(child.text)
        elif child.tag == '{%s}storeysAboveGround' % ns_bldg:
            storeys.append(child.text)

    # finding polygon and his coords

    for surface in ground_walls:
        for w in surface.findall('.//{%s}Polygon' % ns_gml):
            a = markup3dmodule.GMLpoints(w)
            footprintcoords = a

    for surface in walls:
        for w in surface.findall('.//{%s}Polygon' % ns_gml):
            a = markup3dmodule.GMLpoints(w)
            wallcoords.append(a)

    for surface in roof_walls:
        for w in surface.findall('.//{%s}Polygon' % ns_gml):
            a = markup3dmodule.GMLpoints(w)
            roofcoords.append(a)

    # call functions
    clear_nb = []
    bv = str()
    bv = bodyvolume(wallcoords, footprintcoords)
    av = allvolume(roofvolume, bodyvolume)
    a, b, z, area = parameters_of_footprint(footprintcoords)
    rv, hr = roofvolume(footprintcoords, rooftype, roofcoords)
    nb = neighbour_buildings(footprintcoords, anotherbuilding)
    hb, cw_max = hight_of_object(wallcoords)
    # hr,cr_max=hight_of_object(roofcoords)
    h_all = hb + hr

    # bld_nb.append(nb)
    # cleaning ID of selected building from list of the neigbour buildings
    for som in nb:
        if som != id:
            clear_nb.append(som)

    print ids
    print rooftype
    print footprintcoords
    print wallcoords
    print roofcoords
    print a, b, z, area
    print bv
    print rv
    print av
    print clear_nb
    print h_all
    print storeys
    bld_nb2 = []
    bld_nb2.append(ids[0])
    for jop in clear_nb:
        bld_nb2.append(jop)
    bld_nb.append(bld_nb2)

    roof_types[ids[0]] = rooftype[0]  # zkontrolovat jestli opravdu pouzivat IDs nebo jen ID
    num_storeys[ids[0]] = storeys[0]
    body_volume[ids[0]] = bv
    roof_volume[ids[0]] = rv
    building_volume[ids[0]] = av
    building_height[ids[0]] = hb
    roof_height[ids[0]] = hr
    body_height[ids[0]] = h_all

print "bld_nb=", bld_nb
print "roof_types=", roof_types
print "num_storeys=", num_storeys
print "body_volume=", body_volume
print "roof_volume=", roof_volume
print "building_volume=", building_volume
print "building_height=", building_height
print "roof_height=", roof_height
print "body_height=", body_height
print "edges=", create_edges_from_list_of_connection(bld_nb)
