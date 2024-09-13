import ast
import os
import sys


def update_init_py(target_dir: str) -> int:
    init_file = os.path.join(target_dir, "__init__.py")

    if not os.path.exists(target_dir):
        print(f"Skipping non-existent folder: {target_dir}")
        return 2  # Error Code 2: Directory does not exist

    py_files = [
        f for f in os.listdir(target_dir) if f.endswith(".py") and f != "__init__.py"
    ]

    if not py_files:
        print(
            f"No Python files found in {target_dir}. Skipping __init__.py generation."
        )
        return 3  # Error Code 3: No Python files found

    import_lines = [
        "# This file is autogenerated by update_init.py script",
        "",  # Add a blank line before the imports
    ]
    all_classes = []

    for py_file in py_files:
        module_name = py_file.replace(".py", "")
        module_path = os.path.join(target_dir, py_file)

        # Parse the file to find class definitions
        with open(module_path, "r") as file:
            tree = ast.parse(file.read())

        classes = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]

        if classes:
            import_lines.append(f"from .{module_name} import {', '.join(classes)}")
            all_classes.extend(classes)

    # Add __all__ definition
    import_lines.append("\n__all__ = [")
    for class_name in all_classes:
        import_lines.append(f"    '{class_name}',")
    import_lines.append("]")

    # Write to __init__.py
    try:
        with open(init_file, "w") as init_f:
            init_f.write("\n".join(import_lines) + "\n")
        print(f"Successfully updated {init_file}")
        return 0  # Success
    except IOError as e:
        print(f"Failed to write to {init_file}: {e}")
        return 4  # Error Code 4: IOError during file writing


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python update_init.py <target_directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    result = update_init_py(target_dir)
    sys.exit(result)


if __name__ == "__main__":
    main()
