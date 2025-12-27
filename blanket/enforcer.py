# ruff: noqa: T201

"""Enforce blank lines on dedent transitions.

Rules:
1) If indentation depth is reduced by 2 levels or more between consecutive
   statements, require exactly ONE blank line between them.
2) If indentation depth is reduced by 1 level, require exactly ONE blank line
   between them, EXCEPT when the next thing is a continuation clause
   (else/elif/except/finally) AND the ended block has <= 3 statements AND the
   ended block contains no further nested indented blocks.
"""

import ast
from pathlib import Path


def get_indentation(line):
    """Returns the number of spaces at the start of the line."""
    return len(line) - len(line.lstrip())


def is_blank_or_comment(line):
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


class Blanket:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.source_lines = self.filepath.read_text(encoding="utf-8").splitlines(keepends=True)

        try:
            self.tree = ast.parse("".join(self.source_lines))
        except SyntaxError:
            # If code is invalid, we can't enforce style.
            self.tree = None

        self.insertions = set()  # Stores line numbers where blank line should be inserted

    def check(self):
        if not self.tree:
            return False

        # Traverse the tree looking for block transitions
        self._visit_block(self.tree.body)

        # Also walk all nodes to find nested blocks
        for node in ast.walk(self.tree):
            if hasattr(node, "body") and isinstance(node.body, list):
                self._visit_block(node.body)

            if hasattr(node, "orelse") and isinstance(node.orelse, list):
                self._visit_block(node.orelse)

            if hasattr(node, "finalbody") and isinstance(node.finalbody, list):
                self._visit_block(node.finalbody)

            if hasattr(node, "handlers") and isinstance(node.handlers, list):
                self._visit_block(node.handlers)

        return self._apply_changes()

    def _visit_block(self, statements):
        """Analyze a list of statements (a block) to find transitions."""
        if not statements:
            return

        for i in range(len(statements) - 1):
            current_stmt = statements[i]
            next_stmt = statements[i + 1]

            # Find the physically last line of the current statement (including children)
            last_leaf = self._get_last_leaf(current_stmt)

            # Identify line numbers (1-based)
            end_line_idx = last_leaf.end_lineno - 1
            start_line_idx = next_stmt.lineno - 1

            # Get indentation levels from source to handle multi-line dedents correctly
            # We look at the actual line in source to see where the text starts
            end_line_text = self.source_lines[end_line_idx]
            next_line_text = self.source_lines[start_line_idx]

            current_indent = get_indentation(end_line_text)
            next_indent = get_indentation(next_line_text)

            # We only care about DEDENT (reduction in indentation)
            # However, looking at siblings in the same block (flattened list),
            # they usually have the SAME indentation.
            #
            # The "Dedent" the user cares about usually happens:
            # 1. Between a compound statement end and the next sibling (e.g., If -> Next stmt)
            # 2. Inside a compound statement (e.g., If body -> Else)

            # Case A: Transition from a Compound Statement to Sibling
            # logic: If current_stmt has nested blocks, its last line might be deep.
            if current_indent > next_indent:
                self._check_padding_rules(
                    last_leaf,
                    next_stmt,
                    current_indent,
                    next_indent,
                    is_continuation=False,
                    block_stmt_count=None,
                )

        # Case B: Internal Transitions (If -> Else, Try -> Except)
        # We iterate the statements again to check *inside* compound statements
        for stmt in statements:
            self._check_internal_transitions(stmt)

    def _check_internal_transitions(self, node):
        """Check transitions like If-body->Else and Try-body->Except."""
        self._check_if_transitions(node)
        self._check_try_transitions(node)

    def _check_if_transitions(self, node):
        if not (isinstance(node, ast.If) and node.orelse):
            return

        last_node_of_body = self._get_last_leaf(node.body[-1])

        end_line_idx = last_node_of_body.end_lineno - 1
        curr_indent = get_indentation(self.source_lines[end_line_idx])

        continuation_line_idx = self._find_next_code_line(end_line_idx + 1)
        if continuation_line_idx is None:
            return

        cont_indent = get_indentation(self.source_lines[continuation_line_idx])
        if curr_indent <= cont_indent:
            return

        self._check_padding_rules(
            last_node_of_body,
            type("obj", (object,), {"lineno": continuation_line_idx + 1}),
            curr_indent,
            cont_indent,
            is_continuation=True,
            block_stmt_count=len(node.body),
        )

    def _check_try_transitions(self, node):
        if not isinstance(node, ast.Try):
            return

        if node.handlers:
            last_node_body = self._get_last_leaf(node.body[-1])

            end_idx = last_node_body.end_lineno - 1
            curr_indent = get_indentation(self.source_lines[end_idx])

            except_line_idx = self._find_next_code_line(end_idx + 1)
            if except_line_idx is None:
                return

            cont_indent = get_indentation(self.source_lines[except_line_idx])

            if curr_indent > cont_indent:
                self._check_padding_rules(
                    last_node_body,
                    type("obj", (object,), {"lineno": except_line_idx + 1}),
                    curr_indent,
                    cont_indent,
                    is_continuation=True,
                    block_stmt_count=len(node.body),
                )

        if not node.finalbody:
            return

        preceding_source = node.body
        if node.handlers:
            preceding_source = node.handlers[-1].body

        if node.orelse:
            preceding_source = node.orelse

        last_node = self._get_last_leaf(preceding_source[-1])
        end_idx = last_node.end_lineno - 1
        curr_indent = get_indentation(self.source_lines[end_idx])

        finally_line_idx = self._find_next_code_line(end_idx + 1)
        if finally_line_idx is None:
            return

        cont_indent = get_indentation(self.source_lines[finally_line_idx])

        if curr_indent > cont_indent:
            self._check_padding_rules(
                last_node,
                type("obj", (object,), {"lineno": finally_line_idx + 1}),
                curr_indent,
                cont_indent,
                is_continuation=True,
                block_stmt_count=len(preceding_source),
            )

    def _get_last_leaf(self, node):
        """Recursively finds the physically last statement in a node tree."""
        # If node has 'body', 'orelse', 'finalbody', check them.
        # We want the node with the highest line number.
        max_node = node

        children = []
        if hasattr(node, "body") and isinstance(node.body, list) and node.body:
            children.extend(node.body)

        if hasattr(node, "orelse") and isinstance(node.orelse, list) and node.orelse:
            children.extend(node.orelse)

        if hasattr(node, "handlers") and isinstance(node.handlers, list) and node.handlers:
            children.extend(node.handlers)

        if hasattr(node, "finalbody") and isinstance(node.finalbody, list) and node.finalbody:
            children.extend(node.finalbody)

        for child in children:
            leaf = self._get_last_leaf(child)
            if leaf.end_lineno > max_node.end_lineno:
                max_node = leaf

        return max_node

    def _find_next_code_line(self, start_idx):
        """Finds the next index that is not blank or comment."""
        for i in range(start_idx, len(self.source_lines)):
            if not is_blank_or_comment(self.source_lines[i]):
                return i

        return None

    def _check_padding_rules(
        self,
        prev_node,
        next_node_or_obj,
        prev_indent,
        next_indent,
        is_continuation,
        block_stmt_count,
    ):
        # 4 spaces per level
        level_drop = (prev_indent - next_indent) / 4.0

        # Determine strictness
        needs_blank = False

        # Rule 1: Drop >= 2 levels -> Mandatory blank
        if level_drop >= 2:
            needs_blank = True

        # Rule 2: Drop 1 level
        elif level_drop >= 0.5:  # Allow fuzzy match for 1 level (approx 2-4 spaces)
            if not is_continuation:
                # Standard dedent (end of loop, etc) -> Mandatory blank
                needs_blank = True
            elif block_stmt_count is not None and block_stmt_count > 3:
                needs_blank = True

        if needs_blank:
            self._ensure_blank_between(prev_node.end_lineno, next_node_or_obj.lineno)

    def _ensure_blank_between(self, end_lineno, next_lineno):
        """Ensure there is a blank line between two 1-based line numbers."""
        # Convert to 0-based index
        start_search = end_lineno
        end_search = next_lineno - 1  # Up to the line before the next code

        has_blank = False
        for i in range(start_search, end_search):
            if not self.source_lines[i].strip():
                has_blank = True
                break

        if not has_blank:
            # We insert specifically at the start of the next block
            # (or immediately after the previous block, order matters less as long as it's between)
            # To avoid disrupting comments attached to the next block, usually inserting
            # after the previous block is safer, but standard formatters usually prepend empty
            # lines to the next block.

            # We store insertion point as (index, string)
            # We use next_lineno - 1 (0-based) as the insertion index
            self.insertions.add(next_lineno - 1)

    def _apply_changes(self):
        if not self.insertions:
            return False

        # Sort reverse to insert without shifting indices
        for idx in sorted(self.insertions, reverse=True):
            self.source_lines.insert(idx, "\n")

        self.filepath.write_text("".join(self.source_lines), encoding="utf-8")

        return True


def enforce(filepaths):
    """Apply blanket formatting to files. Returns True if any changes are made."""
    has_changes = False
    for filepath in filepaths:
        enforcer = Blanket(filepath)
        if enforcer.check():
            print(f"Fixed blank lines in: {filepath}")
            has_changes = True

    return has_changes
