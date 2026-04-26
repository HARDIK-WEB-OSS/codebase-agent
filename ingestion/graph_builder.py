from dataclasses import dataclass, field
from pathlib import Path
import networkx as nx
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.file_walker import walk_repo
from ingestion.parser import parse_file, ParsedFile

@dataclass
class GraphResult:
    repo_name: str
    graph: nx.DiGraph
    parsed_files: list[ParsedFile] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0

def build_graph(repo_path: Path) -> GraphResult:
    G = nx.DiGraph()
    walk_result = walk_repo(repo_path)
    parsed_files = []
    func_to_file: dict[str, str] = {}
    for code_file in walk_result.files:
        parsed = parse_file(code_file.relative_path, code_file.content, code_file.extension)
        parsed_files.append(parsed)
        file_node = code_file.relative_path
        G.add_node(file_node, type="file", language=parsed.language)
        for func in parsed.functions:
            fn = f"{file_node}::{func.name}"
            G.add_node(fn, type="function", name=func.name, file=file_node,
                start_line=func.start_line, end_line=func.end_line,
                docstring=func.docstring, source=func.source)
            G.add_edge(file_node, fn, relation="contains")
            func_to_file[func.name] = file_node
        for cls in parsed.classes:
            cn = f"{file_node}::{cls.name}"
            G.add_node(cn, type="class", name=cls.name, file=file_node,
                start_line=cls.start_line, end_line=cls.end_line,
                docstring=cls.docstring, bases=cls.bases)
            G.add_edge(file_node, cn, relation="contains")
    for parsed in parsed_files:
        for func in parsed.functions:
            caller = f"{parsed.file_path}::{func.name}"
            if caller not in G:
                continue
            for called in func.calls:
                if called in func_to_file:
                    callee = f"{func_to_file[called]}::{called}"
                    if callee in G and callee != caller:
                        G.add_edge(caller, callee, relation="calls")
    return GraphResult(repo_name=repo_path.name, graph=G, parsed_files=parsed_files,
        node_count=G.number_of_nodes(), edge_count=G.number_of_edges())

def get_neighbors(G: nx.DiGraph, node: str, depth: int = 2) -> list[str]:
    reachable, frontier = set(), {node}
    for _ in range(depth):
        nf = set()
        for n in frontier:
            nf |= (set(G.successors(n)) | set(G.predecessors(n))) - reachable
        reachable |= frontier
        frontier = nf
    reachable.discard(node)
    return list(reachable)
