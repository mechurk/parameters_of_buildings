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
roof_types_number = {}
num_storeys = {}
body_volume = {}
roof_volume = {}
building_volume = {}
building_height = {}
roof_height = {}
body_height = {}
roof_orientation = {}
roof_volume_constant = {}
building_ids=[]
footprints={}
z_footprints={}
z_max_body={}
z_max_roof={}

# --------------------------------------------------------------#
# funcions

def remove_duplicate(duplicate_list):
    """Removes duplicates values in the input list"""
    # in list of lists removing duplicate list include
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
    # if there is 3 variables in list find first one (because gabled roof have wall up to roof)[-1]
    # but we need coord [1]
    coords_max = zcoords[1]  # return max z coords
    return c, coords_max


def create_edges_from_list_of_connection(connection):
    edges = []
    for i in connection:

        for i[0] in i:
            for a in i:
                if i[0] != a:
                    # pks = []
                    pks = (i[0], a)

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


def roof_volumes(footprintcoords, rooftype, roofcoords):
    """Return a volume of the roof"""
    roofvolume = 0
    list_coords = []
    roof_up = []
    roof_down = []
    list_coords_dupl = []
    c = 0
    coords_max=0
    # for roof in rooftype:
    if rooftype[0] == "Flat":
        roofvolume = 0
        c = 0
        coords_max =0
    elif rooftype[0] == 'Shed':
        c, coords_max = hight_of_object(roofcoords)
        a, b, z, area = parameters_of_footprint(footprintcoords)
        roofvolume = (a * b * c) / 2
    elif rooftype[0] == 'Gabled':
        c, coords_max = hight_of_object(roofcoords)
        a, b, z, area = parameters_of_footprint(footprintcoords)
        roofvolume = (a * b * c) / 2
    elif rooftype[0] == "Pyramidal":
        c, coords_max = hight_of_object(roofcoords)
        a, b, z, area = parameters_of_footprint(footprintcoords)
        print a, b, z, area
        roofvolume = (a * b * c) / 3
    elif rooftype[0] == "Hipped":
        c, coords_max = hight_of_object(roofcoords)
        a, b, z, area = parameters_of_footprint(footprintcoords)
        for i in roofcoords:
            if len(i) == 5:
                list_coords_dupl = i
        for k in list_coords_dupl:
            if k not in list_coords:
                list_coords.append(k)
        for u in list_coords:
            if u[2] == coords_max:
                roof_up.append(u)
            else:
                roof_down.append(u)  # nedavala jsem i

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
        roofvolume = (b * c * num) / 6

    else:
        print "unnamed roof type"
    return roofvolume, c,coords_max


def allvolume(roofvolume, bodyvolume):
    """Return a volume of all building"""
    roofvolume, c,coord_max = roofvolume(footprintcoords, rooftype, roofcoords)
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


def rooforientation(footprintcoords, rooftype, roofcoords):
    # Return a volume of the roof
    roof_orientation = 0
    max_edge = []
    parallel_edge = []
    list_coords = []
    roof_up = []
    roof_down = []
    c = 0

    if rooftype[0] == "Flat":
        roof_orientation = 0

    elif rooftype[0] == 'Shed':
        c, coords_max = hight_of_object(roofcoords)
        one_roof_polygon_duplicate = roofcoords[
            0]  # expect that gabled roof have only two shape with same max roof line
        one_roof_polygon = remove_duplicate(one_roof_polygon_duplicate)  # clear duplicates
        for vertex in one_roof_polygon:
            if vertex[2] == coords_max:
                max_edge.append(vertex)
            else:
                parallel_edge.append(vertex)
        difference_x = abs(max_edge[0][0] - max_edge[1][0])
        difference_y = abs(max_edge[0][1] - max_edge[1][1])

        if difference_x == 0 and difference_y != 0:
            difference_parallel_x = parallel_edge[0][0] - max_edge[0][0]  # lower edge-higher edge
            if difference_parallel_x < 0:
                roof_orientation = 90
            elif difference_parallel_x > 0:
                roof_orientation = 270
            else:
                roof_orientation = 999
        elif difference_x != 0 and difference_y == 0:
            difference_parallel_x = parallel_edge[0][1] - max_edge[0][1]  # lower edge-higher edge
            if difference_parallel_x < 0:
                roof_orientation = 180
            elif difference_parallel_x > 0:
                roof_orientation = 0
            else:
                roof_orientation = 999
        else:
            roof_orientation = 9999


    elif rooftype[0] == 'Gabled':
        c, coords_max = hight_of_object(roofcoords)
        one_roof_polygon_duplicate = roofcoords[
            0]  # expect that gabled roof have only two shape with same max roof line
        one_roof_polygon = remove_duplicate(one_roof_polygon_duplicate)  # clear duplicates
        for vertex in one_roof_polygon:
            if vertex[2] == coords_max:
                max_edge.append(vertex)
        difference_x = abs(max_edge[0][0] - max_edge[1][0])
        difference_y = abs(max_edge[0][1] - max_edge[1][1])

        if difference_x == 0 and difference_y != 0:
            roof_orientation = 90
        elif difference_x != 0 and difference_y == 0:
            roof_orientation = 0
        else:
            roof_orientation = 9999


    elif rooftype[0] == "Pyramidal":
        roof_orientation = 0

    elif rooftype[0] == "Hipped":
        c, coords_max = hight_of_object(roofcoords)
        for sublist in roofcoords:
            if len(sublist) == 5:
                one_roof_polygon_duplicate = sublist
        one_roof_polygon = remove_duplicate(one_roof_polygon_duplicate)  # clear duplicates
        for vertex in one_roof_polygon:
            if vertex[2] == coords_max:
                max_edge.append(vertex)
        difference_x = abs(max_edge[0][0] - max_edge[1][0])
        difference_y = abs(max_edge[0][1] - max_edge[1][1])

        if difference_x == 0 and difference_y != 0:
            roof_orientation = 90
        elif difference_x != 0 and difference_y == 0:
            roof_orientation = 0
        else:
            roof_orientation = 9999


    else:
        print "unnamed roof type"

    return roof_orientation

