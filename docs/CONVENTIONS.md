# Coding Conventions

Here are some conventions to consider while developing code in this project.

## Python Style Guide

In this project we follow a set of well-known Python Style Guides and Conventions, establishing a
specific priority among them when they contradict each other, and with some exceptions in which we
apply our own rules.

The priority is defined as follows:

1. Our own conventions, detailed below
2. [PEP 20 – The Zen of Python](https://peps.python.org/pep-0020/)
3. [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0020/)
4. [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html)
5. [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)

### Our Conventions

Here is a short list of our own Python conventions. Some of them contradict the rules detailed on
the referenced style guides from above, and some of them just re-inforce their concepts. In case of
doubt, these are the ultimate rules that must be applied.

01. Follow The Zen of Python

02. Be absolutely PEP-8 compliant.

03. Use a maximum line lenght of 99 characters for python code, and preferrably for Markdown
    documnets too.

04. Write useful docstrings that help other developers understand what each object does or is for,
    as well as how to use it (e.g. which arguments it accespts).

05. Use sensible object names that are self-explaining. Developers should not need to read
    docstrings to understand what a function or class does. Docstrings should be only necessary
    only to dive deeper into how to use the objects, not to understand what they are.

06. Never add whitespace to empty lines. In other words, blank lines should be completely empty,
    whith nothing but a newline character.

07. Never add trailing whitespace. All non-empty lines should end with either an alphanumeric
    character or a symbol, but never with a whitespace.

08. Use blank lines to clearly distinguish and separate logical blocks.

09. Indentation changes (i.e. reducing indentation when an if branch finishes) does not replace the
    need of a blank line to mark the end of a logical block. More specifically, always leave a
    blank line before reducing indentaion unless the indented block only contains at most TWO
    statements and it is part of an `if/elif/else`, or `for/else`, or `try/except/finally` block.
    In all other cases, add a blank line before reducing indentation. And absolutely never
    de-indent two or more levels without adding a blank line, even for one-liners.

    **Good Examples:**

    ```python
    if something():
        do_something()
        do_something_again()   # This logical block ends here, so blank like below.

     if somethin_else():   # Multiple related one-liners, can be together.
         do_something_else()
     elif another_condition():
         do_another_thing()
     else:
         forget_it()

     for variable in some_loop():  # Separate this for from the previous if/else one.
         do_things_in_the_loop()
         if condition:
             break

         some_other_thing()   # Keep blank line above to separate from the inner if block
         even_more_things()

     else:   # keep blank line above because the for loop was more than 3 statements long.
         did_not_break()
    ```

    **Bad examples:**

    ```python
    if something():
        do_something()
    if something_else():   # Previous line is unrelated to this if, so it must be separated
        do_something_else()

    for variable in some_loop():
        do_something()
        if condition:
            do_something()
        do_something_else()   # This is not part of the previous if, so it must be separated
        do_more_things()
    else:   # Indented block above had more than 3 statements, so it must be separated
        return

    try:
        if something:
            return
    except:    # Double de-indentation, it must be separated
        pass
    ```

10. Let's repeat it: Absolutely never de-indent two or more levels without adding a blank line,
    even for one-liners.

11. Define objects (variables, classes, functions and methods) before they are used, and in the
    order in which they are used. In other words, never use a function, class or method before the
    line in which it is defined.

    If new code needs to be added to an object and the new code uses another object that is defined
    later in the module, re-order the module to put the second one above the first one.

    The only exception to this are cases in which two objects use each other. In this case, the one
    that is executed first in the most common use case of the module must be defined on **below**.

12. Type Hints should only be used in public objects that will be used by third party developers,
    and they should only be added if the entire public API if the module or package that is being
    developed already contains Type Hints.

    If a module or package does not contain Type Hints, do not add them in the new functions or
    classes. If at some point the decision to add Type Hints is made, they must be added at once to
    the entire public API of the module.

13. Do not user "Config" (or similar) dataclasses only to pass arguments down to functions and skip
    complains from linters. Arguments must alwasy be used, and if the number of arguments in a
    function or class is too large for the linting rules defined in the configuration, either
    increase the number or allowed arguments (up to a maximum of 10), or just rethink how the code
    is organized to avoid needing so many arguments.
