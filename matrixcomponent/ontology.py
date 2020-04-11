from typing import List
from rdflib import Namespace, Graph, Literal


class Path:
    id: str
    ns: Namespace

    def __init__(self):
        ns = Namespace("") # should be empty!

    def __str__(self):
        return "path" + str(self.id)  # path1

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns.term(self)  # str representation

        # add the object itself
        graph.add((self.ns, vg.Path, Literal(inner_ns))) # todo: check if indeed vg:Path

        # add its properties, recursively if needed


class Node:
    id: str
    links: List # List[Node]
    linksForwardToForward: List # List[Node]
    linksForwardToReverse: List # List[Node]
    linksReverseToForward: List # List[Node]
    linksReverseToReverse: List # List[Node]

    def __init__(self):
        self.links = []
        self.linksForwardToForward = []
        self.linksForwardToReverse = []
        self.linksReverseToForward = []
        self.linksReverseToReverse = []


class Region:
    ns: Namespace
    begin: int
    end: int

    def __init__(self):
        ns = Namespace("") # should be path1

    def __str__(self):
        return "region/" + str(self.begin) + "-" + str(self.end)  # region/2-10

    def ns_term(self):
        return self.ns.term(self.__str__()) # path1/...

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns_term()  # str representation

        # add the object itself
        graph.add((self.ns, "faldo:Region", Literal(inner_ns)))

        # add its properties, recursively if needed
        position = self.ns.term("position")
        graph.add((inner_ns, "faldo:begin", Literal(position.term(str(self.begin)))))
        graph.add((inner_ns, "faldo:end", Literal(position.term(str(self.end)))))


class Step:
    id: str
    node: List[Node]
    path: List[Path]
    position: List[int]
    rank: List[int]
    reverseOfNode: List[Node]

    def __init__(self):
        self.node = []
        self.path = []
        self.position = []
        self.rank = []
        self.reverseOfNode = []


class Row:
    id: str
    ns: Namespace
    positionPercent: float
    inversionPercent: float
    rowRegion: List[Region] # [[1,4], [7,11]]

    def __init__(self):
        self.rowRegion = []

    def __str__(self):
        return "row" + str(self.id)  # row1

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns.term(self)  # str representation

        # add the object itself
        graph.add((inner_ns, vg.Row, Literal(self.id)))

        # add its properties, recursively if needed
        graph.add((inner_ns, vg.positionPercent, Literal(self.positionPercent)))
        graph.add((inner_ns, vg.inversionPercent, Literal(self.inversionPercent)))
        for region in self.rowRegion:
            region.ns = inner_ns
            region.add_to_graph(graph, vg)


class Bin:
    ns: Namespace
    binRank: int
    binEdge: object # pointer to the next Bin
    binRegion: List[Region]

    def __init__(self):
        self.binEdge = None
        self.binRegion = []

    def __str__(self):
        return "bin" + str(self.binRank)  # bin1

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns.term(self)  # str representation

        # add the object itself
        graph.add((self.ns, vg.Bin, Literal(self)))

        # add its properties, recursively if needed
        graph.add((inner_ns, vg.binRank, Literal(self.binRank)))
        for region in self.binRegion:
            # !! region.ns is expected to be set when parsing the Path loop
            graph.add((inner_ns, vg.binRegion, Literal(region.ns_term())))  # can have multiple bins
            region.add_to_graph(graph, vg)

        # add the reference to another object if needed
        if self.binEdge is not None:
            graph.add((inner_ns, vg.binEdge, Literal(self.binEdge))) # __str__ will be called


class Link:
    id: str
    arrival: Bin
    departure: Bin
    paths: List[Path]

    def __init__(self):
        self.paths = []


class Component:
    id: str
    ns: Namespace
    componentEdge: object # Component
    componentRank: int
    bins: List[Bin]
    rows: List[Row]

    def __init__(self):
        self.componentEdge = None
        self.bins = []
        self.rows = []

    def __str__(self):
        return "group" + str(self.id) # group1

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns.term(self) # str representation

        # add the object itself
        graph.add((self.ns, vg.Component, Literal(self)))

        # add its properties, recursively if needed
        graph.add((inner_ns, vg.componentRank, Literal(self.id)))
        for bin in self.bins:
            bin.ns = inner_ns
            graph.add((inner_ns, vg.bins, Literal(bin.ns_term()))) # can have multiple bins
            bin.add_to_graph(graph, vg) # add the inner content of each

        for i,row in self.rows:
            row.ns = inner_ns
            graph.add((inner_ns, vg.bins, Literal(row.ns_term()))) # can have multiple rows
            row.add_to_graph(graph, vg) # add the inner content of each

        # add the reference to another object if needed
        if self.componentEdge is not None:
            graph.add((inner_ns, vg.componentEdge, Literal(self.componentEdge))) # __str__ will be called


class ZoomLevel:
    id: str
    ns: Namespace
    zoomFactor: int
    components: List[Component]

    def __init__(self):
        self.components = []

    def __str__(self):
        return "zoom" +  str(self.zoomFactor) #zoom1000

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns_term() # str representation

        # add the object itself
        graph.add((self.ns, vg.ZoomLevel, Literal(self)))

        # add its properties, recursively if needed
        graph.add((inner_ns, vg.zoomFactor, Literal(self.zoomFactor)))
        for i,comp in self.components:
            comp.ns = inner_ns
            comp.id = str(i+1) # from 1
            comp.add_to_graph(graph, vg)
