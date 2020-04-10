from typing import List


class Path:
    id: int # a dummy field


class Node:
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
    cardinality: int


class Region:
    begin: Position
    end: Position


class Step:
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
    positionPercent: float
    inversionPercent: float
    rowRegion: List[Region] # [[1,4], [7,11]]

    def __init__(self):
        self.rowRegion = []


class Bin:
    binRank: List # List[Bin]
    binEdge: List[int]
    binRegion: List[Region]

    def __init__(self):
        self.binRank = []
        self.binEdge = []
        self.binRegion = []


class Link:
    arrival: List[Bin]
    departure: List[Bin]
    paths: List[Path]

    def __init__(self):
        self.arrival = []
        self.departure = []
        self.paths = []


class Component:
    componentEdge: List # List[Component]
    componentRank: List[int]
    bins: List[Bin]
    rows: List[Row]

    def __init__(self):
        self.bins = []
        self.rows = []


class ZoomLevel:
    zoomFactor: List[int]
    components: List[Component]

    def __init__(self):
        self.zoomFactor = []
        self.components = []
