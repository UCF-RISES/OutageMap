import matplotlib.pyplot as plt
from util.NetworkFunctions import readBusData,readLineCodeData,readLineData, cft, getElevationByCoords
from util.NetworkFunctions import readTransformerData, readLoadData, findNumLoads,findNodeNum, getLandCover, findEdgeElevation, findAvgLineVegetation
import pandas as pd
import networkx as nx
from util.ComponentClasses import Bus, Line, Load, Node, Edge
import matplotlib.pyplot as plt 


# File Paths
transformerPath ="P3R/DSS/Transformers.dss"
busPath ="P3R/DSS/feeder_p3rdt1052-p3rhs0_1247x_Buses.Txt"
elementPath = "P3R/DSS/feeder_p3rdt1052-p3rhs0_1247x_Elements.Txt"
linePath = "P3R/DSS/Lines.dss"
lineCodePath = "P3R/DSS/LineCodes.dss"
loadPath = "P3R/DSS/Loads.dss"


# Parse buses.txt and put data into dictionary
busData=readBusData(busPath)

# Parse transformers.dss and put data into dictionary
transformerData=readTransformerData(transformerPath)

# Parse linecodes.dss and put data into dictionary
lineCodeData=readLineCodeData(lineCodePath)

# Parse Lines.dss and put data into dictionary
lineData = readLineData(linePath)

# Parse Loads.dss and put data into dictionary
loadData=readLoadData(loadPath)

print('Data Read From CSV')

# Append Bus Data to list
BUSES=[]
for bus in busData:
    BUSES.append(Bus(bus['Bus'],bus['Coord'],bus['Base_kV'],len(bus['Nodes Connected'])))

# Append Line Data to list
LINES = []
i=0 
for line in lineData:
    LINES.append(Line(line['Name'], line['Length'], line['Bus1'].split('.')[0], line['Bus2'].split('.')[0], line['Switch'], line['Enable'], line['Phases'], line['LineCode']))

# Append Load Data to list
LOADS = []
i=0 
for load in loadData:
    LOADS.append(Load(load['Name'], load['Connection'], load['Bus'].split('.')[0], load['kV'], load['kW'],load['kvar'], load['Vminpu'], load['Vmaxpu'], load['Phases']))

# Append Buses to Node List
NODES = []
i=0
for bus in BUSES:
    print('Node ' + str(i))
    NODES.append(Node(bus.name, bus.baseVoltage,i,findNumLoads(bus.name,LOADS),cft(bus.coordinates),elevation=getElevationByCoords(bus.coordinates), vegetation=getLandCover(bus.coordinates)))
    i=i+1
print('Nodes Created')
# Append Lines and Transformers to Node List
EDGES = []
for line in LINES:
    if 'UG' in line.linecode:
        location = 0
    else:
        location = 1
    if 'switch' in line.linecode:
        type = 0
    else:
        type = 1
    EDGES.append(Edge(line.name,line.length,type, findNodeNum(line.bus1, NODES),findNodeNum(line.bus2, NODES), line.switch, line.enabled, location))

for tf in transformerData:
    EDGES.append(Edge(tf['Name'],0,2, findNodeNum(tf['bus'][0], NODES),findNodeNum(tf['bus'][1], NODES),'n', 'y',1))

print('Edges Created')
# Create a new graph. # Need to use a graph class that includes Multi (MultiGraph, MultiDiGraph, etc.)
G = nx.MultiDiGraph()

# Initialize a node dictionary
nodeDict = []

# Add Nodes to Graph
for node in NODES:
    G.add_node(node.num, name = node.name, voltage = node.voltage, loads = node.loads, coords = node.coords)
    nodeDict.append({
        'name':node.name,
        'voltage':node.voltage,
        'POF':node.loads,
        'coords':node.coords,
        'elevation':node.elevation,
        'vegetation':node.vegetation
        })
i=0
# Add Edges to Graph
for edge in EDGES:
    if edge.enabled =='y':
        print('Edge ' + str(i))
        G.add_edge(edge.bus1, edge.bus2, length = edge.length, elevation=findEdgeElevation(edge.bus1, edge.bus2, NODES), type = edge.type, location=edge.location, vegetation = findAvgLineVegetation(edge.bus1, edge.bus2, NODES,10), name = edge.name)
        i=i+1
# # Create a position mapping based on node coordinates 
pos = {node.num: node.coords for node in NODES if node.coords is not None}

# # # Draw the graph
# nx.draw_networkx(G, pos=pos,with_labels=True, node_size=30, font_size=6,arrows=True)
# plt.show()

# # Edge List and Node List to Panda Dataframes
el = nx.to_pandas_edgelist(G)
nl = pd.DataFrame(nodeDict)

# # Panda Dataframes to Edge List and Node List csv
pd.DataFrame.to_csv(nl,'P3R/nodeList.csv')
pd.DataFrame.to_csv(el,'P3R/edgeList.csv')
