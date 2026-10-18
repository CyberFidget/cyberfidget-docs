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


PASTE = re.compile(r"^\s*//\s*Paste\s+(?:inside\s+(begin|update|end)\s*\(\s*\)|"
                   r"at\s+the\s+top\s+of\s+the\s+file\b)", re.I)


def fragment_sections(code):
    """Split a fragment into (slot, line offset, code) sections.

    A fragment starts with a "// Paste ..." line; any later "// Paste ..."
    line starts the next section, so one block can say "this goes at the
    top of the file, and this goes inside begin()"."""
    lines = code.splitlines(keepends=True)
    if not lines or not PASTE.match(lines[0]):
        return []
    sections = []
    for index, line in enumerate(lines):
        match = PASTE.match(line)
        if match:
            sections.append([(match.group(1) or "file").lower(), index, ""])
        sections[-1][2] += line
    return [tuple(section) for section in sections]


def classify(block):
    if block.skip:
        return "skipped", block.skip
    if not block.language:
        return "untagged", "tag this block cpp, or text if it is not code"
    sections = fragment_sections(block.code)
    if sections:
        return "fragment:" + "+".join(slot for slot, _, _ in sections), ""
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
        files = {name: (TOOL / "starter" / name).read_text(encoding="utf-8").replace("\r\n", "\n")
                 for name in config["files"]}
        # Locate every anchor in the untouched starter first, then insert from
        # the end of each file backwards so earlier positions stay valid.
        inserts = []
        for slot_name, offset, code in fragment_sections(block.code):
            slot = config["slots"][slot_name]
            matches = list(re.finditer(slot["anchor"], files[slot["file"]], re.M))
            if len(matches) != 1:
                raise ValueError("starter anchor must match exactly once: " + slot_name)
            pos = matches[0].end() if slot["position"] == "after" else matches[0].start()
            inserts.append((slot["file"], pos, offset, code))
        for name, pos, offset, code in sorted(inserts, key=lambda item: (item[0], -item[1], -item[2])):
            content = files[name]
            files[name] = (content[:pos] + "\n" + source_line(block, offset) + code +
                           '#line {} {}\n'.format(content[:pos].count("\n") + 1, json.dumps(name)) +
                           content[pos:])
        for name, content in files.items():
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


def check_studio_starter(website):
    """Compare starter/ with the studio's blank template, when a website checkout is present."""
    generator = website / "assets/js/builder.js"
    if not generator.is_file():
        return "not checked (no website checkout)"
    node = shutil.which("node")
    if not node:
        return "not checked (node not found)"
    with tempfile.TemporaryDirectory() as out:
        subprocess.run([node, str(TOOL / "studio/render_starter.js"), str(generator), out],
                       check=True, capture_output=True)
        for name in ("MyApp.h", "MyApp.cpp"):
            expected = (Path(out) / name).read_text(encoding="utf-8")
            actual = (TOOL / "starter" / name).read_text(encoding="utf-8").replace("\r\n", "\n")
            if expected != actual:
                raise ValueError("starter/" + name + " no longer matches the studio's blank template; "
                                 "regenerate it with: node tools/check-examples/studio/render_starter.js "
                                 + generator.as_posix() + " tools/check-examples/starter")
    return "matches the studio's blank template"


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
    parser.add_argument("--website", type=Path, default=find_workspace_item("cyberfidget_website"),
                        help="website checkout used to confirm starter/ matches the studio's blank template")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    started = time.monotonic()
    try:
        if args.jobs < 1:
            raise ValueError("--jobs must be at least 1")
        if not args.docs_dir.is_dir():
            raise ValueError("docs directory missing; set --docs-dir to a Markdown directory")
        studio = check_studio_starter(args.website)
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
    print("Starter: " + studio)
    print("Wall-clock: {} seconds".format(elapsed))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(dict(totals=totals, elapsed_seconds=elapsed, examples=results), indent=2) + "\n", encoding="utf-8")
    return 1 if totals["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
