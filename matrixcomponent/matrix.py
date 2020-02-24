"""Python object models to be manipulated"""
import json
import math
from bisect import bisect

from dataclasses import dataclass
from typing import List, Any, Set


## Path is all for input files
from math import ceil

from matrixcomponent import JSON_VERSION


class Path:
    name: str
    links: 'List[Path.LinkEntry]'
    bins: 'List[Path.Bin]'

    def __init__(self, name=''):
        self.name = name
        self.bins = []  # Bin
        self.links = []  # LinkEntry
        self._bin_set = set()

    @dataclass
    class Bin:
        bin_id: int
        coverage: float
        inversion_rate: float
        first_nucleotide: int
        last_nucleotide: int
        sequence: str = ''

    class LinkEntry:
        def __init__(self, upstream, downstream):
            self.upstream = upstream
            self.downstream = downstream
            # TODO: self.insert_size will require a topology search to find this

    def __contains__(self, item):  # used by " x in Path "
        return item in self._bin_set

    def finalize_bins(self):
        self._bin_set = {x.bin_id for x in self.bins}  # build and cache a set



## For Output to RDF  ###########
@dataclass
class LinkColumn:
    upstream: int
    downstream: int
    participants: List[bool]  # in order path_names, true if the individual participates in this LinkColumn
    # participants depends on row ordering of path names, optimized precompute for display


@dataclass
class Bin:
    coverage: float
    inversion: float
    first_nucleotide: int
    last_nucleotide: int


class Component:
    """Block of co-linear variation within a Graph Matrix
        # bin_id and seq are global to column and could be reduced to save memory,
        # careful construction can reuse Bin.sequence memory pointer"""
    first_bin: int
    last_bin: int
    occupants: List[bool]
    matrix: List[List[Bin]]
    arrivals: List[LinkColumn]
    departures: List[LinkColumn]

    def __init__(self, first_bin: int, last_bin: int):
        self.first_bin = first_bin
        self.last_bin = last_bin
        self.occupants = []
        self.matrix = []
        self.arrivals = []  # reverse ordered Links
        self.departures = []  # ordered Links


@dataclass
class PangenomeSchematic:
    json_version: int
    bin_size: int
    first_bin: int
    last_bin: int
    components: List[Component]
    path_names: List[str]
    total_nr_files: int

    def json_dump(self):
        def dumper(obj):
            if isinstance(obj, Bin):  # should be in Bin class def
                return [obj.coverage, obj.inversion, obj.first_nucleotide, obj.last_nucleotide]
            if isinstance(obj, set):
                return list(obj)
            try:
                return obj.__dict__
            except:
                return obj

        return json.dumps(self, default=dumper, indent=2)

    def update_first_last_bin(self):
        self.first_bin = 1  # these have not been properly initialized
        self.last_bin = self.components[-1].last_bin

    def split(self, cells_per_file):
        """Splits one Schematic into multiple files with their own
        unique first and last_bin based on the volume of data desired per
        file specified by cells_per_file.  """
        bins_per_file = ceil(cells_per_file / len(self.path_names))
        # bins_per_schematic = bins_per_row * self.bin_size
        self.update_first_last_bin()
        self.total_nr_files = ceil(self.last_bin / bins_per_file)
        partitions = []
        borders = [c.last_bin for c in self.components]
        cut_points = [0]

        # variables cut and end_cut are componentIDs
        # binIDs are in components.{first,last}_bin

        prev_point = 0
        for start_bin in range(0, self.last_bin, bins_per_file):
            cut = bisect(borders, start_bin + bins_per_file)
            cut_points.append(max(prev_point + 1, cut))
            prev_point = cut
        # cut_points.append(len(self.components))  # don't chop of dangling end

        bin2file_mapping = []
        for i, cut in enumerate(cut_points[:-1]):
            end_cut = cut_points[i + 1]
            these_comp = self.components[cut:end_cut]
            partitions.append(
                PangenomeSchematic(JSON_VERSION,
                                   self.bin_size,
                                   these_comp[0].first_bin,
                                   these_comp[-1].last_bin,
                                   these_comp, self.path_names, self.total_nr_files))
            bin2file_mapping.append({"first_bin": these_comp[0].first_bin, "file": self.filename(i)})
        return partitions, bin2file_mapping

    def pad_file_nr(self, file_nr):
        return str(file_nr).zfill(int(math.log10(self.total_nr_files)))

    def filename(self, nth_file):
        return f'chunk{self.pad_file_nr(nth_file)}_bin{self.bin_size}.schematic.json'

    def write_index_file(self, folder, bin2file_mapping):
        """Also write the file2bin mapping into a master json file
        eventually, this could have one list per bin size,
        with all bin size integrated into the same folder"""
        index_file = folder.joinpath(f'bin2file.json')
        file_contents = {'bin_size': self.bin_size,
                         'json_version': JSON_VERSION,
                         'last_bin': self.last_bin,
                         'files': bin2file_mapping}
        with index_file.open('w') as out:
            out.write(json.dumps(file_contents, indent=4))
            print("Saved file2bin mapping to", index_file)