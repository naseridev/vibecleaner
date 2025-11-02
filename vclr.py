#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from fnmatch import fnmatch
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from functools import lru_cache


VERSION = "1.0.0"
MAX_FILE_SIZE = 10 * 1024 * 1024


COMMENT_STYLES = {
    'c_style': {
        'line': ['//'],
        'block': [('/*', '*/')],
        'str': ['"', "'"],
        'exts': {'.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx',
                 '.h', '.hpp', '.hxx', '.cs', '.go', '.rs', '.swift', '.kt', '.kts',
                 '.scala', '.m', '.mm', '.dart', '.v', '.d', '.groovy', '.gradle'}
    },
    'c_style_backtick': {
        'line': ['//'],
        'block': [('/*', '*/')],
        'str': ['`', '"', "'"],
        'exts': {'.js', '.ts', '.jsx', '.tsx', '.go'}
    },
    'c_style_multiline_str': {
        'line': ['//'],
        'block': [('/*', '*/')],
        'str': ['"""', '"'],
        'exts': {'.swift'}
    },
    'c_style_triple_str': {
        'line': ['//'],
        'block': [('/*', '*/')],
        'str': ['"""', '"', "'"],
        'exts': {'.kt', '.kts', '.scala', '.groovy', '.gradle'}
    },
    'c_style_triple_both': {
        'line': ['//'],
        'block': [('/*', '*/')],
        'str': ['"""', "'''", '"', "'"],
        'exts': {'.dart'}
    },
    'hash_style': {
        'line': ['#'],
        'block': [],
        'str': ['"', "'"],
        'exts': {'.sh', '.bash', '.zsh', '.r', '.tcl', '.cr', '.yaml', '.yml',
                 '.toml', '.conf'}
    },
    'hash_style_triple': {
        'line': ['#'],
        'block': [],
        'str': ['"""', "'''", '"', "'"],
        'exts': {'.py'}
    },
    'hash_style_triple_double': {
        'line': ['#'],
        'block': [],
        'str': ['"""', '"', "'"],
        'exts': {'.ex', '.exs', '.nim'}
    },
    'hash_block_style': {
        'line': ['#'],
        'block': [('#=', '=#')],
        'str': ['"""', '"'],
        'exts': {'.jl'}
    },
    'hash_bracket_block': {
        'line': ['#'],
        'block': [('#[', ']#')],
        'str': ['"""', '"'],
        'exts': {'.nim'}
    },
    'php_style': {
        'line': ['//', '#'],
        'block': [('/*', '*/')],
        'str': ['"', "'"],
        'exts': {'.php'}
    },
    'ruby_style': {
        'line': ['#'],
        'block': [('=begin', '=end')],
        'str': ['"', "'"],
        'exts': {'.rb'}
    },
    'lua_style': {
        'line': ['--'],
        'block': [('--[[', ']]')],
        'str': ['"', "'"],
        'exts': {'.lua'}
    },
    'perl_style': {
        'line': ['#'],
        'block': [('=pod', '=cut')],
        'str': ['"', "'"],
        'exts': {'.pl', '.pm'}
    },
    'sql_style': {
        'line': ['--'],
        'block': [('/*', '*/')],
        'str': ['"', "'"],
        'exts': {'.sql'}
    },
    'vim_style': {
        'line': ['"'],
        'block': [],
        'str': ['"', "'"],
        'exts': {'.vim'}
    },
    'erlang_style': {
        'line': ['%'],
        'block': [],
        'str': ['"'],
        'exts': {'.erl', '.hrl'}
    },
    'lisp_style': {
        'line': [';'],
        'block': [],
        'str': ['"'],
        'exts': {'.clj', '.cljs', '.lisp'}
    },
    'haskell_style': {
        'line': ['--'],
        'block': [('{-', '-}')],
        'str': ['"'],
        'exts': {'.hs', '.elm'}
    },
    'ml_style': {
        'line': [],
        'block': [('(*', '*)')],
        'str': ['"'],
        'exts': {'.ml', '.mli'}
    },
    'fsharp_style': {
        'line': ['//'],
        'block': [('(*', '*)')],
        'str': ['"""', '"'],
        'exts': {'.fs', '.fsx'}
    },
    'd_style': {
        'line': ['//'],
        'block': [('/*', '*/'), ('/+', '+/')],
        'str': ['"', "'"],
        'exts': {'.d'}
    },
    'ada_style': {
        'line': ['--'],
        'block': [],
        'str': ['"'],
        'exts': {'.ada', '.adb', '.ads', '.vhd', '.vhdl'}
    },
    'vb_style': {
        'line': ["'"],
        'block': [],
        'str': ['"'],
        'exts': {'.vb'}
    },
    'pascal_style': {
        'line': ['//'],
        'block': [('{', '}'), ('(*', '*)')],
        'str': ["'"],
        'exts': {'.pas', '.pp'}
    },
    'asm_style': {
        'line': [';'],
        'block': [],
        'str': ['"', "'"],
        'exts': {'.asm'}
    },
    'asm_hash_style': {
        'line': [';', '#'],
        'block': [],
        'str': ['"', "'"],
        'exts': {'.s'}
    },
    'batch_style': {
        'line': ['REM', 'rem', '::'],
        'block': [],
        'str': ['"'],
        'exts': {'.bat', '.cmd'}
    },
    'powershell_style': {
        'line': ['#'],
        'block': [('<#', '#>')],
        'str': ['"', "'"],
        'exts': {'.ps1'}
    },
    'coffee_style': {
        'line': ['#'],
        'block': [('###', '###')],
        'str': ['"""', "'''", '"', "'"],
        'exts': {'.coffee'}
    },
    'zig_style': {
        'line': ['//'],
        'block': [],
        'str': ['"'],
        'exts': {'.zig'}
    },
    'html_style': {
        'line': [],
        'block': [('<!--', '-->')],
        'str': ['"', "'"],
        'exts': {'.xml', '.html', '.htm', '.xhtml', '.svg', '.xaml'}
    },
    'css_style': {
        'line': [],
        'block': [('/*', '*/')],
        'str': ['"', "'"],
        'exts': {'.css'}
    },
    'scss_style': {
        'line': ['//'],
        'block': [('/*', '*/')],
        'str': ['"', "'"],
        'exts': {'.scss', '.sass', '.less'}
    },
    'json_style': {
        'line': [],
        'block': [],
        'str': ['"'],
        'exts': {'.json'}
    },
    'ini_style': {
        'line': [';', '#'],
        'block': [],
        'str': ['"', "'"],
        'exts': {'.ini', '.cfg'}
    }
}

