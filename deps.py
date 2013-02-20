#!/usr/bin/env python
import sys
import os.path
import pydot
# import cairo_drawer as drawer
import svg_drawer as drawer
import cPickle


def store_graph(nodes, edges, filename):
    gd = drawer.GraphDrawer(filename, nodes, edges)
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
