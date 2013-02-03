#!/usr/bin/env python
import sys
import math
import os.path
import cairo
import rsvg
import math
import pydot
import cPickle
import collections


def draw_grid(ctx, elements):
    square_size = 1./elements
    for n in range(elements):
        ctx.move_to(n * square_size, 0)
        ctx.line_to(n * square_size, 1)

        ctx.move_to(0, n * square_size)
        ctx.line_to(1, n * square_size)

    ctx.set_source_rgb(0.3, 0.3, 0.3)
    ctx.set_line_width(0.0001)
    ctx.stroke()


def add_labels(ctx, nodes, size):
    square_size = 1./size
    for x, node_x in enumerate(nodes):
        ctx.set_source_rgb(0, 0, 1)
        ctx.set_font_size(square_size)
        ctx.move_to(0, (x + 1) * square_size);
        ctx.show_text(node_x.replace('"', ''))
    ctx.save()
    ctx.translate(0.5, 0.5)
    ctx.rotate(math.pi / 2)
    ctx.translate(-0.5, -0.5)
    for x, node_x in enumerate(reversed(nodes)):
        if x < (len(nodes) - 11):
            ctx.set_source_rgb(0, 0, 1)
            ctx.set_font_size(square_size)
            ctx.move_to(0, (x + 1) * square_size);
            ctx.show_text(node_x.replace('"', ''))
    ctx.restore()


def store_graph(nodes, edges, filename):
    fo = file(filename, 'w')
    WIDTH, HEIGHT  = 1200, 1200
    surface = cairo.SVGSurface(fo, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(WIDTH/1.0, HEIGHT/1.0) # Normalizing the canvas
    size = len(nodes)
    draw_grid(ctx, size)

    square_size = 1./size
    for x, node_x in enumerate(nodes):
        for y, node_y in enumerate(nodes):
            if (node_y, node_x) in edges:
                ctx.rectangle(x * square_size, y * square_size,
                              square_size, square_size)
                ctx.set_source_rgb(0, 0, 0)
                ctx.fill()
    add_labels(ctx, nodes, size)
    surface.finish()


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

def export_dt(noded, edges, out_filename):
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
