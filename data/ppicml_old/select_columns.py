#!/usr/bin/env python3
"""TUI to select which layouts (x_/y_/z_ column triplets) and other columns
to keep from nodes.tsv, then write nodes_new.tsv with only those columns.

Usage:
    python3 select_columns.py [input.tsv] [output.tsv]

Defaults: input=nodes.tsv, output=nodes_new.tsv (both in the current directory).
"""

import csv
import curses
import re
import sys
from pathlib import Path

LAYOUT_RE = re.compile(r"^([xyz])_(.+)$")


def parse_header(header):
    """Split header into layouts (name -> [x,y,z col names]) and other columns.

    A column belongs to a layout only if all three of x_<name>, y_<name>,
    z_<name> are present in the header; otherwise it is treated as a plain
    "other" column.
    """
    by_axis = {"x": {}, "y": {}, "z": {}}
    for col in header:
        m = LAYOUT_RE.match(col)
        if m:
            axis, name = m.groups()
            by_axis[axis][name] = col

    layout_names = sorted(
        set(by_axis["x"]) & set(by_axis["y"]) & set(by_axis["z"])
    )
    layouts = {name: (by_axis["x"][name], by_axis["y"][name], by_axis["z"][name])
               for name in layout_names}

    layout_cols = set()
    for cols in layouts.values():
        layout_cols.update(cols)

    other_cols = [c for c in header if c not in layout_cols]

    return layouts, other_cols


class Item:
    __slots__ = ("label", "checked", "kind", "cols")

    def __init__(self, label, cols, kind):
        self.label = label
        self.checked = True
        self.kind = kind  # "layout" or "column"
        self.cols = cols  # list of underlying column names


def build_items(layouts, other_cols):
    items = []
    for name, cols in layouts.items():
        items.append(Item(f"layout: {name}", list(cols), "layout"))
    for col in other_cols:
        items.append(Item(f"column: {col}", [col], "column"))
    return items


def run_tui(stdscr, items):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # selected row
    curses.init_pair(2, curses.COLOR_GREEN, -1)                  # checked mark
    curses.init_pair(3, curses.COLOR_YELLOW, -1)                 # save button
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW) # save button focused

    n = len(items)
    SAVE_INDEX = n  # virtual row for the Save button
    CANCEL_INDEX = n + 1
    cursor = 0
    top = 0
    saved = False

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        header_lines = [
            "nodes.tsv column selector",
            "Up/Down: move  Space: toggle  a: check all  n: uncheck all",
            "l: toggle all layouts  o: toggle all other columns",
            "Enter on Save: write output   q / Esc: quit without saving",
            "",
        ]
        for i, line in enumerate(header_lines):
            if i < max_y:
                stdscr.addnstr(i, 0, line, max_x - 1)

        list_top = len(header_lines)
        footer_lines = 2
        visible_rows = max(1, max_y - list_top - footer_lines)

        # keep cursor visible
        if cursor < top:
            top = cursor
        elif cursor >= top + visible_rows:
            top = cursor - visible_rows + 1

        row = list_top
        for idx in range(top, min(n, top + visible_rows)):
            item = items[idx]
            mark = "x" if item.checked else " "
            text = f"[{mark}] {item.label}"
            is_cursor = idx == cursor
            attr = curses.color_pair(1) if is_cursor else curses.A_NORMAL
            if not is_cursor and item.checked:
                attr = curses.color_pair(2)
            stdscr.addnstr(row, 0, text.ljust(max_x - 1), max_x - 1, attr)
            row += 1

        # Save / Cancel buttons pinned at bottom
        btn_row = max_y - 2
        save_attr = curses.color_pair(4) if cursor == SAVE_INDEX else curses.color_pair(3)
        cancel_attr = curses.color_pair(1) if cursor == CANCEL_INDEX else curses.A_NORMAL
        if btn_row > row:
            stdscr.addnstr(btn_row, 0, " [ Save ] ", 10, save_attr)
            stdscr.addnstr(btn_row, 12, " [ Cancel ] ", 12, cancel_attr)
            checked_n = sum(1 for it in items if it.checked)
            status = f"{checked_n}/{n} selected"
            stdscr.addnstr(btn_row, max_x - len(status) - 1, status, len(status))

        stdscr.refresh()

        try:
            ch = stdscr.getch()
        except KeyboardInterrupt:
            return False

        total_rows = n + 2  # items + save + cancel
        if ch in (curses.KEY_UP, ord('k')):
            cursor = (cursor - 1) % total_rows
        elif ch in (curses.KEY_DOWN, ord('j')):
            cursor = (cursor + 1) % total_rows
        elif ch == ord(' '):
            if cursor < n:
                items[cursor].checked = not items[cursor].checked
        elif ch == ord('a'):
            for it in items:
                it.checked = True
        elif ch == ord('n'):
            for it in items:
                it.checked = False
        elif ch == ord('l'):
            layout_items = [it for it in items if it.kind == "layout"]
            new_state = not all(it.checked for it in layout_items) if layout_items else True
            for it in layout_items:
                it.checked = new_state
        elif ch == ord('o'):
            col_items = [it for it in items if it.kind == "column"]
            new_state = not all(it.checked for it in col_items) if col_items else True
            for it in col_items:
                it.checked = new_state
        elif ch in (curses.KEY_ENTER, 10, 13):
            if cursor == SAVE_INDEX:
                saved = True
                break
            elif cursor == CANCEL_INDEX:
                saved = False
                break
            else:
                items[cursor].checked = not items[cursor].checked
        elif ch in (27, ord('q')):
            saved = False
            break

    return saved


def write_output(input_path, output_path, selected_cols):
    with open(input_path, newline="", encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.reader(fin, delimiter="\t")
        writer = csv.writer(fout, delimiter="\t", lineterminator="\n")
        header = next(reader)
        idx_map = [header.index(c) for c in selected_cols]
        writer.writerow(selected_cols)
        for row in reader:
            writer.writerow([row[i] if i < len(row) else "" for i in idx_map])


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("nodes.tsv")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("nodes_new.tsv")

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)

    layouts, other_cols = parse_header(header)
    if not layouts and not other_cols:
        print("No columns found in header.", file=sys.stderr)
        sys.exit(1)

    items = build_items(layouts, other_cols)

    saved = curses.wrapper(run_tui, items)

    if not saved:
        print("Cancelled, no file written.")
        return

    selected_cols = []
    for col in header:
        for item in items:
            if col in item.cols:
                if item.checked:
                    selected_cols.append(col)
                break

    if not selected_cols:
        print("No columns selected, nothing written.", file=sys.stderr)
        sys.exit(1)

    write_output(input_path, output_path, selected_cols)
    print(f"Wrote {len(selected_cols)} columns to {output_path}")


if __name__ == "__main__":
    main()
