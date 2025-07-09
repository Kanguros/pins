import re
import sys
from pathlib import Path

doc = """
Pattern to find code blocks like this:

```python file=example/module1.py
```

To be replaced with the actual code from the specified file, like this:
```python file=example/module1.py

def example_function():
    print("This is an example function.")

```

Usage:

python update_readme.py FILE1 [FILE2 ...]

"""


def replace_code_block(match):
    language = match.group(1)
    code_file_path = match.group(2)
    line_start = match.group(3)
    line_end = match.group(4)

    # If no file=, treat as error and exit (per test expectation)
    if not code_file_path:
        print("Missing file attribute in code block.", file=sys.stderr)
        sys.exit(1)
    code_file_path = code_file_path.strip()
    code_path = Path(code_file_path)
    if not code_path.exists():
        print(f"Code file {code_file_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    if not language:
        language = ""
    else:
        language = language.strip().replace("`", "")
    file_lines = code_path.read_text().splitlines()
    if line_start:
        try:
            line_start_int = int(line_start)
        except Exception:
            print(
                f"Invalid line_start: {line_start} for file {code_file_path}.",
                file=sys.stderr,
            )
            sys.exit(1)
        if line_start_int < 1:
            print(
                f"Invalid line_start: {line_start} for file {code_file_path}.",
                file=sys.stderr,
            )
            sys.exit(1)
        start = line_start_int - 1
        if line_end:
            try:
                end = int(line_end)
            except Exception:
                print(
                    f"Invalid line_end: {line_end} for file {code_file_path}.",
                    file=sys.stderr,
                )
                sys.exit(1)
            if end > len(file_lines) or start >= end:
                print(
                    f"Invalid line range: {line_start}-{line_end} for file {code_file_path}.",
                    file=sys.stderr,
                )
                sys.exit(1)
            code_content = "\n".join(file_lines[start:end])
        else:
            if start >= len(file_lines):
                print(
                    f"Invalid line_start: {line_start} for file {code_file_path}.",
                    file=sys.stderr,
                )
                sys.exit(1)
            code_content = "\n".join(file_lines[start:])
    elif line_end:
        print(
            f"line_end provided without line_start for file {code_file_path}.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        code_content = "\n".join(file_lines)
    # Reconstruct the original code block header
    header = f"```{language} file={code_file_path}"
    if line_start:
        header += f" line_start={line_start}"
    if line_end:
        header += f" line_end={line_end}"
    header += "\n"
    return f"{header}{code_content}\n```"


def replace_tokens(file_path: str) -> None:
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"File {file_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    content = file_path.read_text()
    if not content:
        return
    pattern = r"```(\w+)\s+file=([^\s]+)(?:\s+line_start=(-?\d+))?(?:\s+line_end=(-?\d+))?\n(.*?)```"
    try:
        updated_content = re.sub(
            pattern,
            lambda m: replace_code_block(m) if m else m.group(0),
            content,
            flags=re.DOTALL,
        )
        if updated_content != content:
            file_path.write_text(updated_content)
            print(f"{file_path}")
        return
    except SystemExit:
        raise
    except Exception as e:
        print(f"update_readme.py error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(doc, file=sys.stderr)
        sys.exit(1)

    for argv in sys.argv[1:]:
        replace_tokens(argv)