XML_EXTS = {
    '.config', '.csproj', '.vbproj', '.fsproj', '.vcxproj', '.props', '.targets',
    '.nuspec', '.resx', '.settings', '.manifest', '.plist', '.xib', '.storyboard',
    '.xlf', '.xliff', '.xsd', '.wsdl', '.rss', '.atom', '.opml', '.gpx', '.kml'
}

SHEBANG_MAP = {
    'python': '.py', 'node': '.js', 'ruby': '.rb', 'perl': '.pl',
    'bash': '.bash', 'sh': '.sh', 'php': '.php'
}


def build_lang_map():
    lang_map = {}
    for style_name, style_data in COMMENT_STYLES.items():
        for ext in style_data['exts']:
            if ext not in lang_map:
                lang_map[ext] = {
                    'line': style_data['line'],
                    'block': style_data['block'],
                    'str': style_data['str']
                }
    return lang_map


LANG_MAP = build_lang_map()


def check_color_support():
    if not sys.stdout.isatty():
        return False

    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            h = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
                if kernel32.SetConsoleMode(h, mode):
                    return True
        except:
            pass
        return False

    term = os.environ.get('TERM', '')
    if term in ('dumb', ''):
        return False

    return True


class Colors:
    def __init__(self):
        self.enabled = check_color_support()

    def apply(self, text, code):
        if not self.enabled:
            return text
        return f'\033[{code}m{text}\033[0m'

    def red(self, text):
        return self.apply(text, '91')

    def yellow(self, text):
        return self.apply(text, '33')

    def bold(self, text):
        return self.apply(text, '1')


