import pydotplus as pydot
import glob
from itertools import takewhile

DEBUG = True

class NodeDiagram():

    # Fill colors for given node types
    node_colors = {
    "title"              : "white",
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

        file = open("structure_%s.txt" % name, "r")
        self.source = file.read().split("\n")
        self.num_lines = len(self.source)
        self.depth = []

        for i in range (0, len(self.source)):
            self.source[i] = self.source[i].rstrip()
            self.depth.append(self.source[i].count(' '))

        for x in self.depth:
            for y in range(0, x):
                print(" ", end="")
            print(x)

        self.graph = pydot.Dot(graph_type = "graph")

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
        ID = str(self.node_id) + '*'
        self.graph.add_node(pydot.Node(ID, label="...", style="filled", 
                                           fillcolor=self.node_colors[node_type]))
        self.graph.add_edge(pydot.Edge(str(parent_id), ID))
        
    def generate_graph(self):
        # A graph can only be generated once per NodeDiagram
        if self.generated:
            if DEBUG: print("Graph has already been generated")
            return
        else:
            if DEBUG: print('\n' + self.name)
            self.__create_node("title")
            self.__recursive_generate(None, 0, 0)
            self.generated = True

    def __recursive_generate(self, parent_id, last_depth, line_num):
        # parent_id can be None or int, so its print statement is separate
        if DEBUG: print("recursive_generate(", end="")
        if DEBUG: print(parent_id)

        last_line = self.source[line_num]
        # If the line doesn't exist, return
        while line_num < self.num_lines:
            current_depth = self.source[line_num].count(" ")
            if(current_depth == last_depth):
                break
            
            # Get addendum if it exists
            if ':' in last_line: addendum = "\n<" + last_line.split(':')[1] + ">"
            else:                addendum = ""

            # Get the node type and create the node
            node_type = last_line.strip().split(':')[0].replace('*', "")
            this_node_id = self.__create_node(node_type, addendum)

            if current_depth >= last_depth:
                # Attach to parent
                if parent_id is not None:
                    self.__add_child(parent_id, this_node_id)
                last_line = self.__recursive_generate(this_node_id, current_depth+1, line_num+1)

        return last_line

        # while True:
        #     line = self.file.readline().rstrip()
        #     if not line: return
        #     print(line)

        #     current_depth = line.count(' ')
        #     if current_depth < last_depth: return

        #     if ':' in line: addendum = "\n<" + line.split(':')[1] + ">"
        #     else:           addendum = ""

        #     node_type = line.strip().split(':')[0].replace('*', "")

        #     self.__create_node( node_type, addendum )

        #     if parent_id is not None:
        #         self.__add_child(parent_id, self.node_id)

        #         if( line[-1:] == '*' ):
        #             if DEBUG: print(" |--> multi")
        #             self.__attach_ellipse( node_type, parent_id )
        #     line = self.__recursive_generate(self.node_id, current_depth+1)

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
    quick_make()

if __name__ == "__main__":
    main()