def roof_types_num(rooftype ):
    """Return a volume of the roof"""
    roofvolume = 0

    # for roof in rooftype:
    if rooftype[0] == "Flat":
        roof_type_number = 2
    elif rooftype[0] == 'Shed':
        roof_type_number = 3
    elif rooftype[0] == 'Gabled':
        roof_type_number = 4
    elif rooftype[0] == "Pyramidal":
        roof_type_number = 1
    elif rooftype[0] == "Hipped":
        roof_type_number = 5

    else:
        print "unnamed roof type"
    return roof_type_number
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
FULLPATH = "D:\Dokumenty\Diplomka\GML_OBJ\soubory\jeden_blok_2_pks.xml"

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
print anotherbuilding
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

    bv = bodyvolume(wallcoords, footprintcoords)
    av = allvolume(roof_volumes, bodyvolume)
    a, b, z, area = parameters_of_footprint(footprintcoords)
    rv, hr,roof_coords_max = roof_volumes(footprintcoords, rooftype, roofcoords)
    nb = neighbour_buildings(footprintcoords, anotherbuilding)
    hb, cw_max = hight_of_object(wallcoords)
    # hr,cr_max=hight_of_object(roofcoords)
    h_all = hb + hr
    rfo = rooforientation(footprintcoords, rooftype, roofcoords)
    rtn=roof_types_num(rooftype)

    if rv != 0 and hr != 0:
        rvc = rv / hr
    else:
        rvc = 0

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
    print hb
    print hr
    print h_all
    print storeys
    print rfo
    print rvc

    bld_nb2 = []
    bld_nb2.append(ids[0])
    for jop in clear_nb:
        bld_nb2.append(jop)
    bld_nb.append(bld_nb2)

    building_ids.append (ids[0])

    roof_types[ids[0]] = rooftype[0]  # zkontrolovat jestli opravdu pouzivat IDs nebo jen ID
    num_storeys[ids[0]] = storeys[0]
    body_volume[ids[0]] = bv
    roof_volume[ids[0]] = rv
    building_volume[ids[0]] = av
    building_height[ids[0]] = hb
    roof_height[ids[0]] = hr
    body_height[ids[0]] = h_all
    roof_orientation[ids[0]] = rfo
    roof_volume_constant[ids[0]] = rvc
    roof_types_number[ids[0]] = rtn
    footprints[ids[0]]=area
    z_footprints[ids[0]] = z
    z_max_body[ids[0]] = cw_max
    z_max_roof[ids[0]] = roof_coords_max

print "building_ids=", building_ids
print "heights=", body_height
print "footprints=",footprints
print "edges=", create_edges_from_list_of_connection(bld_nb)
print "roof_types=",roof_types_number
print "roof_heights=", roof_height
print "roof_volume_constant=", roof_volume_constant
print "roof_orientation=", roof_orientation
print ""

print "bld_nb=", bld_nb
print "roof_types=", roof_types
print "num_storeys=", num_storeys
print "body_volume=", body_volume
print "roof_volume=", roof_volume
print "building_volume=", building_volume
print "building_height=", building_height
print ""
print "z_footprints=",z_footprints
print "z_max_body=",z_max_body
print "z_max_roof=", z_max_roof
