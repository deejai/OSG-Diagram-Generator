import pydotplus as pydot
import glob

class NodeDiagram():

    # Fill colors for given node types
    nodeColors = {
    "root"              : "white",
    "LOD"               : "orange",
    "PagedLOD"          : "yellow",
    "Group"             : "green",
    "MatrixTransform"   : "turquoise",
    "Switch"            : "violet",
    "Geode"             : "tan"
    }


    def __init__(self, name, identifier=""):
        self.name = name
        self.identifier = identifier
        self.nodeID = 0
        self.generated = False
        self.file = open("structure_%s.txt" % name, "r")
        self.graph = pydot.Dot(graph_type = "graph")

    def getLastTag(self):
        return str(self.nodeID) + self.identifier

    def addChild(self, parentID, childID):
        print("addChild(%d, %d)" % (parentID, childID), end="" )
        if(parentID > self.nodeID):
            print(" ERROR\nInvalid parentID: %d. Current nodeID: %d" %(parentID, self.nodeID) )
            exit()
        else:
            self.graph.add_edge(pydot.Edge(str(parentID), str(childID)))
            print(" Complete.")

    def createNode(self, nodeType, addendum=""):
        print("createNode(%s) (nodeID: " % nodeType, end="")
        if( nodeType not in self.nodeColors ):
            print("ERROR)\nInvalid nodeType: %s" % nodeType)
            exit()
        else:
            self.nodeID += 1
            print("%s)" % self.getLastTag())
            if( nodeType == "root" ):
                label = self.name
            else:
                label = nodeType + addendum
            self.graph.add_node(pydot.Node(str(self.nodeID), label=label, style="filled",
                                                             fillcolor=self.nodeColors[nodeType]))

    def attachEllipsis(self, nodeType, parentID):
        # Add indicator that multiple nodes of the given type can exist
        ID = str(self.nodeID) + "*"
        self.graph.add_node(pydot.Node(ID, label="...", style="filled", 
                                           fillcolor=self.nodeColors[nodeType]))
        self.graph.add_edge(pydot.Edge(str(parentID), ID))
        
    def generateGraph(self):
        if( self.generated ):
            print("Graph has already been generated")
            return
        else:
            print(self.name)
            self.createNode("root")
            self.recursiveGenerate(None, 0)
            self.generated = True

    def recursiveGenerate(self, parentID, depth):
        # parentID can be None or int, so print its statement is separate
        print("recursiveGenerate(", end="")
        print(parentID, end="")
        print(", %d)" % depth )

        line = self.file.readline().rstrip()
        nodeType = line.strip().replace("*", "")
        while(line):
            lvl = line.count(' ')
            if( lvl >= depth ):
                print("lvl(%d) >= depth(%d)" %(lvl, depth) )
                self.createNode( nodeType )
                if( parentID is not None ):
                    self.addChild(parentID, self.nodeID)

                    if( line[-1:] == "*" ):
                        print(" |--> multi")
                        self.attachEllipsis( nodeType, parentID )
                line = self.recursiveGenerate(self.nodeID, lvl+1)
            else:
                break
        return line

    def generateFile(self):
        self.graph.write_png(self.name + ".png")

def quickMake():
    chars = "abcdefghijklmnopqrstuvwxyz"
    i = 0
    # for each .txt file beginning with "structure_", generate a graph and a .png
    for file in glob.glob("structure_*.txt"):
        # provides a unique id for up to (len(chars) * len(chars)) entries
        char1 = i // len(chars)
        char2 = i % len(chars)
        tag = chars[char1] + chars[char2]

        diagram = NodeDiagram(file.replace("structure_", "").replace(".txt", ""), tag)
        diagram.generateGraph()
        diagram.generateFile()
        i += 1

def main():
    quickMake()

if __name__ == "__main__":
    main()
