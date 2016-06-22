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
            if node_type == "root":
                label = self.name
            else:
                label = node_type + addendum
            self.graph.add_node(pydot.Node(str(self.node_id), label=label, style="filled",
                                                              fillcolor=self.node_colors[node_type]))

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
            self.__create_node("root")
            self.__recursive_generate(None, 0)
            self.generated = True

    def __recursive_generate(self, parent_id, depth):
        # parent_id can be None or int, so print its statement is separate
        if DEBUG: print("recursive_generate(", end="")
        if DEBUG: print(parent_id, end="")
        if DEBUG: print(", %d)" % depth )

        while True:
            line = self.file.readline().rstrip()
            if not line: break
            print(line)

            addendum = ""
            if ':' in line:
                addendum += "\n<" + line.split(':')[1] + ">"

            node_type = line.strip().split(':')[0].replace('*', "")
            level = line.count(' ')
            if level < depth: break

            self.__create_node( node_type, addendum )
            if parent_id is not None:
                self.__add_child(parent_id, self.node_id)

                if( line[-1:] == '*' ):
                    if DEBUG: print(" |--> multi")
                    self.__attach_ellipse( node_type, parent_id )
            line = self.__recursive_generate(self.node_id, level+1)
            
        return line

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
