# Bus Component Class
class Bus:
    def __init__(self, name, coordinates, baseVoltage=None):
        # Bus name
        self.name = name
        # Bus location
        self.coordinates = coordinates

        # Bus base voltage
        self.baseVoltage = baseVoltage


# Load Component Class
class Load:
    def __init__(self, name, bus, kV, kW, kvar, vminpu, vmaxpu, phases):
        # Load Name
        self.name = name
        
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
    def __init__(self, name, length, bus1, bus2,enabled,):
        # Load Name
        self.name = name
        
        # Length of Line
        self.length = length
        
        # Starting point of line
        self.bus1 = bus1
        
        # Ending point of line
        self.bus2 = bus2

        # Is the line enabled
        self.enabled = enabled


class Transformer:
    def __init__(self, name, bus1,bus2,voltages,currents):
        
        # Name of Transformer
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.voltages = voltages
        self.currents =currents

# Node Class for Graph Neural Network
class Node:
    def __init__(self, name, num, coords, elevation=None, vegetation=None):
        
        # Node name
        self.name = name
        
        # Node number
        self.num = num

        self.coords = coords

        self.elevation = elevation
        self.vegetation = vegetation

# Edge Class for Graph Neural Network
class Edge:
    def __init__(self, name, length, bus1, bus2, enabled, vegetation=None):
        
        # Name of Edge
        self.name = name
        
        # Length of line 
        self.length = length            # 0 if transformer, else length

        # Terminal 1 Connection
        self.bus1 = bus1
        
        # Terminal 2 Connection
        self.bus2 = bus2

        # Is the edge enabled
        self.enabled = enabled          # This will be 0 if no and 1 if yes'

        self.vegetation = vegetation

