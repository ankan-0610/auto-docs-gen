from ast_analyze import ASTBuilder

def read_lines_as_bytes(file_path, start_line, end_line):
    """
    Read text from a file from line x to line y and return as byte literal.

    Args:
        file_path (str): Path to the file to read
        start_line (int): First line to read (1-based index)
        end_line (int): Last line to read (inclusive)

    Returns:
        bytes: Content from line x to line y as bytes

    Raises:
        ValueError: If start_line > end_line or if line numbers are < 1
        FileNotFoundError: If file doesn't exist
    """
    # Validate line numbers
    if start_line < 1 or end_line < 1:
        raise ValueError("Line numbers must be positive integers")
    if start_line > end_line:
        raise ValueError("Start line cannot be greater than end line")

    lines = []
    lines_read = 0

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                if line_num > end_line:
                    break
                if line_num >= start_line:
                    lines.append(line)
                lines_read += 1

        # Check if requested lines exist
        if lines_read < start_line:
            raise ValueError(
                f"File only has {lines_read} lines, requested start line {start_line}"
            )

        # Join lines and convert to bytes
        text_content = "".join(lines)
        return text_content.encode("utf-8")

    except UnicodeDecodeError:
        # Fallback to binary mode if UTF-8 fails
        with open(file_path, "rb") as file:
            all_lines = file.readlines()
            selected_lines = all_lines[start_line - 1 : end_line]
            return b"".join(selected_lines)

# Read lines 3 to 5 as bytes
bytes_content = read_lines_as_bytes("ast_analyze.py", 33, 194)

builder = ASTBuilder(bytes_content)
store = builder.build()
store.display_ast()