#

class BaseDrawer(object):

    def __init__(self, filename, nodes, edges):
        self.filename = filename
        self.edges = edges
        self.nodes = nodes
        self.size = len(nodes)
        self.square_size = 1./self.size
        self.init()

    def draw_squares(self):
        for x, node_x in enumerate(self.nodes):
            for y, node_y in enumerate(self.nodes):
                if (node_y, node_x) in self.edges:
                    self.draw_square(x, node_x, y, node_y)

    def add_labels(self):
        self.add_vertical_labels()
        self.add_horizontal_labels()

    def add_vertical_labels(self):
        pass

    def add_horizontal_labels(self):
        pass

    def init(self):
        pass

    def draw_grid(self):
        pass

    def draw_square(self, x, node_x, y, node_y):
        pass

    def close(self):
        pass
