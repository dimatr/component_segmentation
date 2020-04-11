from typing import List
from rdflib import Namespace, Graph, Literal


class Path:
    id: str


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


class Position:
    id: str
    cardinality: int


class Region:
    id: str
    begin: Position
    end: Position


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


class Bin:
    ns: Namespace
    binRank: int
    binEdge: object # pointer to the next Bin
    binRegion: List[Region]

    def __init__(self):
        self.binEdge = []
        self.binRegion = []

    def __str__(self):
        return "bin" + str(self.binRank)  # bin1

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns.term(self)  # str representation
        graph.add((inner_ns, vg.binRank, Literal(self.binRank)))

        for region in self.binRegion:
            region.ns = inner_ns
            region.add_to_graph(graph, vg)

        edge = self.binEdge
        if edge is not None:
            graph.add((inner_ns, vg.binEdge, Literal(edge.__str__())))


class Link:
    id: str
    arrival: List[Bin]
    departure: List[Bin]
    paths: List[Path]

    def __init__(self):
        self.arrival = []
        self.departure = []
        self.paths = []


class Component:
    id: str
    ns: Namespace
    componentEdge: List # List[Component]
    componentRank: int
    bins: List[Bin]
    rows: List[Row]

    def __init__(self):
        self.bins = []
        self.rows = []

    def __str__(self):
        return "group" + str(self.id) # group1

    def ns_term(self):
        return self.ns.term(self.__str__())

    def add_to_graph(self, graph: Graph, vg: Namespace) -> None:
        inner_ns = self.ns.term(self) # str representation
        graph.add((inner_ns, vg.componentRank, Literal(self.id)))

        for bin in self.bins:
            bin.ns = inner_ns
            graph.add((inner_ns, vg.bins, Literal(bin.ns_term())))
            bin.add_to_graph(graph, vg)

        for i,row in self.rows:
            row.ns = inner_ns
            graph.add((inner_ns, vg.bins, Literal(row.ns_term())))
            row.add_to_graph(graph, vg)


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
        graph.add((self.ns, vg.zoomLevel, Literal(self))) # add the object itself

        # add its properties, recursively if needed
        graph.add((inner_ns, vg.zoomFactor, Literal(self.zoomFactor)))
        for i,comp in self.components:
            comp.ns = inner_ns
            comp.id = str(i+1) # from 1
            comp.add_to_graph(graph, vg)
