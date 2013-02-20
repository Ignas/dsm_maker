#!/usr/bin/env python
import sys
import math
import os.path
import cairo
import pydot
import cPickle


class GraphDrawer(object):

    def __init__(self, filename, nodes, edges):
        self.filename = filename
        self.edges = edges
        self.nodes = nodes
        self.size = len(nodes)
        self.square_size = 1./self.size
        fo = file(filename, 'w')
        WIDTH, HEIGHT  = 1200, 1200
        self.surface = cairo.SVGSurface(fo, WIDTH, HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(WIDTH/1.0, HEIGHT/1.0) # Normalizing the canvas

    def draw_grid(self):
        for n in range(self.size):
            self.ctx.move_to(n * self.square_size, 0)
            self.ctx.line_to(n * self.square_size, 1)

            self.ctx.move_to(0, n * self.square_size)
            self.ctx.line_to(1, n * self.square_size)

        self.ctx.set_source_rgb(0.3, 0.3, 0.3)
        self.ctx.set_line_width(0.0001)
        self.ctx.stroke()

    def draw_square(self, x, node_x, y, node_y):
        self.ctx.rectangle(x * self.square_size, y * self.square_size,
                           self.square_size, self.square_size)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.fill()

    def draw_squares(self):
        for x, node_x in enumerate(self.nodes):
            for y, node_y in enumerate(self.nodes):
                if (node_y, node_x) in self.edges:
                    self.draw_square(x, node_x, y, node_y)

    def add_vertical_labels(self):
        for x, node_x in enumerate(self.nodes):
            self.ctx.set_source_rgb(0, 0, 1)
            self.ctx.set_font_size(self.square_size)
            self.ctx.move_to(0, (x + 1) * self.square_size)
            self.ctx.show_text(node_x.replace('"', ''))

    def add_horizontal_labels(self):
        self.ctx.save()
        self.ctx.translate(0.5, 0.5)
        self.ctx.rotate(math.pi / 2)
        self.ctx.translate(-0.5, -0.5)
        for x, node_x in enumerate(reversed(self.nodes)):
            if x < (len(self.nodes) - 11):
                self.ctx.set_source_rgb(0, 0, 1)
                self.ctx.set_font_size(self.square_size)
                self.ctx.move_to(0, (x + 1) * self.square_size)
                self.ctx.show_text(node_x.replace('"', ''))
        self.ctx.restore()

    def add_labels(self):
        self.add_vertical_labels()
        self.add_horizontal_labels()

    def close(self):
        self.surface.finish()


def store_graph(nodes, edges, filename):
    gd = GraphDrawer(filename, nodes, edges)
    gd.draw_grid()
    gd.draw_squares()
    gd.add_labels()
    gd.close()


def load_graph(filename):
    graph = pydot.dot_parser.parse_dot_data(open(filename).read())
    nodes = set()
    edges = set()
    for edge_obj in graph.get_edges():
        edge = (edge_obj.get_source(), edge_obj.get_destination())
        nodes.add(edge[0])
        nodes.add(edge[1])
        edges.add(edge)

    # for node in graph.get_nodes():
    #     nodes.add(node.get_name())
    return edges, nodes


def count_dependencies(node, edges):
    return len([node for edge in edges if edge[1] == node])


def recursive_cluster(nodes, edges):
    if not nodes:
        return nodes, edges
    nodes = sorted(nodes, key=lambda n:count_dependencies(n, edges), reverse=True)
    top_node = nodes[0]
    my_nodes = []
    other_nodes = []
    for node in nodes[1:]:
        if (node, top_node) in edges:
            my_nodes.append(node)
        else:
            other_nodes.append(node)
    nodes = [nodes[0]] + recursive_cluster(my_nodes, edges)[0] + recursive_cluster(other_nodes, edges)[0]
    return nodes, edges

def format_node(node):
    node = node.replace('"', '').replace(' ', '')
    n = 0
    return "%d {%s}" % (n, node)

def export_dt(nodes, edges, out_filename):
    lines = []
    for node in nodes:
        lines.append(format_node(node))
    for edge in edges:
        lines.append(format_node(edge[0]) + ":" + format_node(edge[1]))
    lines.append("")
    return "\n".join(lines)

def main(in_filename, out_filename):
    cache_filename = in_filename + ".pickle"
    if not os.path.exists(cache_filename):
        edges, nodes = load_graph(in_filename)
        with open(cache_filename, "w") as cache:
            cPickle.dump((edges, nodes), cache)
    with open(cache_filename) as cache:
        (edges, nodes) = cPickle.load(cache)
    nodes, edges = recursive_cluster(nodes, edges)
    export_dt(nodes, edges, in_filename + ".dt")
    store_graph(list(nodes), edges, out_filename)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        in_filename = sys.argv[1]
    else:
        in_filename = "graph.dot"
    if len(sys.argv) > 2:
        out_filename = sys.argv[2]
    else:
        out_filename = "result.svg"
    main(in_filename, out_filename)
