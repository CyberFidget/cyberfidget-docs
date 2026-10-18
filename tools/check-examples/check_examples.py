# SPDX-License-Identifier: CC-BY-SA-4.0
"""Compile Markdown examples using the firmware's device-app recipe."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import fnmatch
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

TOOL = Path(__file__).resolve().parent
REPO = TOOL.parent.parent
LANGUAGES = {"cpp", "c++", "c", "arduino", "ino"}


@dataclass
class Block:
    page: str
    line: int
    code: str
    language: str
    skip: str = ""


def looks_cpp(code):
    return bool(re.search(
        r"^\s*#\s*include\s*[<\"]|\bvoid\s+\w+\s*\(|"
        r"\bclass\s+\w+\s*\{|\bHAL::\w+|\b(?:display|d)\.\w+\([^\n]*;",
        code, re.M))


def extract(path, root):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        opening = re.match(r"^\s*(`{3,}|~{3,})\s*([^\s]*)[^\n]*$", lines[i])
        if not opening:
            i += 1
            continue
        fence, language = opening.groups()
        start = i
        i += 1
        body = []
        while i < len(lines) and not re.match(
                r"^\s*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", lines[i]):
            body.append(lines[i])
            i += 1
        code = textwrap.dedent("\n".join(body)) + "\n"
        marker = re.fullmatch(r"\s*<!--\s*check-examples:\s*skip\s*-\s*(.+?)\s*-->\s*",
                              lines[start - 1] if start else "", re.I)
        reason = marker.group(1).strip() if marker else ""
        if language.lower() in LANGUAGES or (not language and looks_cpp(code)):
            blocks.append(Block(path.relative_to(root).as_posix(), start + 2,
                                code, language.lower(), reason))
        i += 1
    return blocks


def classify(block):
    if block.skip:
        return "skipped", block.skip
    if not block.language:
        return "untagged", "tag this block cpp, or text if it is not code"
    first = block.code.splitlines()[0] if block.code else ""
    slot = re.match(r"\s*//\s*Paste\s+inside\s+(begin|update|end)\s*\(\s*\)", first, re.I)
    if slot:
        return "fragment:" + slot.group(1).lower(), ""
    if re.match(r"\s*//\s*Paste\s+at\s+the\s+top\s+of\s+the\s+file\b", first, re.I):
        return "fragment:file", ""
    if all(re.search(r"\bvoid\s+(?:\w+::)?" + name + r"\s*\(\s*\)", block.code)
           for name in ("begin", "update", "end")):
        return "complete", ""
    return "no-placement", "say where this goes, or mark it skip"


def source_line(block, offset=0):
    return '#line {} {}\n'.format(block.line + offset, json.dumps(block.page))


def materialize(block, kind, folder):
    if kind.startswith("fragment:"):
        config = json.loads((TOOL / "starter/slots.json").read_text(encoding="utf-8"))
        app, instance = config["app"], config["instance"]
        slot = config["slots"][kind.split(":")[1]]
        for name in config["files"]:
            content = (TOOL / "starter" / name).read_text(encoding="utf-8")
            if name == slot["file"]:
                matches = list(re.finditer(slot["anchor"], content, re.M))
                if len(matches) != 1:
                    raise ValueError("starter anchor must match exactly once: " + name)
                match = matches[0]
                pos = match.end() if slot["position"] == "after" else match.start()
                content = (content[:pos] + "\n" + source_line(block) + block.code +
                           '#line {} {}\n'.format(content[:pos].count("\n") + 1, json.dumps(name)) +
                           content[pos:])
            (folder / name).write_text(content, encoding="utf-8")
        return app, instance
    # Match lifecycle-bearing classes, including split headers with declarations.
    classes = re.findall(r"\bclass\s+(\w+)\b", block.code)
    candidates = []
    for app in classes:
        instance = app[0].lower() + app[1:]
        if re.search(r"(?m)^\s*(?!extern\b)(?:inline\s+)?" + re.escape(app) +
                     r"\s+" + re.escape(instance) + r"\s*(?:[;{=]|\([^;]*\)\s*;)", block.code):
            candidates.append((app, instance))
    if len(candidates) != 1:
        raise ValueError("complete app needs one class and a defined global instance named lowerFirst(ClassName)")
    app, instance = candidates[0]
    markers = list(re.finditer(r"(?m)^\s*//\s*" + re.escape(app) + r"\.(h|cpp)\s*$", block.code))
    if markers:
        if [m.group(1) for m in markers] != ["h", "cpp"] or block.code[:markers[0].start()].strip():
            raise ValueError("split app needs // " + app + ".h then // " + app + ".cpp, with no preceding code")
        for index, marker in enumerate(markers):
            end = markers[index + 1].start() if index + 1 < len(markers) else len(block.code)
            offset = block.code[:marker.end()].count("\n")
            (folder / (app + "." + marker.group(1))).write_text(
                source_line(block, offset) + block.code[marker.end():end], encoding="utf-8")
    else:
        (folder / (app + ".h")).write_text(source_line(block) + block.code, encoding="utf-8")
        (folder / (app + ".cpp")).write_text("", encoding="utf-8")
    return app, instance


def bash_path(path):
    value = Path(path).resolve().as_posix()
    if re.match(r"^[A-Za-z]:/", value):
        return "/" + value[0].lower() + value[2:]
    return value


def find_workspace_item(name):
    for parent in REPO.parents:
        candidate = parent / name
        if candidate.is_dir():
            return candidate
    return REPO.parent / name


def setup(firmware):
    script = firmware / "wasm/device_module/build_custom_device_app.sh"
    if not script.is_file():
        raise ValueError("firmware recipe missing; use --firmware /path/to/cyberfidget-firmware")
    bash = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"
    if not Path(bash).is_file():
        raise ValueError("bash missing; install Git Bash or add bash to PATH")
    emsdk = Path(os.environ["EMSDK_ROOT"]) if os.environ.get("EMSDK_ROOT") else find_workspace_item("emsdk")
    prefix = "export EMSDK_QUIET=1 EMSDK_PYTHON=" + shlex.quote(bash_path(sys.executable)) + "; "
    if (emsdk / "emsdk_env.sh").is_file():
        prefix += "source " + shlex.quote(bash_path(emsdk / "emsdk_env.sh")) + " >/dev/null && "
    check = subprocess.run([bash, "-c", prefix + "em++ --version"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check.returncode or "3.1.51" not in check.stdout:
        raise ValueError("em++ 3.1.51 unavailable; activate emsdk 3.1.51 and set EMSDK_ROOT to its directory.\n" + check.stderr)
    return bash, prefix, script


def compile_block(block, build, environment, keep):
    kind, message = classify(block)
    result = dict(page=block.page, line=block.line, kind=kind,
                  result="skipped" if kind == "skipped" else "failed", message=message, output="")
    if message:
        return result
    folder = Path(tempfile.mkdtemp(prefix="example-", dir=build))
    result["build_dir"] = str(folder)
    try:
        app, instance = materialize(block, kind, folder)
        bash, prefix, script = environment
        args = [bash_path(script), app, instance, bash_path(folder), bash_path(folder / "app.wasm")]
        process = subprocess.run([bash, "-c", prefix + "bash " + " ".join(map(shlex.quote, args))],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace")
        result["output"] = process.stdout + process.stderr
        (folder / "compiler.txt").write_text(result["output"], encoding="utf-8")
        result["result"] = "passed" if process.returncode == 0 else "failed"
        if process.returncode:
            result["message"] = "compile failed"
    except (ValueError, OSError) as error:
        result["message"] = str(error)
    finally:
        if not keep:
            shutil.rmtree(folder)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware", type=Path, default=find_workspace_item("cyberfidget-firmware"))
    parser.add_argument("--docs-dir", type=Path, default=REPO / "docs")
    parser.add_argument("--page", default="*", help="glob relative to docs-dir")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    started = time.monotonic()
    try:
        if args.jobs < 1:
            raise ValueError("--jobs must be at least 1")
        if not args.docs_dir.is_dir():
            raise ValueError("docs directory missing; set --docs-dir to a Markdown directory")
        environment = setup(args.firmware.resolve())
        blocks = [block for path in sorted(args.docs_dir.rglob("*.md"))
                  if fnmatch.fnmatchcase(path.relative_to(args.docs_dir).as_posix(), args.page)
                  for block in extract(path, args.docs_dir)]
        build = TOOL / ".build"
        build.mkdir(exist_ok=True)
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(lambda b: compile_block(b, build, environment, args.keep), blocks))
    except (ValueError, OSError) as error:
        print("Setup error: " + str(error), file=sys.stderr)
        return 2
    print("page | line | kind | result")
    for result in results:
        print("{page} | {line} | {kind} | {result}".format(**result))
        if result["message"]:
            print("  " + result["message"])
        if result["result"] == "failed" and result["output"]:
            print(textwrap.indent("\n".join(result["output"].splitlines()[:15]), "  "))
    totals = {"blocks": len(results), "complete": 0, "fragments": 0, "skipped-with-marker": 0,
              "untagged": 0, "no-placement": 0, "passed": 0, "failed": 0}
    for result in results:
        kind = result["kind"]
        key = "fragments" if kind.startswith("fragment:") else "skipped-with-marker" if kind == "skipped" else kind
        totals[key] += 1
        if result["result"] in ("passed", "failed"):
            totals[result["result"]] += 1
    elapsed = round(time.monotonic() - started, 2)
    print("Totals: " + ", ".join("{}={}".format(k, v) for k, v in totals.items()))
    print("Wall-clock: {} seconds".format(elapsed))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(dict(totals=totals, elapsed_seconds=elapsed, examples=results), indent=2) + "\n", encoding="utf-8")
    return 1 if totals["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
