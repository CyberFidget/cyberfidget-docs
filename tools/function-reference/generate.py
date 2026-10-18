# SPDX-License-Identifier: CC-BY-SA-4.0
"""Extract the app-facing intersection of the device and emulator headers."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
HEADERS = ('HAL.h', 'DisplayProxy.h', 'ButtonManager.h', 'AudioManager.h',
           'RGBController.h', 'globals.h', 'MenuManager.h', 'Arduino.h')
LIBS = ('HAL', 'DisplayProxy', 'ButtonManager', 'AudioManager', 'RGBController',
        'Globals', 'MenuManager')
CLASSES = {'DisplayProxy', 'ButtonManager', 'AudioManager', 'MenuManager',
           'Actor', 'AnimationPlayer', 'MeshActor', 'RigActor'}
SECTIONS = ['Screen', 'Text', 'Buttons', 'LEDs', 'Sound', 'Slider', 'Motion',
            'Time', 'Sprites and animation', 'Leaving the app / app control']
TABLES = ['Button names', 'LED names', 'Colors', 'Fonts', 'Text alignment',
          'Button event types', 'Animation constants', 'Readable globals']


def find_firmware():
    for parent in (ROOT, *ROOT.parents):
        candidate = parent / 'cyberfidget-firmware'
        if (candidate / 'wasm/device_module/shims/HAL.h').is_file():
            return candidate
    raise ValueError('Firmware not found. Pass --firmware PATH to the firmware checkout.')


def active_source(source):
    """Mask comments/directives and the two test-only branches, preserving offsets."""
    source = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/',
                    lambda m: re.sub(r'[^\n]', ' ', m[0]), source)
    stack = []
    enabled = True
    result = []
    for line in source.splitlines(keepends=True):
        directive = re.match(r'\s*#\s*(if\w*|else|elif|endif)\b(.*)', line)
        if directive:
            op, arg = directive.groups()
            if op in ('if', 'ifdef', 'ifndef'):
                condition = arg.strip() not in ('HOST_TEST', 'CF_TEST_CLI')
                if op == 'ifndef' and arg.strip() in ('HOST_TEST', 'CF_TEST_CLI'):
                    condition = True
                stack.append((enabled, condition))
                enabled = enabled and condition
            elif op in ('else', 'elif'):
                parent, condition = stack[-1]
                enabled = parent and not condition
            elif op == 'endif':
                enabled, _ = stack.pop()
        if line.lstrip().startswith('#') or not enabled:
            line = re.sub(r'[^\n]', ' ', line)
        result.append(line)
    return ''.join(result)


def parse_header(path, firmware):
    """Purpose-built declaration walker, skipping inline bodies by brace depth.

    Only the named app-facing classes are inspected; String, serial, display
    driver and asset data structs are types rather than this tool's API scope.
    """
    source = active_source(path.read_text(encoding='utf-8'))
    result = []
    def add(name, signature, kind, offset, value=None):
        row = dict(name=name, signature=' '.join(signature.split()), kind=kind,
                   header=path.relative_to(firmware).as_posix(),
                   line=source.count('\n', 0, offset) + 1)
        if value is not None:
            row['value'] = value
        result.append(row)

    def close_brace(start, end):
        depth = 1
        token = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]')
        for m in token.finditer(source, start, end):
            if m[0] == '{': depth += 1
            if m[0] == '}': depth -= 1
            if depth == 0: return m.start()
        raise ValueError(f'Unbalanced header {path}; extend the parser for this syntax.')

    def walk(start, end, scope='', cls=None, public=True, friends_only=False):
        pos = start
        while pos < end:
            while pos < end and source[pos].isspace(): pos += 1
            access = re.match(r'(public|private|protected)\s*:', source[pos:end])
            if access:
                public = access[1] == 'public'
                pos += access.end()
                continue
            begin = pos
            parens = brackets = 0
            while pos < end:
                c = source[pos]
                if c in ('"', "'"):
                    quote = c
                    pos += 1
                    while pos < end and source[pos] != quote:
                        pos += 2 if source[pos] == '\\' else 1
                elif c == '(': parens += 1
                elif c == ')': parens -= 1
                elif c == '[': brackets += 1
                elif c == ']': brackets -= 1
                elif c in ';{}' and not parens and not brackets: break
                pos += 1
            text = source[begin:pos].strip()
            delimiter = source[pos:pos + 1]
            if not delimiter: break
            body_end = close_brace(pos + 1, end) if delimiter == '{' else pos
            ns = re.fullmatch(r'namespace\s+(\w+)', text)
            aggregate = re.match(r'(class|struct)\s+(\w+)\b', text)
            enum = re.match(r'enum\s+(class\s+)?(\w+)(?:\s*:\s*\w+)?$', text)
            if ns:
                walk(pos + 1, body_end, scope + ns[1] + '::')
            elif enum and public:
                prefix = scope + (enum[2] + '::' if enum[1] else '')
                value = -1
                for m in re.finditer(r'(\w+)\s*(?:=\s*([^,]+))?(?:,|$)', source[pos+1:body_end]):
                    if m[2]:
                        value = int(m[2].strip(), 0)
                    else: value += 1
                    add(prefix + m[1], m[0].strip().rstrip(','), 'enum', pos+1+m.start(), str(value))
            elif aggregate:
                if aggregate[2] in CLASSES:
                    walk(pos + 1, body_end, scope + aggregate[2] + '::',
                         aggregate[2], aggregate[1] == 'struct')
                else:
                    # A friend operator is a free function, even inside a type
                    # whose member API is outside the reference's scope.
                    walk(pos + 1, body_end, scope, friends_only=True)
            elif text and (public or text.startswith('friend ')) and (not friends_only or text.startswith('friend ')):
                # A function has a terminal parameter list (plus const/attributes).
                function = re.search(r'(operator\s*[+*/<>=!-]+|~?\w+)\s*\(', text)
                if function and not text.startswith(('static_assert', 'typedef', 'using')):
                    add(scope + function[1], text, 'method' if cls else 'function', begin)
                elif re.fullmatch(r'using std::(?:min|max)', text):
                    add(text.split('::')[-1], text, 'function', begin)
                elif '(' not in text:
                    variable = re.match(r'(?:(?:inline|static)\s+)?(?:constexpr|const|extern)\s+[\s\S]*?\b(\w+)\s*(?:\[[^]]*\])?\s*(?:=\s*([\s\S]*))?$', text)
                    if variable:
                        name, value = variable.groups()
                        kind = 'font' if name.startswith('ArialMT_') else ('global' if text.startswith('extern ') else 'constant')
                        add(scope + name, text, kind, begin, value)
            pos = body_end + 1
    walk(0, len(source))
    return result


def inventory(firmware):
    targets = {}
    headers = set()
    graphics = firmware / 'lib/CFGraphics/include'
    # Follow the umbrella's local includes, including mesh/rig/icons.
    gfx = set()
    def follow(path):
        if path in gfx: return
        gfx.add(path)
        for name in re.findall(r'#include "(cf_gfx[^\"]+\.h)"', path.read_text(encoding='utf-8')):
            follow(graphics / name)
    follow(graphics / 'cf_gfx.h')
    for target, directory in [('device', 'wasm/device_module/shims'), ('emulator', 'wasm/shims')]:
        paths = []
        for name in HEADERS:
            path = firmware / directory / name
            if not path.exists():
                candidates = [firmware / 'lib' / lib / name for lib in LIBS]
                path = next((p for p in candidates if p.exists()), None)
                if path is None: raise ValueError(f'Cannot resolve {target} {name}; update header resolution.')
            paths.append(path)
        if target == 'emulator': paths.append(firmware / 'wasm/shims/SSD1306Wire.h')
        rows = {}
        for path in sorted(set(paths) | gfx):
            headers.add(path.relative_to(firmware).as_posix())
            for row in parse_header(path, firmware):
                rows.setdefault(row['name'], []).append(row)
        targets[target] = rows
    return targets, sorted(headers)


def slug(text):
    text = re.sub(r'[`*_]', '', text)
    text = unicodedata.normalize('NFC', text).lower().strip()
    return re.sub(r'\s+', '-', re.sub(r'[^\w\s-]', '', text))


def validate_link(link):
    page, _, anchor = link.partition('#')
    path = (ROOT / 'docs/reference' / page).resolve()
    if not path.is_relative_to(ROOT / 'docs') or not path.is_file():
        raise ValueError(f'Link {link} has no page. Fix see in reference.toml to an existing docs page.')
    if anchor:
        headings = []
        fenced = False
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith(('```', '~~~')): fenced = not fenced
            if not fenced and re.match(r'^#{1,6} ', line):
                base = slug(re.sub(r'^#+\s+', '', line))
                unique = base
                suffix = 1
                while unique in headings:
                    unique = f'{base}_{suffix}'
                    suffix += 1
                headings.append(unique)
        if anchor not in headings:
            raise ValueError(f'Link {link} has no heading anchor. Fix see in reference.toml; valid anchors: {", ".join(headings)}')


def build(firmware, sidecar):
    targets, headers = inventory(firmware)
    data = tomllib.loads(sidecar.read_text(encoding='utf-8'))
    described, ignored = data.get('symbols', {}), data.get('ignore', {})
    common = set(targets['device']) & set(targets['emulator'])
    union = set(targets['device']) | set(targets['emulator'])
    errors = []
    for name in sorted(set(described) - common):
        errors.append(f'{name} is not in BOTH targets. Remove its description or correct its qualified name in {sidecar}.')
    for name in sorted(union - set(described) - set(ignored)):
        errors.append(f'{name} is undescribed. Add [symbols."{name}"] with section/use/does/see to {sidecar}, or add an explicit ignore reason.')
    for name, reason in ignored.items():
        if name not in union: errors.append(f'{name} is not a header symbol. Remove its stale ignore entry from {sidecar}.')
        if not isinstance(reason, str) or not reason.strip(): errors.append(f'{name}: add a nonempty ignore reason in {sidecar}.')
        if name in described: errors.append(f'{name}: choose a description or an ignore entry in {sidecar}, not both.')
    for name, entry in described.items():
        for key in ('section', 'use', 'does', 'see'):
            if not isinstance(entry.get(key), str) or not entry[key].strip(): errors.append(f'{name}: add nonempty {key} in {sidecar}.')
        if entry.get('section') not in SECTIONS + TABLES: errors.append(f'{name}: choose a documented section in {sidecar}.')
        if entry.get('see'):
            try: validate_link(entry['see'])
            except ValueError as exc: errors.append(str(exc))
    if errors: raise ValueError('\n'.join(errors))
    commit = subprocess.check_output(['git', '-c', f'safe.directory={firmware.as_posix()}',
                                      '-C', str(firmware), 'rev-parse', 'HEAD'], text=True).strip()
    symbols = []
    for name in described:
        entry = described[name]
        declarations = [dict(row, target=target) for target in ('device', 'emulator') for row in targets[target][name]]
        symbols.append(dict(name=name, signature='; '.join(row['signature'] for row in targets['device'][name]),
                            kind=targets['device'][name][0]['kind'], **entry,
                            targets=['device', 'emulator'], declarations=declarations))
    # Keep the authored reader order on the page, and a stable name order in JSON.
    def cell(value): return value.replace('|', '&#124;').replace('\n', ' ')
    def anchor(name): return 'symbol-' + re.sub(r'[^a-z0-9-]', '-', name.lower())
    lines = ['<!-- generated by tools/function-reference/generate.py from the firmware headers - edit reference.toml, not this page. -->',
             '# App function reference', '',
             'Every function your app can call, on one page. Each row links to the page that explains it.', '',
             'How to read this: copy a call into your app; start with the [first-app guide](../getting-started/first-app.md).', '',
             '<style>.function-reference table { table-layout: fixed; width: 100%; } .function-reference th, .function-reference td { min-width: 0 !important; padding: .6em .5em !important; overflow-wrap: anywhere; } .function-reference th:first-child { width: 44%; } .reference-calls th:nth-child(2), .reference-constants th:last-child { width: 42%; } .reference-calls th:last-child, .reference-constants th:nth-child(2) { width: 14%; } .function-reference code { white-space: normal; overflow-wrap: anywhere; }</style>', '',
             '<div class="function-reference" markdown="1">', '',
             'These calls are available on both the device and the app emulator. The screen is 128 x 64 pixels with (0, 0) at the top-left; x goes right and y goes down. LEDs are RGBW (red, green, blue, white), with each channel from 0-255.', '',
             'The calls are written the way they look inside `begin()`, `update()` and `end()` of the studio starter, where `display` (the screen) and `buttonManager` (the buttons) are ready to use. In your own functions at the top of the file, write `HAL::displayProxy()` and `HAL::buttonManager()` instead.', '',
             'Examples use your own `void onRight(const ButtonEvent& event)` callback (a function called when a button changes), `sprite` image, `sheet`, `animation`, and `player` objects. A button event has `buttonIndex`, `eventType`, and `duration` in ms. Register callbacks in `begin()` and unregister them in `end()`.', '',
             '!!! tip "Quick answers"']
    for label, name in [('Middle LED blue', 'HAL::setRgbLed'), ('Beep', 'AudioManager::playTone'), ('React to the right button', 'ButtonManager::registerCallback'), ('Draw text', 'DisplayProxy::drawString'), ('Draw a sprite', 'cf::gfx::drawSprite'), ('Read the slider', 'sliderPosition_Percentage_Filtered')]:
        lines.append(f'    - [{label}](#{anchor(name)}): `{described[name]["use"]}`')
    lines.append('')
    for section in SECTIONS + TABLES:
        rows = [row for row in symbols if row['section'] == section]
        if section == 'Readable globals':
            rows = [row for row in symbols if row['kind'] == 'global'
                    and row['name'] != 'millis_APP_LASTINTERACTION']
        lines += [f'## {section}', '']
        if section == 'LEDs': lines += ['Pixel map: 0 Back, 1 Front Top, 2 Front Middle, 3 Front Bottom.', '']
        if section == 'Sprites and animation': lines += ['Use `#include "cf_gfx.h"` and your generated asset header. Examples use `cf::gfx::Actor player`, `cf::gfx::AnimationPlayer clock`, `cf::gfx::MeshActor model`, and `cf::gfx::RigActor figure`. A pivot is the point on a sprite placed at its screen position.', '']
        if not rows:
            detail = 'Read slider position as 0-100 %, 0-255, or 0-4095.' if section == 'Slider' else 'Read acceleration along X, Y, and Z; roughly 1000 units equal gravity (1 g).'
            lines += [detail + ' See [Readable globals](#readable-globals) below.', '']
            continue
        constant = section in TABLES and section != 'Readable globals'
        lines += [f'<div class="reference-{"constants" if constant else "calls"}" markdown="1">', '']
        lines += ['| Name | Value | What it does |' if constant else '| Call | What it does | Learn more |',
                  '|---|---|---|']
        for row in rows:
            suffix = '-summary' if section == 'Readable globals' else ''
            ident = f'<span id="{anchor(row["name"])}{suffix}"></span>'
            if constant:
                value = targets['device'][row['name']][0].get('value') or 'font handle'
                seen = set()
                while value in targets['device'] and value not in seen:
                    seen.add(value)
                    value = targets['device'][value][0].get('value') or value
                lines.append(f'| {ident}`{row["name"]}` | `{cell(value)}` | {cell(row["does"])} [More]({row["see"]}) |')
            else:
                lines.append(f'| {ident}`{cell(row["use"])}` | {cell(row["does"])} | [Guide]({row["see"]}) |')
        lines += ['', '</div>', '']
    lines += ['</div>', '']
    stats = {target: len(rows) for target, rows in targets.items()}
    stats.update(both=len(common), described=len(described), ignored=len(ignored))
    return '\n'.join(lines), json.dumps(dict(generated_from=dict(firmware_commit=commit, headers=headers), symbols=sorted(symbols, key=lambda row: row['name'])), indent=2, ensure_ascii=False) + '\n', stats, {target: sorted(set(rows) - common) for target, rows in targets.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware', type=Path)
    parser.add_argument('--sidecar', type=Path, default=Path(__file__).with_name('reference.toml'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        page, symbols, stats, only = build((args.firmware or find_firmware()).resolve(), args.sidecar)
        outputs = {ROOT / 'docs/reference/functions.md': page,
                   ROOT / 'docs/assets/reference/app-functions.json': symbols}
        drift = False
        for path, content in outputs.items():
            if args.check:
                if not path.exists() or path.read_text(encoding='utf-8') != content:
                    print(f'{path.relative_to(ROOT)} differs. Run python tools/function-reference/generate.py with the same --firmware and --sidecar, then review both outputs.', file=sys.stderr)
                    drift = True
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8', newline='\n')
        print(json.dumps(dict(counts=stats, target_only=only), indent=2))
        return int(drift)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
