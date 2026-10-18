# SPDX-License-Identifier: GPL-3.0-or-later
"""Compile Markdown examples using the firmware's device-app recipe."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import difflib
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
    final: bool = False
    cumulative: bool = False
    # Earlier fragment blocks on a cumulative page, in page order.
    prior: list = field(default_factory=list)


def load_config():
    return json.loads((TOOL / "starter/slots.json").read_text(encoding="utf-8"))


CONFIG = load_config()
MARKERS = {spec["marker"]: slot for slot, spec in CONFIG["slots"].items()}


def looks_cpp(code):
    return bool(re.search(
        r"^\s*#\s*include\s*[<\"]|\bvoid\s+\w+\s*\(|"
        r"\bclass\s+\w+\s*\{|\bHAL::\w+|\bcf::gfx::|\b(?:display|d)\.\w+\([^\n]*;",
        code, re.M))


CUMULATIVE = re.compile(r"<!--\s*check-examples:\s*cumulative\s*-->", re.I)
FINAL = re.compile(r"\s*<!--\s*check-examples:\s*final\s*-->\s*", re.I)


def extract(path, root):
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    cumulative = bool(CUMULATIVE.search(text))
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
        final = bool(start and FINAL.fullmatch(lines[start - 1]))
        if language.lower() in LANGUAGES or (not language and looks_cpp(code)):
            blocks.append(Block(path.relative_to(root).as_posix(), start + 2,
                                code, language.lower(), reason, final, cumulative))
        i += 1
    if cumulative:
        # Each fragment step applies on top of every earlier fragment step;
        # the final listing is compared with all of them.
        steps = []
        for block in blocks:
            kind = classify(block)[0]
            if kind.startswith("fragment:"):
                block.prior = list(steps)
                steps.append(block)
            elif kind == "final":
                block.prior = list(steps)
    return blocks


PASTE_LIKE = re.compile(r"^\s*//\s*paste\b", re.I)
SLOT_GUESS = re.compile(r"\b(?:inside\s+)?(begin|update|end)\s*\(|\btop\s+of\s+the\s+file\b", re.I)


def guess_slot(line):
    """The slot a non-canonical placement line seems to mean, or None."""
    match = SLOT_GUESS.search(line)
    if not match:
        return None
    return (match.group(1) or "file").lower()


def scan_fragment(code):
    """Split a fragment into (slot, line offset, code) sections.

    A fragment starts with a placement line, one of the canonical markers in
    starter/slots.json. Any later placement line starts the next section, so
    one block can say "this goes at the top of the file, and this goes inside
    begin()". Placement-looking lines inside block comments or raw strings
    stay part of their section. Returns (sections, bad), where bad lists
    (line offset, text, guessed slot) for "// Paste ..." lines that are not
    exactly a canonical marker."""
    lines = code.splitlines(keepends=True)
    if not lines or not PASTE_LIKE.match(lines[0]):
        return [], []
    sections = []
    bad = []
    block_comment = False
    raw_end = None
    for index, line in enumerate(lines):
        if not block_comment and raw_end is None and PASTE_LIKE.match(line):
            slot = MARKERS.get(line.rstrip())
            if slot is None:
                guessed = guess_slot(line)
                bad.append((index, line.rstrip(), guessed))
                slot = guessed or "file"
            sections.append([slot, index, ""])
        sections[-1][2] += line
        pos = 0
        while pos < len(line):
            if raw_end is not None:
                end = line.find(raw_end, pos)
                if end < 0:
                    break
                pos = end + len(raw_end)
                raw_end = None
            elif block_comment:
                end = line.find("*/", pos)
                if end < 0:
                    break
                pos = end + 2
                block_comment = False
            elif line.startswith("//", pos):
                break
            elif line.startswith("/*", pos):
                block_comment = True
                pos += 2
            else:
                raw = re.match(r'R"([^\s()\\]{0,16})\(', line[pos:])
                if raw:
                    raw_end = ")" + raw.group(1) + '"'
                    pos += raw.end()
                elif line[pos] in ('"', "'"):
                    quote = line[pos]
                    pos += 1
                    while pos < len(line):
                        if line[pos] == "\\":
                            pos += 2
                        elif line[pos] == quote:
                            pos += 1
                            break
                        else:
                            pos += 1
                else:
                    pos += 1
    return [tuple(section) for section in sections], bad


def fragment_sections(code):
    return scan_fragment(code)[0]


def bad_marker_message(block, bad):
    notes = []
    for offset, text, slot in bad:
        if slot:
            want = 'write exactly "' + CONFIG["slots"][slot]["marker"] + '"'
        else:
            want = "write exactly one of: " + ", ".join(
                '"' + spec["marker"] + '"' for spec in CONFIG["slots"].values())
        notes.append("line {}: {!r} is not a placement line; {}".format(block.line + offset, text, want))
    return "; ".join(notes)


def classify(block):
    if block.skip:
        return "skipped", block.skip
    if "cf::gfx::" in block.code:
        return "studio-incompatible", ("The studio refuses cf::gfx:: in projects without art; "
                                       "add using namespace cf::gfx; at the top of the file, "
                                       "below the #include lines, and use short names.")
    if block.final:
        if not block.cumulative:
            return "final", "a final listing needs <!-- check-examples: cumulative --> on its page"
        return "final", ""
    if not block.language:
        return "untagged", "tag this block cpp, or text if it is not code"
    sections, bad = scan_fragment(block.code)
    if bad:
        return "bad-marker", bad_marker_message(block, bad)
    if sections:
        return "fragment:" + "+".join(slot for slot, _, _ in sections), ""
    if all(re.search(r"\bvoid\s+(?:\w+::)?" + name + r"\s*\(\s*\)", block.code)
           for name in ("begin", "update", "end")):
        return "complete", ""
    return "no-placement", "say where this goes, or mark it skip"


def source_line(block, offset=0):
    return '#line {} {}\n'.format(block.line + offset, json.dumps(block.page))


def renamed(text, app):
    """Rename exact starter identifiers (also in file names) in one pass."""
    base, instance = CONFIG["app"], CONFIG["instance"]
    if app == base:
        return text
    replacements = {base: app, instance: app[0].lower() + app[1:],
                    base.upper() + "_H": app.upper() + "_H"}
    pattern = r"\b(?:" + "|".join(map(re.escape, replacements)) + r")\b"
    return re.sub(pattern, lambda match: replacements[match[0]], text)


def assemble(steps, app=None, plain=False):
    """Apply fragment steps, in page order, to the starter.

    Sections for the same slot are pasted one after another in step order,
    so a later step lands below the code earlier steps put there. With
    plain=True the result is what a reader's file looks like: no #line
    directives and no placement lines. Returns ({file name: text}, app,
    instance)."""
    app = app or CONFIG["app"]
    files = {renamed(name, app): renamed((TOOL / "starter" / name).read_text(encoding="utf-8")
                                         .replace("\r\n", "\n"), app)
             for name in CONFIG["files"]}
    pieces = {}
    for step in steps:
        for slot, offset, code in fragment_sections(step.code):
            if plain:
                # The scanner's offset identifies the section opener. Later
                # marker-looking lines may belong to a raw string or comment.
                code = "".join(step.code.splitlines(keepends=True)[
                    offset + 1:offset + len(code.splitlines(keepends=True))])
            else:
                code = source_line(step, offset) + code
            pieces.setdefault(slot, []).append(code)
    # Locate every anchor in the untouched starter first, then insert from
    # the end of each file backwards so earlier positions stay valid.
    inserts = []
    for slot_name, codes in pieces.items():
        slot = CONFIG["slots"][slot_name]
        name = renamed(slot["file"], app)
        matches = list(re.finditer(renamed(slot["anchor"], app), files[name], re.M))
        if len(matches) != 1:
            raise ValueError("starter anchor must match exactly once: " + slot_name)
        pos = matches[0].end() if slot["position"] == "after" else matches[0].start()
        inserts.append((name, pos, "".join(codes)))
    for name, pos, code in sorted(inserts, key=lambda item: (item[0], -item[1])):
        content = files[name]
        resume = "" if plain else '#line {} {}\n'.format(content[:pos].count("\n") + 1, json.dumps(name))
        files[name] = content[:pos] + "\n" + code + resume + content[pos:]
    return files, app, app[0].lower() + app[1:]


def split_parts(block, app):
    """{"h"/"cpp": (line offset, code)} for a listing split by // App.h and // App.cpp."""
    markers = list(re.finditer(r"(?m)^\s*//\s*" + re.escape(app) + r"\.(h|cpp)\s*$", block.code))
    if not markers:
        return {}
    if [m.group(1) for m in markers] != ["h", "cpp"] or block.code[:markers[0].start()].strip():
        raise ValueError("split app needs // " + app + ".h then // " + app + ".cpp, with no preceding code")
    parts = {}
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(block.code)
        parts[marker.group(1)] = (block.code[:marker.end()].count("\n"), block.code[marker.end():end])
    return parts


