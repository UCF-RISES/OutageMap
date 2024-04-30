import re
from pathlib import Path
import pynldas2 as nldas
from pygeohydro import WBD
import pygeohydro as gh
from pynhd import NLDI
import py3dep
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from util.ComponentClasses import Bus, Line, Load, Node, Edge
import os
import time
import multiprocessing 
from datetime import datetime
import math

def readBusData(file_path):
    """
    Parses the bus data from the file, including both x and y coordinates.
    This version correctly parses the "Nodes Connected" field, accounting for the actual nodes connected.

    Args:
    file_path (str): The path to the file containing the bus data.

    Returns:
    list of dicts: A list containing the parsed data with keys 'Bus', 'Coord', and 'Nodes Connected'.
    """
    parsed_data = []

    with open(file_path, 'r') as file:
        # Skip header lines
        for _ in range(5):
            next(file)

        # Parse each line
        for line in file:
            if line.strip():  # Skip empty lines
                # Extract the bus name
                bus_match = re.search(r'"(.*?)"', line)
                bus = bus_match.group(1) if bus_match else None
                # Extract the coordinates
                coord_match = re.search(r'\(([^)]+)\)', line)
                coord = tuple(coord_match.group(1).split(', ')) if coord_match else None

                # Extract the Base kV
                base_kv_match = re.search(r'\s+(\d+\.?\d*)\s+', line)
                base_kV = float(base_kv_match.group(1)) if base_kv_match else None
                #print(base_kV)

                # Extract the number of nodes and nodes connected
                # Find all numbers after coordinates and exclude the first one (which is the number of nodes)
                numbers_after_coord = re.findall(r'(\d+)', line[coord_match.end():])
                if numbers_after_coord:
                    num_nodes = int(numbers_after_coord[0])
                    nodes_connected = numbers_after_coord[1:1 + num_nodes]  # Extract nodes based on the count

                # Adding the parsed data to the list
                parsed_data.append({
                    'Bus': bus,
                    'Base_kV': base_kV,
                    'Coord': coord,
                    'Nodes Connected': nodes_connected
                })

    return parsed_data

def readTransformerData(dss_file_path):
    """
    Reads and parses transformer data from a DSS file.

    This function opens a specified DSS file and reads it line by line to extract
    information about transformers. It uses regular expressions to parse data fields such
    as the transformer's name, number of phases, windings, normal high voltage capacity (NormHKVA),
    winding numbers (Wdg), connection types (ConnType), voltage levels (kV), capacity (kVA), and
    buses. The function supports multiple occurrences of windings, connection types, voltage levels,
    capacities, and buses, aggregating these values into lists.

    Parameters:
    - dss_file_path (str): The path to the DSS file to be read.

    Returns:
    - list[dict]: A list of dictionaries, each containing the parsed data of a transformer.
                  Returns None if the file is not found.

    Raises:
    - FileNotFoundError: If the specified file cannot be found.
    """
    try:
        parsed_data = []
        with open(dss_file_path, 'r') as file:
            for line in file:
                # Skip empty lines
                if line.strip():  

                    # Define patterns for each piece of data to extract
                    namePattern = r'Transformer.\S*'
                    phasePattern = r'phases\S*'
                    windingsPattern = r'windings\S*'
                    normhkvaPattern = r'normhkva\S*'
                    wdgPattern = r'wdg\S*'
                    connectionPattern = r'conn\S*'
                    kVPattern = r'Kv\S*'
                    kvaPattern = r'kva\S*'
                    busPattern = r'bus\S*'
                    equalPattern = r'=(\S+)'

                    # Match patterns in the line
                    nameMatch = re.search(namePattern, line)
                    phaseMatch = re.search(phasePattern, line)
                    windingsMatch = re.search(windingsPattern, line)
                    normhkvaMatch = re.search(normhkvaPattern, line)
                    wdgMatchNE = [re.search(equalPattern, wdg).group(1) for wdg in re.findall(wdgPattern, line)]
                    connMatchNE = [re.search(equalPattern, conn).group(1) for conn in re.findall(connectionPattern, line)]
                    kvMatchNE = [re.search(equalPattern, kv).group(1) for kv in re.findall(kVPattern, line)]
                    kvaMatchNE = [re.search(equalPattern, kva).group(1) for kva in re.findall(kvaPattern, line)]
                    busMatchNE = [re.search(equalPattern, bus).group(1) for bus in re.findall(busPattern, line)]

                    # Extract the value after the equal sign for single occurrence parameters
                    phaseMatchNE = re.search(equalPattern, phaseMatch.group())
                    windingsMatchNE = re.search(equalPattern, windingsMatch.group())
                    normhkvaMatchNE = re.search(equalPattern, normhkvaMatch.group())
                
                    parsed_data.append({
                    'Name': nameMatch.group().lower(),
                    'Phases': phaseMatchNE.group(1),
                    'Windings': windingsMatchNE.group(1),
                    'NormHKVA': normhkvaMatchNE.group(1),
                    'Wdg': wdgMatchNE,
                    'ConnType': connMatchNE,
                    'kV': kvMatchNE,
                    'kVA': kvaMatchNE,
                    'bus':busMatchNE
                    })
        return parsed_data
    except FileNotFoundError:
        print(f"The file {dss_file_path} was not found.")
        return None