class TUI:
    def __init__(self):
        self.colors = Colors()

    def term_size(self):
        try:
            if sys.platform == 'win32':
                from ctypes import windll, create_string_buffer, Structure, byref
                from ctypes.wintypes import SHORT

                class COORD(Structure):
                    _fields_ = [("X", SHORT), ("Y", SHORT)]

                class SMALL_RECT(Structure):
                    _fields_ = [("Left", SHORT), ("Top", SHORT), ("Right", SHORT), ("Bottom", SHORT)]

                class CONSOLE_SCREEN_BUFFER_INFO(Structure):
                    _fields_ = [
                        ("dwSize", COORD),
                        ("dwCursorPosition", COORD),
                        ("wAttributes", SHORT),
                        ("srWindow", SMALL_RECT),
                        ("dwMaximumWindowSize", COORD)
                    ]

                h = windll.kernel32.GetStdHandle(-12)
                csbi = CONSOLE_SCREEN_BUFFER_INFO()
                windll.kernel32.GetConsoleScreenBufferInfo(h, byref(csbi))
                return csbi.srWindow.Right - csbi.srWindow.Left + 1, csbi.srWindow.Bottom - csbi.srWindow.Top + 1
            else:
                import fcntl, termios, struct
                data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
                h, w = struct.unpack('hh', data)
                return w, h
        except:
            return 80, 24

    def clear(self):
        if sys.platform == 'win32':
            os.system('cls')
        else:
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()

    def getch(self):
        if sys.platform == 'win32':
            import msvcrt
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                return {'H': 'up', 'P': 'down', 'M': 'right', 'K': 'left'}.get(ch2.decode('ascii', errors='ignore'), None)
            if ch == b'\r':
                return 'enter'
            return ch.decode('ascii', errors='ignore').lower()
        else:
            import termios, tty
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(2)
                    return {'[A': 'up', '[B': 'down', '[C': 'right', '[D': 'left'}.get(ch2, None)
                return 'enter' if ch in ('\r', '\n') else ch.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)


