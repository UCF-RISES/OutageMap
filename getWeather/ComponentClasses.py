# Bus Component Class
class Bus:
    def __init__(self, name, coordinates, baseVoltage=None, numNodes=3):
        # Bus name
        self.name = name
        # Bus location
        self.coordinates = coordinates
        # Bus nodes (max is 3)
        self.numNodes = numNodes
        # Bus base voltage
        self.baseVoltage = baseVoltage

# Load Component Class
class Load:
    def __init__(self, name, configuration, bus, kV, kW, kvar, vminpu, vmaxpu, phases):
        # Load Name
        self.name = name
        
        # Connection Type 
        self.configuration = configuration

        # Bus name that load is connected to
        self.bus = bus
        
        # Load Voltage
        self.kV = kV

        # Load Consumption
        self.kW = kW

        self.kvar = kvar
        
        # Load min per unit voltage
        self.vminpu = vminpu
        
        # Load max per unit voltage
        self.vmaxpu = vmaxpu

        # Number of phases in load
        self.phases = phases

# Line Component Class
class Line:
    def __init__(self, name, length, bus1, bus2, switch, enabled, phases, linecode):
        # Load Name
        self.name = name
        
        # Length of Line
        self.length = length
        
        # Starting point of line
        self.bus1 = bus1
        
        # Ending point of line
        self.bus2 = bus2
        
        # Is the line a switch
        self.switch = switch
        
        # Is the line enabled
        self.enabled = enabled
        
        # Number of phases in line
        self.phases = phases
        
        # Linecode associated with line
        self.linecode = linecode

class Transformer:
    def __init__(self, name, phases, windings, normhkva, wdg1Connect,wdg2Connect,wdg3Connect, 
                 wdg1Bus,wdg2Bus,wdg3Bus, wdg1KV,wdg2KV,wdg3KV,
                 wdg1KVA,wdg2KVA,wdg3KVA,wdg1ehkva,wdg2ehkva,wdg3ehkva,xhl,xht,xlt):
        # Name of Transformer
        self.name = name

        # Number of Phases in Transformer
        self.phases = phases
        
        # Number of windings in transformer
        self.windings = windings
        self.normhkva = normhkva
        
        self.wdg1_connection = wdg1Connect
        self.wdg2_connection = wdg2Connect
        self.wdg3_connection = wdg3Connect
        
        self.wdg1_bus = wdg1Bus
        self.wdg2_bus = wdg2Bus
        self.wdg3_bus = wdg3Bus

        self.wdg1_kv = wdg1KV
        self.wdg2_kv = wdg2KV
        self.wdg3_kv = wdg3KV

        self.wdg1_kva = wdg1KVA
        self.wdg2_kva = wdg2KVA
        self.wdg3_kva = wdg3KVA

        self.wdg1_ehkva = wdg1ehkva
        self.wdg2_ehkva = wdg2ehkva
        self.wdg3_ehkva = wdg3ehkva

        self.xhl = xhl
        self.xht = xht
        self.xlt = xlt


# Node Class for Graph Neural Network
class Node:
    def __init__(self, name, voltage, num, loads,coords, elevation=None, vegetation=None):
        
        # Node name
        self.name = name
        
        # Node number
        self.num = num
        
        # Nominal Voltage at Node
        self.voltage = voltage
        
        # Number of Loads Connected
        self.loads = loads

        self.coords = coords

        self.elevation = elevation
        self.vegetation = vegetation

# Edge Class for Graph Neural Network
class Edge:
    def __init__(self, name, length, type, bus1, bus2, switch, enabled, location, elevation=None, vegetation=None):
        
        # Name of Edge
        self.name = name
        
        # Length of line 
        self.length = length            # 0 if transformer, else length
        
        # Location of Edge 
        self.location = location

        # Linecode or transformer identifier
        self.type = type                # 0 if switch, 1 if line, 2 if transformer
        
        # Terminal 1 Connection
        self.bus1 = bus1
        
        # Terminal 2 Connection
        self.bus2 = bus2


        # Is the edge a switch
        self.switch = switch            # This will be 0 if no and 1 if yes
        
        # Is the edge enabled
        self.enabled = enabled          # This will be 0 if no and 1 if yes'

        self.elevation = elevation

        self.vegetation = vegetation



class newNode:
    def __init__(self, name, num, voltage, coords, POF, elevation, vegetation=None):
        # Node name
        self.name = name
        # Node number
        self.num = num
        # Nominal Voltage at Node
        self.voltage = voltage
        # Node Coordinates
        self.coords = coords
        # Node Vegetaion
        self.vegetation = vegetation
        # Node Points of Failure
        self.POF = POF
        # Node Elevation Level
        self.elevation = elevation



class newEdge:
    def __init__(self, name, length, type, bus1, bus2, switch, enabled, location, elevation=None, vegetation=None):    
        # Name of Edge
        self.name = name
        
        # Length of line 
        self.length = length            # 0 if transformer, else length
        
        # Location of Edge 
        self.location = location

        # Linecode or transformer identifier
        self.type = type                # 0 if switch, 1 if line, 2 if transformer
        
        # Terminal 1 Connection
        self.bus1 = bus1
        
        # Terminal 2 Connection
        self.bus2 = bus2

        # Is the edge a switch
        self.switch = switch            # This will be 0 if no and 1 if yes
        
        # Is the edge enabled
        self.enabled = enabled          # This will be 0 if no and 1 if yes'

        self.elevation = elevation

        self.vegetation = vegetation