def readLineCodeData(dss_file_path):
    """
    Reads and parses line code data from a DSS file.

    This function opens a DSS file provided by the `dss_file_path` parameter and
    reads it line by line to extract data related to line codes. It searches for
    specific patterns indicating the line code's name, number of phases, fault rate,
    resistance matrix (R), reactance matrix (X), capacitance matrix (C), and normal
    ampacity. It uses regular expressions for pattern matching to ensure accurate
    data extraction. For parameters that may not be present in the line (e.g., fault rate,
    capacitance matrix), the function assigns 'None' to maintain data integrity.

    Parameters:
    - dss_file_path (str): The path to the DSS file to be read.

    Returns:
    - list[dict]: A list of dictionaries, each containing the parsed data for a line code.
                  Returns None if the file is not found.

    Raises:
    - FileNotFoundError: If the specified DSS file cannot be found at the given path.
    """
    try:
        parsed_data = []
        with open(dss_file_path, 'r') as file:
            for line in file:
                # Skip empty lines
                if line.strip():  
                    # Define patterns for each piece of data to extract
                    namePattern = r'Linecode.\S*'
                    phasePattern = r'nphases\S*'
                    faultPattern = r'Faultrate\S*'
                    RPattern = r'Rmatrix=\(([^\)]*)\)'
                    XPattern = r'Xmatrix=\(([^\)]*)\)'
                    CPattern = r'Cmatrix=\(([^\)]*)\)'                    
                    normAmpPattern = r'normamps\S*'
                    equalPattern = r'=(\S+)'
                    equalPattern1 = r'=\(([^\)]*)\)'

                    # Search for the pattern in the string
                    nameMatch = re.search(namePattern, line)
                    
                    # Perform pattern matching
                    if nameMatch:
                        phaseMatch = re.search(equalPattern, re.search(phasePattern, line).group()).group(1)
                        faultMatch = 'None' if re.search(faultPattern, line) is None else re.search(equalPattern, re.search(faultPattern, line).group()).group(1)
                        RMatch = re.search(equalPattern1, re.search(RPattern, line).group()).group()
                        XMatch = re.search(equalPattern1, re.search(XPattern, line).group()).group()
                        CMatch = 'None' if re.search(CPattern, line) is None else re.search(equalPattern1, re.search(CPattern, line).group()).group(1)
                        normAmpMatch = re.search(equalPattern, re.search(normAmpPattern, line).group()).group(1)
                        
                        # Append the parsed data
                        parsed_data.append({
                        'Name': nameMatch.group(),
                        'Phases': phaseMatch,
                        'FaultRate': faultMatch,
                        'R': RMatch,
                        'X': XMatch,
                        'C': CMatch,
                        'Normal Ampacity': normAmpMatch
                        })
        return parsed_data
    
    except FileNotFoundError:
        print(f"The file {dss_file_path} was not found.")
        return None

