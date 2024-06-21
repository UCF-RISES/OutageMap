import matplotlib.pyplot as plt
import networkx as nx
import opendssdirect as dss
import pandas as pd
from util.NetworkFunctions import getElevationByCoords, fixBusName,findNodeNum, getLandCover,findAvgLineVegetation
from util.ComponentClasses import Bus, Line, Load, Node, Edge, Transformer
import warnings
warnings.filterwarnings("ignore")

# Load the P3R Network
dss.Command('Redirect P3R/DSS/Master.dss')

# Acquire a list of buses, lines, elements, transformers, and loads
buses = dss.Circuit.AllBusNames()
lines = dss.Lines.AllNames()
elements = dss.Circuit.AllElementNames()
transformers  = [item for item in elements if 'Transformer' in item]
loads = [item for item in elements if 'Load' in item] 

# Initialize empty list for circuit and graph components
BUSES=[]
LINES = []
TRANSFORMERS = []
LOADS = []
NODES = []
EDGES = []

# Loop through buses, and append bus data to bus list
for bus in buses:
    dss.Circuit.SetActiveBus(bus)
    # Append [Name, (X,Y), Base kV] to bus object and store in list
    BUSES.append(Bus(dss.Bus.Name(),(dss.Bus.X(),dss.Bus.Y()),dss.Bus.kVBase()))

# Loop through lines, and append line data to line list
for line in lines:
    # Set the current line
    dss.Lines.Name(line)
    # Set the current line (element form to get enabled)
    dss.Circuit.SetActiveElement(line)
    # Append [Name, Length, Bus1, Bus2, Enabled] to line object and store list
    LINES.append(Line(dss.Lines.Name(),dss.Lines.Length(),dss.Lines.Bus1(),dss.Lines.Bus2(),dss.CktElement.Enabled()))

# Loop through transformers
for transformer in transformers:
    # Set the current transformer
    dss.Circuit.SetActiveElement(transformer)
    # Get the buses attached to transformers
    busesT = dss.CktElement.BusNames()
    # Remove the node number from bus name for simplification
    newBusT = fixBusName(busesT)
    # Append [Name, Bus1 Bus2 WdgVoltages and WdgCurrents] to Transformer object and store in list
    TRANSFORMERS.append(Transformer(dss.Element.Name(),newBusT[0],newBusT[1],dss.Transformers.WdgVoltages(),dss.Transformers.WdgCurrents()))

# Loop through loads
for load in loads:
    # Set the current load element
    dss.Circuit.SetActiveElement(load)
    # Get the bus attached to the load
    lBus = dss.CktElement.BusNames()
    # Fix the bus name for simplicity
    newBusL = fixBusName(lBus)
    # Append [Name, Bus, kV, kvar, Vminpu, Vmaxpu, Phases] to Load object and store in list
    LOADS.append(Load(dss.Loads.Name(), newBusL[0], dss.Loads.kV(), dss.Loads.kW(), dss.Loads.kvar(), dss.Loads.Vminpu(), dss.Loads.Vmaxpu(), dss.Loads.Phases()))

# Loop through bus list
for i, bus in enumerate(BUSES):
    # Print the node number for progress check
    print('Node ' + str(i))
    # Append [Name, Num, Coord, Elevation, Vegetation] to node object and store in node list
    NODES.append(Node(bus.name,i,bus.coordinates,elevation=getElevationByCoords(bus.coordinates), vegetation=getLandCover(bus.coordinates)))

# Print Progress Update
print('Nodes Created')

# Loop through lines
for line in LINES:
    # Append [Name, Length, Node1, Node2, Enabled] to Edge object and store in list
    EDGES.append(Edge(line.name,line.length,findNodeNum(line.bus1, NODES),findNodeNum(line.bus2, NODES),line.enabled))

# Loop through transformers
for tf in TRANSFORMERS:
    # Append [Name, 0, Node1, Node2, 1] to Edge object and store in list
    EDGES.append(Edge(tf.name,0, findNodeNum(tf.bus1, NODES),findNodeNum(tf.bus2, NODES),1))

# Print Progress Update
print('Edges Created')

# Create a new graph. # Need to use a graph class that includes Multi (MultiGraph, MultiDiGraph, etc.)
G = nx.MultiDiGraph()

# Initialize a node dictionary to convert to csv
nodeDict = []

# Loop through node list
for node in NODES:
    # Add the Node to Graph G
    G.add_node(node.num, name = node.name, coords = node.coords)
    # Add Node Data to dictionary entry and store in list
    nodeDict.append({
        'name':node.name,
        'coords':node.coords,
        'elevation':node.elevation,
        'vegetation':node.vegetation
        })

# Loop through edges
for i, edge in enumerate(EDGES):
    # Check if the edge is enabled
    if edge.enabled ==1:
        # Print the edge number for progress update
        print('Edge ' + str(i))
        # Add the Edge to Graph G and assign edge data to corresponding attributes
        G.add_edge(edge.bus1, edge.bus2,name = edge.name, length = edge.length, vegetation = findAvgLineVegetation(edge.bus1, edge.bus2, NODES,10))

# Create a position mapping based on node coordinates 
pos = {node.num: node.coords for node in NODES if node.coords is not None}

# Draw the graph
nx.draw_networkx(G, pos=pos,with_labels=True, node_size=30, font_size=6,arrows=True)
plt.show()

# Convert Edge List and Node List to Panda Dataframes
el = nx.to_pandas_edgelist(G)
nl = pd.DataFrame(nodeDict)

# Convert Panda Dataframes to Edge List and Node List CSV
pd.DataFrame.to_csv(nl,'P3R/nodeList.csv')
pd.DataFrame.to_csv(el,'P3R/edgeList.csv')
