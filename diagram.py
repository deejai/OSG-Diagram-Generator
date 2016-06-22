import pydotplus as pydot
import glob

DEBUG = True

class NodeDiagram():

    # Fill colors for given node types
    node_colors = {
    "root"              : "white",
    "LOD"               : "orange",
    "PagedLOD"          : "yellow",
    "Group"             : "green",
    "MatrixTransform"   : "turquoise",
    "Switch"            : "violet",
    "Geode"             : "tan"
    }


    def __init__(self, name, tag=""):
        self.name = name
        self.tag = tag
        self.node_id = 0
        self.generated = False
        self.file = open("structure_%s.txt" % name, "r")
        self.graph = pydot.Dot(graph_type = "graph")

    def __getLastTag(self):
        return str(self.node_id) + self.tag

    def __addChild(self, parentID, childID):
        if DEBUG: print("addChild(%d, %d)" % (parentID, childID), end="" )
        if parentID > self.node_id:
            if DEBUG: print(" ERROR\nInvalid parentID: %d. Current node_id: %d"
                                           % (parentID, self.node_id) )
            exit()
        else:
            self.graph.add_edge(pydot.Edge(str(parentID), str(childID)))
            if DEBUG: print(" Complete.")

    def __createNode(self, nodeType, addendum=""):
        if DEBUG: print("createNode(%s) (node_id: " % nodeType, end="")
        if nodeType not in self.node_colors:
            if DEBUG: print("ERROR)\nInvalid nodeType: %s" % nodeType)
            exit()
        else:
            self.node_id += 1
            if DEBUG: print("%s, addednum: %s)" % (self.__getLastTag(), addendum) )
            if nodeType == "root":
                label = self.name
            else:
                label = nodeType + addendum
            self.graph.add_node(pydot.Node(str(self.node_id), label=label, style="filled",
                                                              fillcolor=self.node_colors[nodeType]))

    def __attachEllipsis(self, nodeType, parentID):
        # Add indicator that multiple nodes of the given type likely exist
        # Creates a node, but doesn't increment self.node_id
        ID = str(self.node_id) + '*'
        self.graph.add_node(pydot.Node(ID, label="...", style="filled", 
                                           fillcolor=self.node_colors[nodeType]))
        self.graph.add_edge(pydot.Edge(str(parentID), ID))
        
    def generateGraph(self):
        # A graph can only be generated once per NodeDiagram
        if self.generated:
            if DEBUG: print("Graph has already been generated")
            return
        else:
            if DEBUG: print('\n' + self.name)
            self.__createNode("root")
            self.__recursiveGenerate(None, 0)
            self.generated = True

    def __recursiveGenerate(self, parentID, depth):
        # parentID can be None or int, so print its statement is separate
        if DEBUG: print("recursiveGenerate(", end="")
        if DEBUG: print(parentID, end="")
        if DEBUG: print(", %d)" % depth )

        while True:
            line = self.file.readline().rstrip()
            if not line: break
            print(line)

            if ':' in line:
                addendum = line.split(':')[1] + "\n"
                print(addendum)
            else:
                addendum = ""

            nodeType = line.strip().split(':')[0].replace('*', "")
            level = line.count(' ')
            if level < depth: break

            self.__createNode( nodeType, addendum )
            if parentID is not None:
                self.__addChild(parentID, self.node_id)

                if( line[-1:] == '*' ):
                    if DEBUG: print(" |--> multi")
                    self.__attachEllipsis( nodeType, parentID )
            line = self.__recursiveGenerate(self.node_id, level+1)
            
        return line

    def generateFile(self):
        if not self.generated:
            if DEBUG: print("PNG file cannot be generated until the graph is generated")
        else:
            self.graph.write_png(self.name + ".png")

def quickMake():
    chars = "abcdefghijklmnopqrstuvwxyz"
    i = 0
    # for each .txt file beginning with "structure_", generate a graph and a .png
    for file in glob.glob("structure_*.txt"):
        # provides a unique id for up to (len(chars) * len(chars)) entries
        char1 = (i // len(chars)) % len(chars)
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