def readLineData(dss_file_path):
    """
    Reads and parses electrical line data from a DSS file.

    This function opens a specified DSS file and reads it line by line, extracting
    information relevant to electrical lines such as name, length, connecting buses,
    number of phases, whether it is a switch, its enabled status, and the line code.
    It uses regular expressions for pattern matching to ensure accurate data extraction.
    The extracted data is stored in a list of dictionaries, with each dictionary representing
    a line and its attributes.

    Parameters:
    - dss_file_path (str): The path to the DSS file to be read.

    Returns:
    - list[dict]: A list of dictionaries, each containing parsed data for an electrical line.
                  Returns None if the file is not found.

    Raises:
    - FileNotFoundError: If the specified DSS file cannot be found at the given path.
    """
    
    try:
        parsed_data = []
        with open(dss_file_path, 'r') as file:
            for line in file:
                # Skip empty lines
                if line.strip():
                    # Define patterns for data extraction
                    namePattern = r'^New Line.\S*'
                    lengthPattern = r'Length\S*'
                    bus1Pattern = r'bus1\S*'
                    bus2Pattern = r'bus2\S*'
                    phasePattern = r'phases\S*'
                    switchPattern = r'switch=\S*'
                    enablePattern = r'enabled\S*'
                    lineCodePattern = r'Linecode\S*'
                    equalPattern = r'=(\S+)'

                    # Search for the pattern in the string
                    nameMatch = re.search(namePattern, line)
                    if nameMatch:
                        lengthMatch = re.search(equalPattern,re.search(lengthPattern, line).group())
                        bus1Match = re.search(equalPattern,re.search(bus1Pattern, line).group())
                        bus2Match = re.search(equalPattern,re.search(bus2Pattern, line).group())
                        phaseMatch = re.search(equalPattern,re.search(phasePattern, line).group())
                        switchMatch =re.search(equalPattern,re.search(switchPattern, line).group())
                        enableMatch =re.search(equalPattern,re.search(enablePattern, line).group())
                        lineCodeMatch = re.search(equalPattern,re.search(lineCodePattern, line).group())

                        # Append the parsed data
                        parsed_data.append({
                        'Name': nameMatch.group().lower(),
                        'Length': lengthMatch.group(1),
                        'Bus1': bus1Match.group(1),
                        'Bus2': bus2Match.group(1),
                        'Phases': phaseMatch.group(1),
                        'LineCode': lineCodeMatch.group(1),
                        'Switch': switchMatch.group(1),
                        'Enable':enableMatch.group(1)
                        })
        return parsed_data
    
    except FileNotFoundError:
        print(f"The file {dss_file_path} was not found.")
        return None

def readLoadData(dss_file_path):
    """
    Reads and parses load data from a DSS file.

    This function opens a DSS file from the given path and reads it line by line
    to extract information about each load. It expects each line to contain data
    in a specific format and uses regular expressions to find and extract
    details such as the load's name, connection type, bus, voltage levels (kV, Vminpu, Vmaxpu),
    power (kW, kvar), and the number of phases. The extracted data is stored in
    a dictionary for each load, and a list of these dictionaries is returned.

    Parameters:
    - dss_file_path (str): The path to the DSS file to be read.

    Returns:
    - list[dict]: A list of dictionaries, each containing the parsed data of a load.
                  Returns None if the file is not found.

    Raises:
    - FileNotFoundError: If the specified file cannot be found.
    """
    
    try:
        parsed_data = []
        with open(dss_file_path, 'r') as file:
            for line in file:
                # Skip empty lines
                if line.strip(): 
                    # Define patterns for each piece of data to extract
                    namePattern = r'Load.\S*'
                    connectionPattern = r'conn\S*'
                    busPattern = r'bus1\S*'
                    kVPattern = r'kV\S*'
                    VminpuPattern = r'Vminpu\S*'
                    VmaxpuPattern = r'Vmaxpu\S*'
                    kWPattern = r'kW\S*'
                    kvarPattern = r'kvar\S*'
                    phasePattern = r'Phases\S*'
                    equalPattern = r'=(\S+)'

                    # Search for the pattern in the string
                    nameMatch = re.search(namePattern, line)
                    connectionMatch = re.search(connectionPattern,line)
                    busMatch = re.search(busPattern, line)
                    kvMatch = re.search(kVPattern,line)
                    vminMatch = re.search(VminpuPattern,line)
                    vmaxMatch = re.search(VmaxpuPattern,line)
                    kWMatch = re.search(kWPattern,line)
                    kvarMatch = re.search(kvarPattern,line)
                    phaseMatch = re.search(phasePattern, line)
                    
                    # Extract the value after the equal sign for each parameter
                    connectionMatchNE = re.search(equalPattern,connectionMatch.group())
                    busMatchNE = re.search(equalPattern,busMatch.group())
                    kvMatchNE = re.search(equalPattern,kvMatch.group())
                    vminMatchNE = re.search(equalPattern,vminMatch.group())
                    vmaxMatchNE = re.search(equalPattern,vmaxMatch.group())
                    kWMatchNE = re.search(equalPattern,kWMatch.group()) 
                    kvarMatchNE = re.search(equalPattern,kvarMatch.group()) 
                    phaseMatchNE = re.search(equalPattern,phaseMatch.group())
                    
                    # Append the parsed data dictionary to the list
                    parsed_data.append({
                    'Name': nameMatch.group().lower(),
                    'Connection': connectionMatchNE.group(1),
                    'Bus': busMatchNE.group(1),
                    'kV': kvMatchNE.group(1),
                    'Vminpu': vminMatchNE.group(1),
                    'Vmaxpu': vmaxMatchNE.group(1),
                    'kW': kWMatchNE.group(1),
                    'kvar': kvarMatchNE.group(1),
                    'Phases': phaseMatchNE.group(1)
                    })
        return parsed_data
    except FileNotFoundError:
        print(f"The file {dss_file_path} was not found.")
        return None

