from tree_sitter import Language, Parser
import os

# Compile the language grammars
Language.build_library(
    # Store the compiled shared library in the `build` directory
    "build/my-languages.so",
    # Include the paths to the language grammar repositories
    [
        "vendor/tree-sitter-python",  # Python
        "vendor/tree-sitter-javascript",  # JavaScript
        "vendor/tree-sitter-java",  # Java
        "vendor/tree-sitter-go",  # Go
        "vendor/tree-sitter-rust",  # Rust
        "vendor/tree-sitter-c",  # C
        "vendor/tree-sitter-cpp",  # C++
    ],
)

# Now you can use the respective languages like this
PYTHON_LANGUAGE = Language("build/my-languages.so", "python")
JAVASCRIPT_LANGUAGE = Language("build/my-languages.so", "javascript")
JAVA_LANGUAGE = Language("build/my-languages.so", "java")
GO_LANGUAGE = Language("build/my-languages.so", "go")
RUST_LANGUAGE = Language("build/my-languages.so", "rust")
C_LANGUAGE = Language("build/my-languages.so", "c")
CPP_LANGUAGE = Language("build/my-languages.so", "cpp")

# Initialize the parser
parser = Parser()
parser.set_language(PYTHON_LANGUAGE)


class ASTNode:
    """Represents a node in the in-memory AST."""

    def __init__(self, node_type, name, parent=None):
        self.node_type = node_type  # "function", "class", "module"
        self.name = name
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"{self.node_type}({self.name})"


class ASTStore:
    """In-memory store for AST."""

    def __init__(self):
        self.modules = {}

    def add_node(self, node, module_name="module"):
        if module_name not in self.modules:
            self.modules[module_name] = ASTNode("module", module_name)
        self.modules[module_name].add_child(node)

    def get_module(self, module_name):
        return self.modules.get(module_name, None)

    def display_ast(self, module_name="module", indent=0):
        """Recursively display the AST in a tree format."""
        module = self.get_module(module_name)
        if module:
            self._display_helper(module, indent)

    def _display_helper(self, node, indent):
        print("  " * indent + f"{node.node_type}: {node.name}")
        for child in node.children:
            self._display_helper(child, indent + 1)


def analyze_code(code, parser):
    """
    Analyze code using Tree-sitter and store AST in-memory.
    """
    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node
    ast_store = ASTStore()

    def traverse_node(node, parent=None):
        if node.type == "function_definition":
            function_name = node.child_by_field_name("name").text.decode("utf-8")
            func_node = ASTNode("function", function_name, parent)
            if parent:
                parent.add_child(func_node)
            ast_store.add_node(func_node)

        elif node.type == "class_definition":
            class_name = node.child_by_field_name("name").text.decode("utf-8")
            class_node = ASTNode("class", class_name, parent)
            if parent:
                parent.add_child(class_node)
            ast_store.add_node(class_node)
            parent = class_node  # Make this class the new parent for nested functions

        for child in node.children:
            traverse_node(child, parent)

    traverse_node(root_node)
    return ast_store


def analyze_codebase(directory):
    """
    Traverse a directory, analyze Python files using Tree-sitter, and collect functions, classes, and modules.
    """
    analysis_result = {"functions": [], "classes": [], "modules": []}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Analyze only Python files
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    code = f.read()
                    result = analyze_code(code)
                    analysis_result["functions"].extend(result["functions"])
                    analysis_result["classes"].extend(result["classes"])
                    analysis_result["modules"].extend(result["modules"])

    return analysis_result