CPP_TOKEN = re.compile(
    r'(?P<space>\s+)|(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|'
    r'(?:u8|u|U|L)?R"(?P<delimiter>[^\s()\\]{0,16})\([\s\S]*?\)(?P=delimiter)"(?:[A-Za-z_]\w*)?|'
    r'''(?:u8|u|U|L)?(?:"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*')(?:[A-Za-z_]\w*)?|'''
    r'(?:\d|\.\d)(?:[eEpP][+-]|[\w.\'])*|[A-Za-z_]\w*|'
    r'%:%:|>>=|<<=|<=>|->\*|\.\.\.|::|\.\*|->|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\||'
    r'\+=|-=|\*=|/=|%=|\^=|&=|\|=|##|<:|:>|<%|%>|%:|[^\s]'
)


def cpp_tokens(text):
    """C++ lexical tokens; discard comments and inter-token whitespace.

    Ordinary, character and raw literals retain their exact spelling, including
    internal whitespace. Operators use longest match, so += is one token.
    """
    return [match[0] for match in CPP_TOKEN.finditer(text)
            if match.lastgroup not in ("space", "comment")]


def materialize_final(block, folder):
    """Check a final listing against the starter plus every earlier step, then lay it out."""
    match = re.search(r"\b([A-Za-z_]\w*)::begin\s*\(\s*\)", block.code)
    if not match:
        raise ValueError("final listing needs a ClassName::begin() definition")
    expected, app, instance = assemble(block.prior, app=match.group(1), plain=True)
    parts = split_parts(block, app) or {"cpp": (0, block.code)}
    diffs = []
    for ext, (_, code) in parts.items():
        name = app + "." + ext
        want, got = cpp_tokens(expected[name]), cpp_tokens(code)
        if want != got:
            diffs.extend(difflib.unified_diff(want, got, "starter + steps: " + name,
                                              "final listing: " + name, n=1, lineterm=""))
    if diffs:
        shown = diffs[:40] + (["... ({} more diff lines)".format(len(diffs) - 40)] if len(diffs) > 40 else [])
        raise ValueError("final listing differs from the starter plus the steps above it "
                         "(comments and whitespace between tokens ignored):\n" + "\n".join(shown))
    for ext in ("h", "cpp"):
        name = app + "." + ext
        if ext in parts:
            offset, code = parts[ext]
            (folder / name).write_text(source_line(block, offset) + code, encoding="utf-8")
        else:
            (folder / name).write_text(expected[name], encoding="utf-8")
    return app, instance