def find_node_by_name(connections, target):
    """
    Function to search for the index of an element by name

    Args:
        connections (list): List of connection objects
        target (str): Name of element to fidn

    Returns:
        (int): index of element if it is found
    """
    # Loop through connections
    for i in range (len(connections)):
        # Check if names are equal
        if connections[i].name == target:
            # Return index
            return i     
    # Else return none
    return None

def findNumLoads(bus, loads):
    """
    Counts the number of loads connected to a specified bus.
    
    This function iterates through a list of loads, checking if each load's bus attribute
    matches the specified bus parameter. It counts and returns the total number of matching loads.
    
    Parameters:
    - bus (str): The identifier of the bus for which to count connected loads.
    - loads (list): A list of load objects. Each load object must have a 'bus' attribute.
    
    Returns:
    - int: The total number of loads connected to the specified bus.
    """
    num = 0
    for load in loads:
        if bus == load.bus:
            num = num+1
    return num

def findNodeNum(bus, nodes):
    """
    Finds and returns the numerical identifier of a node with a specified name.
    
    This function iterates through a list of node objects, comparing each node's name attribute
    with the specified bus parameter. If a match is found, it returns the numerical identifier
    (num attribute) of the matching node.
    
    Parameters:
    - bus (str): The name of the node to find.
    - nodes (list): A list of node objects. Each node object must have 'name' and 'num' attributes.
    
    Returns:
    - int or None: The numerical identifier of the matching node, or None if no match is found.
    """
    if '.' in bus:
        bus = nodeNameSplit(bus)

    for node in nodes:
        if bus == node.name:
            return node.num
 
def getWeatherByCoords(lon,lat,start,end):
    """
    Grabs an hourly weather dataset at the specified longitude and latitude.

    Args:
    lon (str): Longitude of desired location.
    lat (str): Latitude of desired location.
    start (str): Start Time of Desired Event
    end (str): Stop Time of Desired Event

    NLDAS Hourly Weather Data Identifiers
    - prcp: precipitation hourly total (kg/m^2)
    - rlds: surface downward longwave radiation (W/m^2)
    - rsds: surface downward shortwave radiation (W/m^2)
    - temp: air temperature (K) ** at 2 meters above the surface
    - humidity: specific humidity (kg/kg) ** at 2 meters above the surface
    - wind_u: U wind component (m/s) at 10 meters above the surface
    - wind_v: V wind component (m/s) at 10 meters above the surface

    Indexing: data['wind_u'][1] gives the wind_u value for second hour of event
    - Wind Speed m/sec = sqrt(data['wind_u']**2 + data['wind_v']**2)
    - getWeather(-120.82899598, 36.50996789,"2010-01-08", "2010-01-08")

    Returns:
    data (dict): Dictionary corresponding to the hour climatology data associated with the data and location
    """

    data =nldas.get_bycoords(list(zip([lon],[lat])),start,end) 
    return data

