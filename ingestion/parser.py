import ast
from dataclasses import dataclass, field

@dataclass
class FunctionInfo:
    name: str
    file_path: str
    start_line: int
    end_line: int
    docstring: str
    source: str
    calls: list[str] = field(default_factory=list)

@dataclass
class ClassInfo:
    name: str
    file_path: str
    start_line: int
    end_line: int
    docstring: str
    methods: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)

@dataclass
class ImportInfo:
    module: str
    names: list[str]
    is_from_import: bool
    line: int

@dataclass
class ParsedFile:
    file_path: str
    language: str
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[ImportInfo] = field(default_factory=list)
    parse_error: str | None = None

class _CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls: list[str] = []
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)

def _extract_source(source_lines, start, end):
    return "".join(source_lines[start - 1:end])

def _get_base_name(node):
    if isinstance(node, ast.Name): return node.id
    elif isinstance(node, ast.Attribute): return node.attr
    return ""

def parse_python_file(file_path: str, content: str) -> ParsedFile:
    parsed = ParsedFile(file_path=file_path, language="python")
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        parsed.parse_error = str(e)
        return parsed
    source_lines = content.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cv = _CallVisitor()
            cv.visit(node)
            parsed.functions.append(FunctionInfo(
                name=node.name, file_path=file_path,
                start_line=node.lineno, end_line=node.end_lineno or node.lineno,
                docstring=ast.get_docstring(node) or "",
                source=_extract_source(source_lines, node.lineno, node.end_lineno or node.lineno),
                calls=cv.calls,
            ))
        elif isinstance(node, ast.ClassDef):
            parsed.classes.append(ClassInfo(
                name=node.name, file_path=file_path,
                start_line=node.lineno, end_line=node.end_lineno or node.lineno,
                docstring=ast.get_docstring(node) or "",
                methods=[n.name for n in ast.walk(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))],
                bases=[_get_base_name(b) for b in node.bases],
            ))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parsed.imports.append(ImportInfo(module=alias.name, names=[alias.asname or alias.name], is_from_import=False, line=node.lineno))
        elif isinstance(node, ast.ImportFrom):
            parsed.imports.append(ImportInfo(module=node.module or "", names=[a.name for a in node.names], is_from_import=True, line=node.lineno))
    return parsed

def parse_file(file_path: str, content: str, extension: str) -> ParsedFile:
    if extension == ".py":
        return parse_python_file(file_path, content)
    return ParsedFile(file_path=file_path, language=extension.lstrip("."))
