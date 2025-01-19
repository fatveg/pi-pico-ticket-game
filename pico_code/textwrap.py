# Simple text-wrapping funtction, to take a string s and a width width, and
# return a list of strings, each no more than width characters long.
# Function tries to split on whitespace, but will break words if necessary.
# If joiner is specified, the returned list will be joined with it,
# otherwise a newline will be used.
# If joiner is None, the function returns a list of strings.
# If width is not specified, use a width of 70.
def wrap(s, width=70, joiner="\n"):
    words = s.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > width:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word

    if current_line:
        lines.append(current_line)
    if joiner is None:
        return lines
    else:
        return joiner.join(lines)
