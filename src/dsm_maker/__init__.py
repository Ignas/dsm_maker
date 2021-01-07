#!/usr/bin/env python
import argparse
import os.path
import pydot
from simplegexf import Gexf, Edge
import pickle

from collections import defaultdict

from . import svg_drawer as drawer


def store_graph(nodes, edges, filename, title):
    gd = drawer.GraphDrawer(filename, nodes, edges, title)
    gd.draw_grid()
    gd.draw_squares()
    gd.add_labels()
    gd.close()


def load_graph_dot(filename):
    graph = pydot.dot_parser.parse_dot_data(open(filename).read())[0]
    nodes = set()
    edges = set()
    for edge_obj in graph.get_edges():
        edge = (edge_obj.get_source(), edge_obj.get_destination())
        nodes.add(edge[0])
        nodes.add(edge[1])
        edges.add(edge)

    return edges, nodes


def load_graph_gexf(filename):
    from lxml import etree
    doc = etree.parse(open(filename))
    ns = {"g": "http://www.gexf.net/1.2draft"}
    node_map = {}
    nodes = set()
    for node in doc.getroot().xpath(
            "//g:node", namespaces=ns):
        label = node.attrib['label']
        id = node.attrib['id']
        nodes.add(label)
        node_map[id] = label
    edges = set()
    for edge in doc.getroot().xpath(
            "//g:edge", namespaces=ns):
        source = node_map[edge.attrib['source']]
        target = node_map[edge.attrib['target']]
        edges.add((source, target))
    return edges, nodes


def load_graph(filename):
    if filename.endswith(".dot"):
        return load_graph_dot(filename)
    elif filename.endswith(".gexf"):
        return load_graph_gexf(filename)

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


def collect_transient_dependencies(edges):
    transient_dependency_map = defaultdict(set)
    for a, b in edges:
        transient_dependency_map[a].add(b)

    for v in list(transient_dependency_map.values()):
        old_deps = set(v)
        while True:
            for dep in list(v):
                v.update(transient_dependency_map[dep])
            if v == old_deps:
                break
            old_deps = set(v)
    return transient_dependency_map


def triangle_cluster(nodes, edges):
    if not nodes:
        return nodes, edges

    transient_deps = collect_transient_dependencies(edges)
    items = sorted(nodes, key=lambda n:count_dependencies(n, edges), reverse=True)
    grouped_items = []
    taken_items = set()
    old_items = list(items)
    while True:
        for k in list(items):
            if taken_items.issuperset(transient_deps[k]):
                grouped_items.append(k)
                taken_items.add(k)
                items.remove(k)
        if old_items == items:
            break
        old_items = list(items)
    nodes = grouped_items + list(items)
    return nodes, edges


def main():
    parser = argparse.ArgumentParser(description='Generate dependency structure matrix from a dot file.')
    parser.add_argument('input_file', help='input file (dot)')
    parser.add_argument('-t', '--title', help='graph title. Default: DSM', default='DSM')
    parser.add_argument('-o', '--output', help='output file (svg)')
    parser.add_argument('-c', '--cache', help='cache file (pickle)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--recursive_cluster", action="store_true")
    group.add_argument("--triangle_cluster", action="store_true", default=True)

    parser.add_argument('--pack', help='pack clusters N times', type=int, default=0)

    args = parser.parse_args()

    if args.cache:
        if not os.path.exists(args.cache):
            edges, nodes = load_graph(args.input_file)
            with open(args.cache, "w") as cache:
                pickle.dump((edges, nodes), cache)

        with open(args.cache) as cache:
            (edges, nodes) = pickle.load(cache)
    else:
        edges, nodes = load_graph(args.input_file)

    if args.recursive_cluster:
        nodes, edges = recursive_cluster(nodes, edges)
    elif args.triangle_cluster:
        nodes, edges = triangle_cluster(nodes, edges)

    for _ in range(args.pack):
        nodes, edges = pack(nodes, edges, collect_transient_dependencies(edges))

    if args.output:
        out_filename = args.output
    else:
        out_filename = "result.svg"

    store_graph(list(nodes), edges, out_filename, args.title)
