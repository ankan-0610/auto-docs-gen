from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import os

# # Compile the language grammars
# Language.build_library(
#     # Store the compiled shared library in the `build` directory
#     "build/my-languages.so",
#     # Include the paths to the language grammar repositories
#     [
#         "vendor/tree-sitter-python",  # Python
#         "vendor/tree-sitter-javascript",  # JavaScript
#         "vendor/tree-sitter-java",  # Java
#         "vendor/tree-sitter-go",  # Go
#         "vendor/tree-sitter-rust",  # Rust
#         "vendor/tree-sitter-c",  # C
#         "vendor/tree-sitter-cpp",  # C++
#     ],
# )

# Now you can use the respective languages like this
PYTHON_LANGUAGE = Language(tspython.language())
# JAVASCRIPT_LANGUAGE = Language("build/my-languages.so", "javascript")
# JAVA_LANGUAGE = Language("build/my-languages.so", "java")
# GO_LANGUAGE = Language("build/my-languages.so", "go")
# RUST_LANGUAGE = Language("build/my-languages.so", "rust")
# C_LANGUAGE = Language("build/my-languages.so", "c")
# CPP_LANGUAGE = Language("build/my-languages.so", "cpp")

# Initialize the parser
parser = Parser(PYTHON_LANGUAGE)

class ASTNode:
    """Represents a node in the in-memory AST."""

    def __init__(self, node_type, name, parent=None):
        self.node_type = node_type  # "function", "class", "module"
        self.name = name
        self.parent = parent
        self.children = []
        self.references = []  # list of ASTNode objects being called

    def add_child(self, child):
        self.children.append(child)

    def add_reference(self, ref_node):
        self.references.append(ref_node)

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
        indent_str = "  " * indent
        print(f"{indent_str}{node.node_type}: {node.name}")
        if node.references:
            for ref in node.references:
                print(f"{indent_str}  -> references: {ref.node_type}({ref.name})")
        for child in node.children:
            self._display_helper(child, indent + 1)


class ASTBuilder:
    def __init__(self, code: bytes):
        self.code = code
        self.tree = parser.parse(code)
        self.symbol_table = {}  # name -> ASTNode
        self.instance_bindings = {}  # name -> ASTNode
        self.store = ASTStore()

    def build(self):
        root = self.tree.root_node
        module_node = ASTNode("module", "module")
        self._traverse(root, module_node)
        self.store.add_node(module_node)
        return self.store

    def _traverse(self, node, parent, class_context=None, function_context=None):
        # Handle class definitions
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            class_name = name_node.text.decode()
            class_node = ASTNode("class", class_name, parent)
            self.symbol_table[class_name] = class_node
            if parent:
                parent.add_child(class_node)
            else:
                self.store.add_node(class_node)
            for child in node.children:
                self._traverse(child, class_node, class_node)

        # Handle function definitions
        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            func_name = name_node.text.decode()
            func_node = ASTNode("function", func_name, parent)
            if parent:
                parent.add_child(func_node)
            else:
                self.store.add_node(func_node)
            self.symbol_table[func_name] = func_node
            for child in node.children:
                self._traverse(child, func_node, class_context)
        # Handle call expressions
        elif node.type == "call":
            func_node = node.child_by_field_name("function")
            if func_node is not None:
                call_text = self._get_node_text(func_node)
                ref = self._resolve_reference(call_text, class_context)
                if ref and parent:
                    parent.references.append(ref)

        # Handle instance assignments: g = Greeter(...)
        elif node.type == "assignment":
            left_node = node.child_by_field_name("left")
            right_node = node.child_by_field_name("right")
            if left_node and right_node:
                left_text = self._get_node_text(left_node)
                if right_node.type == "call":
                    constructor_node = right_node.child_by_field_name("function")
                    if constructor_node:
                        constructor_text = self._get_node_text(constructor_node)
                        if constructor_text in self.symbol_table:
                            self.instance_bindings[left_text] = constructor_text

        # Recurse
        for child in node.children:
            self._traverse(child, parent, class_context)

    def _resolve_reference(self, name, class_context):
        if "." in name:
            base, method = name.split(".", 1)
            if base == "self" and class_context:
                for child in class_context.children:
                    if child.name == method and child.node_type == "function":
                        return child
            elif base in self.symbol_table:
                class_node = self.symbol_table[base]
                for child in class_node.children:
                    if child.name == method and child.node_type == "function":
                        return child
            elif base in self.instance_bindings:
                class_name = self.instance_bindings[base]
                class_node = self.symbol_table.get(class_name)
                if class_node:
                    for child in class_node.children:
                        if child.name == method and child.node_type == "function":
                            return child
        elif name in self.symbol_table:
            return self.symbol_table[name]
        return None

    def _get_node_text(self, node):
        return self.code[node.start_byte : node.end_byte].decode()


def analyze_codebase(directory):
    """
    Traverse a directory, analyze Python files using Tree-sitter, and collect functions, classes, and modules.
    """
    analysis_result = {"functions": [], "classes": [], "modules": []}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Analyze only Python files
                filepath = os.path.join(root, file)
                with open(filepath, "rb") as f:
                    code = f.read()
                    result = ASTBuilder(code).build()
                    analysis_result["functions"].extend(result["functions"])
                    analysis_result["classes"].extend(result["classes"])
                    analysis_result["modules"].extend(result["modules"])

    return analysis_result

code_snippet = b"""
class Greeter:
    def __init__(self, name):
        self.name = name
        self.say_hello()

    def say_hello(self):
        print("Hello", self.name)

def main():
    g = Greeter("Ankan")
    g.say_hello()
"""