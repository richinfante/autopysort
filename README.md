# Autopysort

This *experimental* tool re-organizes python files in alphabetical order. This can be useful for large files full of mostly pure utility functions. 

Internally, this uses `libcst` for transformations, and checks it's work using pyflakes. The pyflakes checking *can* be disabled, and we're working on better detection of error cases.

## Usage
```bash
python3 sortpy.py [--ignore-syntax-errors] <file globs...>

#.. or after install..#
sortpy [--ignore-syntax-errors] <file globs...>
```

## Install
```bash
sudo make install
```

## Warning!
**This edits files in-place. Please don't use it on code that's not in source control, or it's entirely possible it might be lost forever if this messes up.**

## Known Issues
- Some files like entrypoints which rely on functions coming before certain if statements / calls will not function properly if ran through this tool.