def getLandCover(coords):
    """
    Grabs the tree canopy coverage (in year 2016) at the specified longitude and latitude.

    Args:
    coords (tuple): Longitude, and Latitude of desired location.

    Returns:
    tcc (float): Value corresponding to the tree canopy coverage in that area
    """
    # Grab latitude and longitude from coords
    lon = coords[0]
    lat = coords[1]
    
    # OR get the data for specific coordinates using nlcd_bycoords (cover_statistics does not work with this method)
    land_usage_land_cover = gh.nlcd_bycoords(list(zip([lon],[lat])), years={"canopy": [2016]})

    # Grab the tree canopy coverage
    tcc = land_usage_land_cover.canopy_2016[0]

    # Return the land usage and cover data
    return tcc

def getElevationByCoords(coords):
   """
    Grabs the elevation in meters at the specified longitude and latitude using Py3DEP.

    Args:
    coords (tuple): Longitude, and Latitude of desired location.

    Returns:
    elevation (float): Value corresponding to the elevation in meters
    """
   # Elevation Acquisition (in meters)
   elevation = py3dep.elevation_bycoords(coords, crs=4326) 
   return elevation

def findEdgeElevation(bus1,bus2, nodes):
    """
    Determines edge elevation by finding midpoint between two nodes and finding the elevation at that point.

    Args:
    bus1 (int): Number of first node connected to the edge
    bus2 (int): Number of second node connected to the edge
    nodes (list): List of nodes in the network

    Returns:
    edgeElevation (float): Value corresponding to the elevation for the edge in meters
    """

    # Loops through all the nodes
    for node in nodes:
        # Finds the node number for the first node and grabs it coords
        if bus1 == node.num:
            coord1 = node.coords
        # Finds the node number for the second node and grabs it coords
        if bus2 == node.num:
            coord2 = node.coords
    # Creates a list of the two coordinates 
    test_list = [coord1,coord2]

    # Average the two coordinates to get the midpoint
    res = [sum(ele) / len(test_list) for ele in zip(*test_list)] 

    # Find elevation at midpoint
    edgeElevation = getElevationByCoords(tuple(res))
    
    return edgeElevation
    
def roundup(x):
    """
    Function to round a float to integer using ceiling

    Args:
    x (float): Number to round

    Returns:
    rounded (int): Value corresponding to the rounded float
    """

    rounded = int(math.ceil(x / 100.0)) * 100
    return rounded

def cft(input_tuple):
    """
    Function to remove white space from a tuple while also converting values to floats

    Args:
    input_tuple (tuple): Tuple to modify

    Returns:
    newTuple (tuple): Modified Tuple
    """
    # Strip leading and trailing whitespace and convert to float
    newTuple = tuple(float(item.strip()) for item in input_tuple)

    return newTuple

def parseDate(date):
    """
    Parses a datetime string into a date string.

    Args:
        date (str): A string representing a datetime in the format '%Y-%m-%d %H:%M:%S'.

    Returns:
        str: A string representing the date extracted from the input datetime string
             in the format '%Y-%m-%d'.
             
    Raises:
        ValueError: If the input date string is not in the expected format or cannot be parsed.

    """
    datetime_obj = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')

    date_str = datetime_obj.strftime('%Y-%m-%d')

    return date_str

def parseTime(time):
    """
    Parses a time string into a standardized format.

    Args:
        time (str): A string representing time in the format 'HHMM', where HH represents
                    hours (00 to 23) and MM represents minutes (00 to 59).

    Returns:
        str: A string representing the time in a standardized format 'HHMM', where hours
             and minutes are zero-padded if necessary.
    """
    
    time = str(time)
    if len(time) != 4:
        time = ("0" * (4 - len(time))) + time
    return time

def nodeNameSplit(text):
    """
    Splits the input text by the dot ('.') character and returns the first part.

    Parameters:
    text (str): The input text to be split.

    Returns:
    str: The first part of the input text before the first dot ('.') character.
    """
    return text.split('.')[0]


