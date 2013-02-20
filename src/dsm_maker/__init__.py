#!/usr/bin/env python
import sys
import os.path
import pydot
import cPickle
from collections import defaultdict

from . import svg_drawer as drawer


def store_graph(nodes, edges, filename, title):
    gd = drawer.GraphDrawer(filename, nodes, edges, title)
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


def pack(nodes, edges, deps):
    size = len(nodes)
    for packed_node in reversed(nodes):
        idx = nodes.index(packed_node)
        for n in range(idx + 1, size):
            it = nodes[n]
            its_deps = deps[it]
            if packed_node in its_deps:
                nodes.remove(packed_node)
                nodes.insert(n - 1, packed_node)
                break
        else:
            nodes.remove(packed_node)
            nodes.append(packed_node)
    return nodes, edges


def triangle_cluster(nodes, edges):
    if not nodes:
        return nodes, edges

    direct_deps = defaultdict(set)
    for a, b in edges:
        direct_deps[a].add(b)

    for k, v in direct_deps.items():
        old_deps = set(v)
        while True:
            for dep in list(v):
                v.update(direct_deps[dep])
            if v == old_deps:
                break
            old_deps = set(v)

    items = sorted(nodes, key=lambda n:count_dependencies(n, edges), reverse=True)
    grouped_items = []
    taken_items = set()
    old_items = list(items)
    while True:
        for k in list(items):
            if taken_items.issuperset(direct_deps[k]):
                grouped_items.append(k)
                taken_items.add(k)
                items.remove(k)
        if old_items == items:
            break
        old_items = list(items)
    nodes = grouped_items + list(items)
    return nodes, edges
    # nodes, edges = pack(nodes, edges, direct_deps)
    # return pack(nodes, edges, direct_deps)


def main(in_filename, out_filename, title):
    cache_filename = in_filename + ".pickle"
    if not os.path.exists(cache_filename):
        edges, nodes = load_graph(in_filename)
        with open(cache_filename, "w") as cache:
            cPickle.dump((edges, nodes), cache)
    with open(cache_filename) as cache:
        (edges, nodes) = cPickle.load(cache)
    #nodes, edges = recursive_cluster(nodes, edges)
    nodes, edges = triangle_cluster(nodes, edges)
    store_graph(list(nodes), edges, out_filename, title)