def materialize(block, kind, folder):
    if kind.startswith("fragment:"):
        files, app, instance = assemble(block.prior + [block])
        for name, content in files.items():
            (folder / name).write_text(content, encoding="utf-8")
        return app, instance
    if kind == "final":
        return materialize_final(block, folder)
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
    parts = split_parts(block, app)
    if parts:
        for ext, (offset, code) in parts.items():
            (folder / (app + "." + ext)).write_text(source_line(block, offset) + code, encoding="utf-8")
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
    if not website.is_dir():
        return "not checked (no website checkout)"
    generator = website / "assets/js/builder.js"
    regenerate = ("regenerate it with: node tools/check-examples/studio/render_starter.js "
                  + generator.as_posix() + " tools/check-examples/starter")
    if not generator.is_file():
        raise ValueError("website starter generator missing: " + generator.as_posix()
                         + "; restore the generator, then " + regenerate)
    node = shutil.which("node")
    if not node:
        raise ValueError("Node.js missing; install Node.js or add node to PATH to check the studio starter")
    with tempfile.TemporaryDirectory() as out:
        try:
            subprocess.run([node, str(TOOL / "studio/render_starter.js"), str(generator), out],
                           check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        except subprocess.CalledProcessError as error:
            raise ValueError("studio starter renderer failed:\n" + (error.stderr or "") + "\n" + regenerate) from error
        except OSError as error:
            raise ValueError("studio starter renderer could not run: " + str(error) + "\n" + regenerate) from error
        for name in ("MyApp.h", "MyApp.cpp"):
            try:
                expected = (Path(out) / name).read_text(encoding="utf-8")
            except OSError as error:
                raise ValueError("studio starter renderer output missing or unreadable: " + name
                                 + "\n" + regenerate) from error
            actual = (TOOL / "starter" / name).read_text(encoding="utf-8").replace("\r\n", "\n")
            if expected != actual:
                raise ValueError("starter/" + name + " differs from the studio's blank template; " + regenerate)
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
            if block.prior:
                result["message"] += " (with the {} earlier steps on this page applied first)".format(len(block.prior))
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
            print(textwrap.indent(result["message"], "  "))
        if result["result"] == "failed" and result["output"]:
            print(textwrap.indent("\n".join(result["output"].splitlines()[:15]), "  "))
    totals = {"blocks": len(results), "complete": 0, "fragments": 0, "skipped-with-marker": 0,
              "untagged": 0, "no-placement": 0, "bad-marker": 0, "studio-incompatible": 0,
              "final": 0, "passed": 0, "failed": 0}
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
