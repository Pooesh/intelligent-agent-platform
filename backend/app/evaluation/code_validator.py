
import re
import subprocess
import tempfile
from pathlib import Path


def validate_java_code(source_code: str) -> dict:
    """
    Validate Java source code by compiling it with javac.

    Automatically detects the public class name and uses
    the matching Java filename.

    The temporary directory is automatically deleted.
    """

    if not source_code or not source_code.strip():
        return {
            "passed": False,
            "stage": "validation",
            "reason": "Java source code is empty.",
        }

    # Detect the public top-level class, interface, enum or record.
    class_match = re.search(
        r"\bpublic\s+(?:(?:abstract|final|sealed|non-sealed)\s+)*"
        r"(?:class|interface|enum|record)\s+([A-Za-z_$][\w$]*)",
        source_code,
    )

    class_name = class_match.group(1) if class_match else "Main"

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = Path(temp_dir) / f"{class_name}.java"

        source_path.write_text(
            source_code,
            encoding="utf-8",
        )

        try:
            result = subprocess.run(
                ["javac", str(source_path)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=temp_dir,
                check=False,
            )

        except FileNotFoundError:
            return {
                "passed": False,
                "stage": "compilation",
                "reason": "Java compiler (javac) was not found.",
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "stage": "compilation",
                "reason": "Java compilation timed out.",
            }

        if result.returncode != 0:
            return {
                "passed": False,
                "stage": "compilation",
                "reason": result.stderr.strip(),
            }

        return {
            "passed": True,
            "stage": "compilation",
            "reason": f"Java source compiled successfully: {class_name}.java",
        }
