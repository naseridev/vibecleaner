# VibeCleaner

A high-performance comment removal utility for stripping comments from source code across multiple programming languages. Built for efficiency, accuracy, and developer control.

## Overview

VibeCleaner is designed to clean codebases by intelligently removing comments while preserving code integrity. It supports over 40 programming languages, provides manual review mode, and scales with parallel processing capabilities.

## Why VibeCleaner?

Modern AI coding assistants (Gemini, ChatGPT, etc.) have a nasty habit of polluting your code with excessive comments. Every. Single. Line. Explained. Like you're five.

Look, comments are not documentation. Comments are excuses for bad code. If your code needs a comment to be understood, you wrote bad code. Rewrite it.

But we're stuck with AI models that think `// Add 1 to counter` above `counter++` is helpful. It's not. It's noise. It wastes your precious token limits. Makes code harder to read, not easier.

VibeCleaner exists because:
1. **AI-generated code is comment hell** - Gemini and friends can't help themselves
2. **Free tier limits are brutal** - Every comment eats into your daily quota
3. **You hit rate limits faster** - More tokens = faster throttling = wasted time
4. **Clean code speaks for itself** - Good code doesn't need novels attached
5. **Comments belong at the END** - Write code first, document later if you must

Using free AI agents? You're probably hitting limits constantly. Half your tokens are wasted on useless comments. Strip them. Get more actual work done before you hit the wall.

Use VibeCleaner during development. Strip the garbage. Keep your codebase clean. Stretch your free tier further. Add real documentation when the project is done, not during every iteration.

Code should be obvious. If it's not obvious, fix the code. Don't paper over bad code with comments.

## Features

- Multi-language support for 40+ file types
- Smart comment detection (line and block comments)
- String-aware parsing (never corrupts strings)
- Manual review mode with interactive TUI
- Parallel processing with multi-core utilization
- Automatic backup creation
- Pattern-based file filtering
- Colored terminal output with fallback support
- Progress tracking and detailed statistics

## Installation

Clone the repository and ensure Python 3.7+ is installed:

```bash
git clone https://github.com/naseridev/vibecleaner.git
```

```bash
cd vibecleaner
```

```bash
chmod +x vclr.py
```

## Usage

### Basic Syntax

```bash
./vclr.py [OPTIONS] PATH [PATH ...]
```

### Examples

Clean all files in a directory (automatic mode):
```bash
./vclr.py /path/to/project
```

Clean specific files:
```bash
./vclr.py file1.py file2.js file3.cpp
```

Manual review mode (review each comment before removal):
```bash
./vclr.py /path/to/project -m
```

Create backups before cleaning:
```bash
./vclr.py /path/to/project -b
```

Use ignore patterns:
```bash
./vclr.py /path/to/project -i .gitignore
```

Enable parallel processing:
```bash
./vclr.py /path/to/project -p
```

Combine multiple options:
```bash
./vclr.py /path/to/project -mbp -i .gitignore
```

## Options

| Option | Description |
|--------|-------------|
| `-m, --manual` | Enable manual review mode with interactive TUI |
| `-b, --backup` | Create .bak backup files before modification |
| `-i, --ignore` | Path to ignore patterns file |
| `-p, --parallel` | Enable parallel processing for faster cleaning |
| `-q, --quiet` | Suppress progress output |
| `-v, --version` | Display version information |

## Manual Review Mode

When using `-m` flag, VibeCleaner displays each comment interactively:

- **Enter**: Remove the current comment
- **A**: Remove all remaining comments automatically
- **Arrow Keys**: Navigate between comments (up/down/left/right)
- **S**: Skip the current comment
- **Q**: Quit and save changes

The TUI highlights:
- Line numbers in yellow
- Comments in red bold
- Context lines around each comment

## Supported Languages

### C-Style Languages
JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Swift, Kotlin, Scala, Dart, Objective-C, Groovy, V, D, Zig

### Script Languages
Python, Shell (bash/sh/zsh), Ruby, Perl, PHP, Lua, R, PowerShell

### Functional Languages
Haskell, OCaml, F#, Elixir, Erlang, Clojure, Lisp, Elm

### Markup & Config
HTML, XML, CSS, SCSS, Sass, Less, YAML, TOML, JSON, INI

### Others
SQL, Vim Script, Assembly, Batch, Pascal, VB, Ada, VHDL, Nim, Crystal, Julia, Tcl, CoffeeScript

## Comment Detection

VibeCleaner intelligently detects and removes:

- **Line comments**: `//`, `#`, `--`, `;`, `'`, etc.
- **Block comments**: `/* */`, `<!-- -->`, `""" """`, `=begin =end`, etc.
- **Nested comments**: Properly handles nested structures
- **String literals**: Never corrupts strings containing comment-like syntax

### Example

**Before:**
```python
# This is a comment
def hello():
    """This is a docstring"""  # Keep docstrings
    message = "# Not a comment"  # This is removed
    print(message)  # This too
```

**After:**
```python
def hello():
    """This is a docstring"""
    message = "# Not a comment"
    print(message)
```

## Ignore Patterns

Create a file with patterns to exclude specific files or directories:

```
node_modules
*.log
build/
dist/
.git
__pycache__
*.min.js
vendor/
```

## Performance Considerations

- Parallel processing activates automatically with `-p` flag on multi-core systems
- Maximum file size: 10 MB per file
- Files must be valid text files (binary files are skipped)
- Memory-efficient processing for large codebases

## Color Support

VibeCleaner automatically detects terminal capabilities:

- **Supported**: Modern terminals on Linux/macOS/Windows 10+
- **Fallback**: Automatically disables colors on unsupported terminals
- **Windows**: Enables Virtual Terminal Processing when available

## Backup System

When using `-b` flag:
- Original files are saved with `.bak` extension
- Example: `main.py` → `main.py.bak`
- Backups are created before any modifications
- Safe to run multiple times (overwrites old backups)

## Output Statistics

VibeCleaner provides detailed statistics:

```
VibeCleaner v1.0.0
================================================================================
Files: 15 | Mode: Auto
Backup: Enabled
================================================================================

Processing: main.py
Removed: 23
Processing: utils.js
Removed: 45
...

================================================================================
Processed: 15/15 | Comments: 342 | Time: 1.23s
================================================================================
```

## Exit Codes

- 0: Success
- 1: Fatal error
- 130: User interruption (Ctrl+C)

## Requirements

- Python 3.7 or higher
- No external dependencies required
- Works on Linux, macOS, and Windows

## Safety Features

- **Non-destructive by default**: Test without `-b` flag first
- **String-aware**: Never corrupts string literals
- **Manual mode**: Review changes before applying
- **Backup support**: Always create backups with `-b`
- **Text file detection**: Automatically skips binary files

## Contributing

Contributions are welcome. Submit pull requests with clear descriptions and test coverage.

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, open an issue on the GitHub repository.

## Acknowledgments

Built with a focus on:
- Code simplicity and readability
- Zero external dependencies
- Cross-platform compatibility
- Developer productivity