def fmt_time(s):
    if s < 60:
        return f"{s:.2f}s"
    m = int(s // 60)
    return f"{m}m {s % 60:.1f}s" if s < 3600 else f"{int(s // 3600)}h {m % 60}m"


@lru_cache(maxsize=128)
def load_ignore(path):
    if not Path(path).exists():
        return tuple()
    with open(path) as f:
        return tuple(l.strip() for l in f if l.strip() and not l.startswith('#'))


def should_ignore(fpath, base, patterns):
    if not patterns:
        return False
    try:
        rel = str(fpath.relative_to(base))
    except:
        rel = fpath.name
    return any(fnmatch(fpath.name, p) or fnmatch(rel, p) for p in patterns)


def is_text(fpath):
    try:
        sz = fpath.stat().st_size
        if sz == 0 or sz > MAX_FILE_SIZE:
            return False
        with open(fpath, 'rb') as f:
            chunk = f.read(min(8192, sz))
            return b'\x00' not in chunk
    except:
        return False


def detect_lang(fpath):
    ext = fpath.suffix.lower()
    if ext in LANG_MAP:
        return ext
    if ext in XML_EXTS:
        return '.xml'

    try:
        with open(fpath, 'rb') as f:
            head = f.read(256)
            if head.startswith(b'#!'):
                shebang = head.split(b'\n')[0].decode('utf-8', errors='ignore').lower()
                for key, lang in SHEBANG_MAP.items():
                    if key in shebang:
                        return lang
            if b'<?xml' in head[:100] or b'<!DOCTYPE' in head[:100]:
                return '.xml'
    except:
        pass

    return ext if ext in LANG_MAP else None


def find_strings(text, cfg):
    ranges = []
    i = 0
    n = len(text)

    while i < n:
        for delim in cfg.get('str', []):
            dlen = len(delim)
            if text[i:i+dlen] == delim:
                start = i
                i += dlen
                if delim in ('"""', "'''"):
                    while i + dlen <= n:
                        if text[i:i+dlen] == delim:
                            i += dlen
                            break
                        i += 2 if text[i] == '\\' and i + 1 < n else 1
                else:
                    while i < n:
                        if text[i] == delim:
                            i += 1
                            break
                        i += 2 if text[i] == '\\' and i + 1 < n else 1
                ranges.append((start, i))
                break
        else:
            i += 1

    return ranges


def in_string(pos, ranges):
    return any(s <= pos < e for s, e in ranges)


def find_comments(text, cfg):
    comments = []
    strings = find_strings(text, cfg)
    lines = text.split('\n')
    pos = 0

    for ln, line in enumerate(lines):
        for lc in cfg.get('line', []):
            idx = 0
            while idx < len(line):
                found = line.find(lc, idx)
                if found == -1:
                    break
                if not in_string(pos + found, strings):
                    comments.append({
                        'start': pos + found,
                        'end': pos + len(line),
                        'line': ln,
                        'type': 'line',
                        'col': found,
                        'col_end': len(line)
                    })
                    break
                idx = found + len(lc)
        pos += len(line) + 1

    for bs, be in cfg.get('block', []):
        i = 0
        while i < len(text):
            si = text.find(bs, i)
            if si == -1:
                break
            if in_string(si, strings):
                i = si + len(bs)
                continue
            ei = text.find(be, si + len(bs))
            ei = ei + len(be) if ei != -1 else len(text)

            sl = text[:si].count('\n')
            el = text[:ei].count('\n')
            ls = text.rfind('\n', 0, si) + 1
            le = text.rfind('\n', 0, ei) + 1

            comments.append({
                'start': si,
                'end': ei,
                'line': sl,
                'line_end': el,
                'type': 'block',
                'col': si - ls,
                'col_end': ei - le
            })
            i = ei

    return sorted(comments, key=lambda x: x['start'])


def strip_auto(text, cfg):
    comments = find_comments(text, cfg)
    if not comments:
        return text, 0

    lines = text.split('\n')
    kill = set()
    partial = {}

    for c in comments:
        if c['type'] == 'line':
            ln = c['line']
            before = lines[ln][:c['col']].strip()
            if not before:
                kill.add(ln)
            else:
                partial.setdefault(ln, []).append((c['col'], c['col_end']))
        else:
            sl, el = c['line'], c['line_end']
            if sl == el:
                before = lines[sl][:c['col']].strip()
                after = lines[sl][c['col_end']:].strip()
                if not before and not after:
                    kill.add(sl)
                else:
                    partial.setdefault(sl, []).append((c['col'], c['col_end']))
            else:
                before = lines[sl][:c['col']].strip()
                after = lines[el][c['col_end']:].strip()
                if not before and not after:
                    kill.update(range(sl, el + 1))
                else:
                    partial.setdefault(sl, []).append((c['col'], len(lines[sl])))
                    kill.update(range(sl + 1, el))
                    partial.setdefault(el, []).append((0, c['col_end']))

    result = []
    for i, line in enumerate(lines):
        if i in kill:
            continue
        if i in partial:
            for s, e in sorted(partial[i], reverse=True):
                line = line[:s] + line[e:]
            line = line.rstrip()
            if line:
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result), len(comments)


