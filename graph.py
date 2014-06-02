class Vertex(object):
    def __init__(self,key, node):
        self.id = key
        self.node = node
        self.connectedTo = {} #adjacent sensors

    def addNeighbor(self,nbr,weight=0):
        self.connectedTo[nbr] = weight #distance from one node to the other

    def getConnections(self):
        return self.connectedTo.keys()

    def getId(self):
        return self.id

    def getNode(self):
        return self.node

    def getWeight(self,nbr):
    	"""Returns the distance from the colling node to neighbord node (nbr)"""
        return self.connectedTo[nbr]

    def __str__(self):
        return str(self.node) + '\nconnectedTo: ' + \
        str([x.id for x in self.connectedTo]) + '\n'

class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self,key, node):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key, node)
        self.vertList[key] = newVertex
        #return newVertex

    def getVertex(self,vert):
        if vert in self.vertList:
            return self.vertList[vert]
        else:
            return None

    def __contains__(self,vert):
        return vert in self.vertList

    def addEdge(self,a,b,cost=0):
        if a not in self.vertList:
            nv = self.addVertex(a)
        if b not in self.vertList:
            nv = self.addVertex(b)
        self.vertList[a].addNeighbor(self.vertList[b], cost)

    def getVertices(self):
        return self.vertList

    def __iter__(self):
        return iter(self.vertList.values())

    def getNumVertices(self):
    	return self.numVertices
		
		