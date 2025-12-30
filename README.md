[![PyPI version](https://img.shields.io/pypi/v/blanken)](https://pypi.org/project/blanken/)
![License](https://img.shields.io/pypi/l/blanken)
![Python versions](https://img.shields.io/pypi/pyversions/blanken)

# Blanken

Blank Line Enforcement for Python

## Overview

Blanken is a Python code auto-formatter that enforces separation of logical code blocks via proper
usage of blank lines.

It uses indentation changes and keywords as the primary way to know where logical blocks start or
end, and inserts blank lines to separate them if they are missing.

## Usage

Install with pip

```bash
pip install blanken
```

Run on one or more files to insert blank lines where required:

```bash
blanken path/to/file.py
```

Use from Python:

```python
from blanken import enforce

enforce(["path/to/file.py"])
```

## Pre-commit

Add the hook to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/csala/blanken
  rev: v0.1.0
  hooks:
  - id: blanken
```

This hook will auto-format the files and fail if any file has been modified by blanken.

# Philosophy

The idea behind Blanken is to guarantee that source code is easy to read and understand at first
glance with as little mental effort as possible. And we, the blanken authors, believe that blank
lines play a super important role in this "first glance" understanding: by using them to properly
separate logically unrelated blocks of code, we help the brain quickly understand the context in
which the code that is being read operates while keeping it isolated from other unrelated blocks.

Identifying which lines of code are related or unrelated with simple rules that do not leverage
semantic understanding of the code is really hard. For this reason, blanken only enforces a few
simple rules based on keywords and indented blocks: We understand that when indentation is reduced,
the lines that follow are logically unrelated to the previous ones, with the exception of some
special continuation blocks like else or elif, where the lines that follow may need to be kept in
consideration to fully understand the previous ones.

## Enforced rules

### Dedent by 2+ levels requires one blank line

If we find a line that is has 2 or more indentation levels than the previous one, we know for sure
that the lines that follow belong to a new logical block, because it cannot be a continuation
block.

Therefore, we enforce a blank line.

**Bad:**

```python
if outer():
    if inner():
        do_inner()
do_next()
```

**Corrected:**

```python
if outer():
    if inner():
        do_inner()

do_next()
```

### Dedent by 1 level requires one blank line if no continuation keyword is found.

If we find a line that has 1 indentation level less than the previous one, we consider that it is
unrelated to the previous one if it does not start with any of the following continuation keywords:

- `else`
- `elif`
- `except`
- `finally`

**Good:**

```python
if something:
    do_something()
elif something_else:
    do_something_else()
else:
    do_another_thing()

try:
    something_dangerous()
except SomeException:
    log_the_error()
finally:
    clean_things_up()
```

**Bad:**

```python
for item in items:
    handle(item)
while some_condition:
    run_some_logic()
log_done()
```

**Corrected:**

```python
for item in items:
    handle(item)

while some_condition:
    run_some_logic()

log_done()
```

### Dedent by 1 level requires one blank line if block is too long

If we find a line that has 1 indentation level less than the previous one and is followed by one of
the continuation keywords listed above, we do not require a blank line if the block is _short_.

If the indented block is too _long or complex_, we understand that the block will need to be read
and understood on its own, and that it is better to separate it visually from the one that follows,
even if the next one starts with one of the continuation lines.

In particular, if the indented block has more than 3 top-level statements, we require a blank line.

**Bad:**

```python
if condition:
    one()
    two()
    three()
    four()
else:
    five()
```

**Corrected:**

```python
if condition:
    one()
    two()
    three()
    four()

else:
    five()
```

The example above seems probably simple, but consider the next one. Bear in mind that only
top-level statements are counted:

**Bad:**

```python
if condition:
    one()
    if two:
        nested_one()
        nested_two()
    else:
        nested_three()

    for item in three:
        nested_four()
        for nested_five:
            nested_six()
            nested_seven()

    four()
else:
    five()
```

In a situation like the one above, one could easily be tricked into missing the `four()` statement,
since visually it falls closer than the `five()` call that is unrelated.

So we enforce a blank line:

**Corrected:**

```python
if condition:
    one()
    if two:
        nested_one()
        nested_two()
    else:
        nested_three()

    for item in three:
        nested_four()
        for nested_five:
            nested_six()
            nested_seven()

    four()

else:
    five()
```

## Development Roadmap

- [x] Standalone script to run on individual files
- [x] Installable package and cli tool to run on individual files
- [x] Pre-commit hook
- [ ] Run recursively on folders
- [ ] Separate validation from file formatting
- [ ] Add discovery CLI options (such as exclude or include)
- [ ] Read options from pyproject
- [ ] Add formatting options