def strip_manual(text, cfg, fpath):
    comments = find_comments(text, cfg)
    if not comments:
        return text, 0

    lines = text.split('\n')
    approved = []
    idx = 0
    total = len(comments)
    auto = False
    tui = TUI()

    while idx < total:
        c = comments[idx]
        ln = c['line']

        if not auto:
            tui.clear()
            w, h = tui.term_size()

            print('=' * w)
            print(f' VibeCleaner v{VERSION} '.center(w))
            print('=' * w)
            print(f'File: {fpath.name}')
            print(f'Progress: {idx + 1}/{total} | Line: {ln + 1}')
            print('=' * w)
            print()

            ctx = 2
            start = max(0, ln - ctx)
            end = min(len(lines), (c['line_end'] if c['type'] == 'block' else ln) + ctx + 1)

            for i in range(start, end):
                num = f'{i + 1:4d} | '

                if c['type'] == 'line' and i == ln:
                    before = lines[i][:c['col']]
                    comment = lines[i][c['col']:c['col_end']]
                    print(f'{tui.colors.yellow(num)}{before}{tui.colors.red(tui.colors.bold(comment))}')

                elif c['type'] == 'block':
                    sl, el = c['line'], c['line_end']
                    if i < sl or i > el:
                        print(f'{num}{lines[i]}')
                    elif sl == el and i == sl:
                        before = lines[i][:c['col']]
                        comment = lines[i][c['col']:c['col_end']]
                        after = lines[i][c['col_end']:]
                        print(f'{tui.colors.yellow(num)}{before}{tui.colors.red(tui.colors.bold(comment))}{after}')
                    elif i == sl:
                        before = lines[i][:c['col']]
                        comment = lines[i][c['col']:]
                        print(f'{tui.colors.yellow(num)}{before}{tui.colors.red(tui.colors.bold(comment))}')
                    elif i == el:
                        comment = lines[i][:c['col_end']]
                        after = lines[i][c['col_end']:]
                        print(f'{tui.colors.yellow(num)}{tui.colors.red(tui.colors.bold(comment))}{after}')
                    else:
                        print(f'{tui.colors.yellow(num)}{tui.colors.red(tui.colors.bold(lines[i]))}')
                else:
                    print(f'{num}{lines[i]}')

            print()
            print('=' * w)
            print('[Enter] Remove  [A] Remove All  [Arrow Keys] Navigate  [S] Skip  [Q] Quit')
            print('=' * w)

            key = tui.getch()

            if key == 'enter':
                approved.append(c)
                idx += 1
            elif key == 'a':
                auto = True
                approved.append(c)
                idx += 1
            elif key == 'right' or key == 'down':
                idx = min(idx + 1, total)
            elif key == 'left' or key == 'up':
                idx = max(idx - 1, 0)
            elif key == 's':
                idx += 1
            elif key == 'q':
                tui.clear()
                break
            else:
                idx = min(idx + 1, total)
        else:
            approved.append(c)
            idx += 1

    if not approved:
        return text, 0

    kill = set()
    partial = {}

    for c in approved:
        if c['type'] == 'line':
            ln = c['line']
            before = lines[ln][:c['col']].strip()
            if not before:
                kill.add(ln)
            else:
                partial.setdefault(ln, []).append((c['col'], c['col_end']))
        else:
            sl, el = c['line'], c['line_end']
            if sl == el:
                before = lines[sl][:c['col']].strip()
                after = lines[sl][c['col_end']:].strip()
                if not before and not after:
                    kill.add(sl)
                else:
                    partial.setdefault(sl, []).append((c['col'], c['col_end']))
            else:
                before = lines[sl][:c['col']].strip()
                after = lines[el][c['col_end']:].strip()
                if not before and not after:
                    kill.update(range(sl, el + 1))
                else:
                    partial.setdefault(sl, []).append((c['col'], len(lines[sl])))
                    kill.update(range(sl + 1, el))
                    partial.setdefault(el, []).append((0, c['col_end']))

    result = []
    for i, line in enumerate(lines):
        if i in kill:
            continue
        if i in partial:
            for s, e in sorted(partial[i], reverse=True):
                line = line[:s] + line[e:]
            line = line.rstrip()
            if line:
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result), len(approved)


