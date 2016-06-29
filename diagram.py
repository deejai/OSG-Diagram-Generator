import pydotplus as pydot
import glob
from itertools import takewhile

DEBUG = True

# class OsgNode(pydot.Node):
#
#     def __init__(self, node_type, addendum, depth):
#         super(self, OsgNode).__init__()

class NodeDiagram():

    # Fill colors for given node types
    node_colors = {
    "title"             : "white",
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
        self.ellipse_id = '*'
        self.iterator = 0
        self.generated = False

        file = open("structure_%s.txt" % name, "r")
        self.source = file.read().split("\n")
        self.depth        = []
        self.node_types   = []
        self.addendums    = []
        self.is_multinode = []
        self.node_ids     = []

        # Create a blank pydot graph
        self.graph = pydot.Dot(graph_type = "graph")

        # Initialize arrays
        for i in range (0, len(self.source)):
            self.source[i] = self.source[i].rstrip()
            
            # Get the node types
            self.node_types.append(self.source[i].strip().split(":")[0])

            # Determine if the node likely has multiples
            self.is_multinode.append(self.node_types[i][-1:] == "*")
            self.node_types[i] = self.node_types[i].replace("*", "")

            # Get the node depths
            self.depth.append(self.source[i].count(" "))
            
            # Get addendum if it exists
            if ":" in self.source[i]:
                self.addendums.append("\n<" + self.source[i].split(":")[1] + ">")
            else:
                self.addendums.append("")

            # Create each pydot node and store their ids
            self.node_ids.append(self.__create_node(self.node_types[i], self.addendums[i]))

    def __get_last_tag(self):
        return str(self.node_id) + self.tag

    def __add_child(self, parent_id, child_id):
        if DEBUG: print("add_child(%d, %d)" % (parent_id, child_id), end="" )
        if parent_id > self.node_id:
            if DEBUG: print(" ERROR\nInvalid parent_id: %d. Current node_id: %d"
                                           % (parent_id, self.node_id) )
            exit()
        else:
            self.graph.add_edge(pydot.Edge(str(parent_id), str(child_id)))
            if DEBUG: print(" Complete.")

    def __create_node(self, node_type, addendum=""):
        if DEBUG: print("create_node(%s) (node_id: " % node_type, end="")
        
        if node_type not in self.node_colors:
            if DEBUG: print("ERROR)\nInvalid node_type: %s" % node_type)
            exit()
        else:
            self.node_id += 1
            if DEBUG: print("%s, addednum: %s)" % (self.__get_last_tag(), addendum.replace("\n", "")) )
            if node_type == "title":
                label = self.name
            else:
                label = node_type + addendum
            self.graph.add_node(pydot.Node(str(self.node_id), label=label, style="filled",
                                                              fillcolor=self.node_colors[node_type]))
            return self.node_id

    def __attach_ellipse(self, node_type, parent_id):
        # Add indicator that multiple nodes of the given type likely exist
        # Creates a node, but doesn't increment self.node_id
        ID = self.ellipse_id
        self.ellipse_id += "*"
        self.graph.add_node(pydot.Node(ID, label="...", style="filled", 
                                           fillcolor=self.node_colors[node_type]))
        self.graph.add_edge(pydot.Edge(str(parent_id), ID))
        
    def generate_graph(self):
        # A graph can only be generated once per NodeDiagram
        if self.generated:
            if DEBUG: print("Graph has already been generated")
            return
        else:
            if DEBUG: print("\n" + self.name)
            self.__create_node("title")
            self.__generate_edges()
            self.generated = True

    def __generate_edges(self):
        stack = []
        for x in range(len(self.node_ids)):
            depth = self.depth[x]
            stack[depth:] = [self.node_ids[x]]
            print(stack)

            if(len(stack) > 1):
                self.__add_child(stack[-2], stack[-1])
                if(self.is_multinode[x]):
                    self.__attach_ellipse(self.node_types[x], stack[-2])

    def generate_file(self):
        if not self.generated:
            if DEBUG: print("PNG file cannot be generated until the graph is generated")
        else:
            self.graph.write_png(self.name + ".png")

def quick_make():
    chars = "abcdefghijklmnopqrstuvwxyz"
    i = 0
    # for each .txt file beginning with "structure_", generate a graph and a .png
    for file in glob.glob("structure_*.txt"):
        # provides a unique id for up to (len(chars) * len(chars)) entries
        char1 = (i // len(chars)) % len(chars)
        char2 = i % len(chars)
        tag = chars[char1] + chars[char2]

        diagram = NodeDiagram(file.replace("structure_", "").replace(".txt", ""), tag)
        diagram.generate_graph()
        diagram.generate_file()
        i += 1

def main():
    # quick_make()
    test = NodeDiagram("FEATURE_SWITCH")
    test.generate_graph()
    test.generate_file()

if __name__ == "__main__":
    main()