def process_file(fpath, manual, backup):
    lang = detect_lang(fpath)
    if not lang or lang not in LANG_MAP:
        return None

    try:
        text = fpath.read_text(encoding='utf-8')
    except:
        try:
            text = fpath.read_text(encoding='latin-1')
        except:
            return None

    cfg = LANG_MAP[lang]
    new_text, removed = (strip_manual(text, cfg, fpath) if manual else strip_auto(text, cfg))

    if removed == 0:
        return {'file': fpath, 'removed': 0, 'changed': False}

    if backup:
        try:
            fpath.with_suffix(fpath.suffix + '.bak').write_bytes(fpath.read_bytes())
        except:
            pass

    try:
        fpath.write_text(new_text, encoding='utf-8', newline='\n')
    except:
        return None

    return {'file': fpath, 'removed': removed, 'changed': True}


def collect_files(paths, patterns):
    files = []

    for pstr in paths:
        p = Path(pstr).resolve()
        if not p.exists():
            continue

        if p.is_file():
            if is_text(p):
                lang = detect_lang(p)
                if lang and lang in LANG_MAP:
                    files.append(p)
        elif p.is_dir():
            for root, dirs, names in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for name in names:
                    if name.startswith('.'):
                        continue
                    fp = Path(root) / name
                    if should_ignore(fp, p, patterns):
                        continue
                    if is_text(fp):
                        lang = detect_lang(fp)
                        if lang and lang in LANG_MAP:
                            files.append(fp)

    return sorted(files)


def run(paths, manual, backup, ignore, parallel, quiet):
    t0 = time.time()
    patterns = load_ignore(ignore) if ignore else tuple()
    files = collect_files(paths, patterns)

    if not files:
        print('No files found')
        return 1

    if not quiet:
        print(f'VibeCleaner v{VERSION}')
        print('=' * 80)
        print(f'Files: {len(files)} | Mode: {"Manual" if manual else "Auto"}')
        if backup:
            print('Backup: Enabled')
        print('=' * 80)
        print()

    removed = changed = 0

    if parallel and not manual and len(files) > 1:
        workers = min(cpu_count(), len(files))
        with ProcessPoolExecutor(max_workers=workers) as exe:
            futures = {exe.submit(process_file, f, False, backup): f for f in files}
            for fut in as_completed(futures):
                res = fut.result()
                if res and res['changed']:
                    removed += res['removed']
                    changed += 1
                    if not quiet:
                        print(f"Done: {res['file'].name} ({res['removed']})")
    else:
        for fp in files:
            if not quiet and not manual:
                print(f'Processing: {fp.name}')
            res = process_file(fp, manual, backup)
            if res and res['changed']:
                removed += res['removed']
                changed += 1
                if not quiet and not manual:
                    print(f'Removed: {res["removed"]}')

    elapsed = time.time() - t0

    if not quiet:
        print()
        print('=' * 80)
        print(f'Processed: {changed}/{len(files)} | Comments: {removed} | Time: {fmt_time(elapsed)}')
        print('=' * 80)

    return 0


def main():
    desc = f'''VibeCleaner v{VERSION}

Strip comments from source code. Simple and effective.

Examples:
  %(prog)s project/
  %(prog)s file1.py file2.js
  %(prog)s project/ -m
  %(prog)s file.py -mb
  %(prog)s project/ -p -i .gitignore
'''

    p = ArgumentParser(description=desc, formatter_class=RawDescriptionHelpFormatter)
    p.add_argument('paths', nargs='+', help='files or directories')
    p.add_argument('-m', '--manual', action='store_true', help='manual review mode')
    p.add_argument('-b', '--backup', action='store_true', help='create backups')
    p.add_argument('-i', '--ignore', help='ignore patterns file')
    p.add_argument('-p', '--parallel', action='store_true', help='parallel processing')
    p.add_argument('-q', '--quiet', action='store_true', help='quiet mode')
    p.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}')

    args = p.parse_args()

    try:
        return run(args.paths, args.manual, args.backup, args.ignore, args.parallel, args.quiet)
    except KeyboardInterrupt:
        print('\nCancelled')
        return 130
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())