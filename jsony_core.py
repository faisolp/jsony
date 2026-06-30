"""
jsony_core.py — JSONY recursive-descent parser.

Vendored and adapted from Kyle-Helmick/Python-JSONY (GPL-3.0, archived):
    https://github.com/Kyle-Helmick/Python-JSONY

Changes from the original main.py:
  - Errors raise JsonyError instead of print()+exit(1), so it is usable
    as a library.
  - Added .to_python() on the tree nodes to recover real Python values
    (dict / list / str / float / bool / None).
  - Added a tolerant pre-tokenizer (strip insignificant whitespace) since
    the original parser requires a whitespace-free single line.
  - Added loads() convenience wrapper.

This keeps JSONY as the *parse path* (per request), while the CLI on top
uses it to read/validate the append-only log.
"""


class JsonyError(ValueError):
    """Raised on any parse error."""


def _strip_ws(s):
    """Remove insignificant whitespace and comments (keep string contents)."""
    out = []
    in_str = False
    esc = False
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        # not in string: handle comments
        if ch == "/" and i + 1 < n and s[i + 1] == "/":
            i += 2
            while i < n and s[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and s[i + 1] == "*":
            i += 2
            while i + 1 < n and not (s[i] == "*" and s[i + 1] == "/"):
                i += 1
            i += 2
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
        elif ch in " \t\r\n":
            pass
        else:
            out.append(ch)
        i += 1
    return "".join(out)


class _Num:
    valid = set("0123456789")

    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.val = None
        self._consume()

    def _consume(self):
        pop = self.arr.pop(0)
        buf = pop
        self.popped.append(pop)
        decimal = False
        while self.arr and (self.arr[0] in self.valid or self.arr[0] == "."):
            if decimal and self.arr[0] == ".":
                raise JsonyError("only one decimal allowed in numbers")
            pop = self.arr.pop(0)
            buf += pop
            self.popped.append(pop)
            if pop == ".":
                decimal = True
        if not self.arr:
            raise JsonyError("expected more characters after number")
        self.val = float(buf)

    def to_python(self):
        return self.val


class _Val:
    valid = set("0123456789")

    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.mid = ""
        self._consume()

    def _string(self):
        pop = self.arr.pop(0)  # opening quote
        self.popped.append(pop)
        buf = []
        esc = False
        while self.arr and (esc or self.arr[0] != '"'):
            pop = self.arr.pop(0)
            self.popped.append(pop)
            if esc:
                buf.append({'n': '\n', 't': '\t', 'r': '\r'}.get(pop, pop))
                esc = False
            elif pop == "\\":
                esc = True
            else:
                buf.append(pop)
        if not self.arr:
            raise JsonyError("expected closing quote")
        pop = self.arr.pop(0)  # closing quote
        self.popped.append(pop)
        self.mid = "".join(buf)

    def _bool(self):
        for word, value in (("false", False), ("true", True), ("null", None)):
            if self.arr[0] == word[0]:
                for char in word:
                    if self.arr and self.arr[0] == char:
                        self.popped.append(self.arr.pop(0))
                    else:
                        raise JsonyError("malformed literal, expected %r" % word)
                self.mid = value
                return
        raise JsonyError("expected literal true|false|null")

    def _consume(self):
        c = self.arr[0]
        if c == '"':
            self._string()
        elif c == "[":
            self.mid = _Array(self.arr, self.popped)
        elif c == "{":
            self.mid = _Json(self.arr, self.popped)
        elif c in self.valid or c == "-":
            self.mid = _Num(self.arr, self.popped)
        elif c in "tfn":
            self._bool()
        else:
            raise JsonyError("expected value, got %r" % c)

    def to_python(self):
        if isinstance(self.mid, (_Array, _Json, _Num)):
            return self.mid.to_python()
        return self.mid


class _ArrayElement:
    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.items = []
        self._consume()

    def _consume(self):
        self.items.append(_Val(self.arr, self.popped))
        if not self.arr:
            raise JsonyError("no closing ']' for array")
        while self.arr[0] == ",":
            self.popped.append(self.arr.pop(0))
            if self.arr and self.arr[0] == "]":  # tolerant: trailing comma
                break
            self.items.append(_Val(self.arr, self.popped))
            if not self.arr:
                raise JsonyError("no closing ']' for array")

    def to_python(self):
        return [v.to_python() for v in self.items]


class _Array:
    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.mid = None
        self._consume()

    def _consume(self):
        if len(self.arr) < 2:
            raise JsonyError("array too short")
        pop = self.arr.pop(0)
        self.popped.append(pop)
        if pop != "[":
            raise JsonyError("expected '['")
        if self.arr[0] == "]":
            self.popped.append(self.arr.pop(0))
            return
        self.mid = _ArrayElement(self.arr, self.popped)
        if not self.arr or self.arr[0] != "]":
            raise JsonyError("expected closing ']'")
        self.popped.append(self.arr.pop(0))

    def to_python(self):
        return self.mid.to_python() if self.mid else []


class _Item:
    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.key = None
        self.value = None
        self._consume()

    def _consume(self):
        if self.arr[0] != '"':
            raise JsonyError("expected key opening quote")
        self.popped.append(self.arr.pop(0))
        key = []
        esc = False
        while self.arr and (esc or self.arr[0] != '"'):
            pop = self.arr.pop(0)
            self.popped.append(pop)
            if esc:
                key.append({'n': '\n', 't': '\t', 'r': '\r'}.get(pop, pop))
                esc = False
            elif pop == "\\":
                esc = True
            else:
                key.append(pop)
        if not self.arr:
            raise JsonyError("expected key closing quote")
        self.popped.append(self.arr.pop(0))
        self.key = "".join(key)
        if not self.arr or self.arr[0] != ":":
            raise JsonyError("expected ':' between key and value")
        self.popped.append(self.arr.pop(0))
        self.value = _Val(self.arr, self.popped)

    def to_python(self):
        return self.key, self.value.to_python()


class _JsonElement:
    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.items = []
        self._consume()

    def _consume(self):
        self.items.append(_Item(self.arr, self.popped))
        if not self.arr:
            raise JsonyError("no closing '}' for object")
        while self.arr[0] == ",":
            self.popped.append(self.arr.pop(0))
            if self.arr and self.arr[0] == "}":  # tolerant: trailing comma
                break
            self.items.append(_Item(self.arr, self.popped))
            if not self.arr:
                raise JsonyError("no closing '}' for object")

    def to_python(self):
        return dict(it.to_python() for it in self.items)


class _Json:
    def __init__(self, arr, popped):
        self.arr, self.popped = arr, popped
        self.mid = None
        self._consume()

    def _consume(self):
        if len(self.arr) < 2:
            raise JsonyError("object too short")
        pop = self.arr.pop(0)
        self.popped.append(pop)
        if pop != "{":
            raise JsonyError("expected '{'")
        if self.arr[0] == "}":
            self.popped.append(self.arr.pop(0))
            return
        self.mid = _JsonElement(self.arr, self.popped)
        if not self.arr or self.arr[0] != "}":
            raise JsonyError("expected closing '}'")
        self.popped.append(self.arr.pop(0))

    def to_python(self):
        return self.mid.to_python() if self.mid else {}


class jsony_parser:
    """Parse a JSONY object string into a tree. .root holds the top object."""

    def __init__(self, test_str):
        self.arr = list(_strip_ws(test_str))
        self.popped = []
        if not self.arr:
            raise JsonyError("empty input")
        self.root = _Json(self.arr, self.popped)
        if self.arr:
            raise JsonyError("trailing characters after object: %r" % "".join(self.arr))

    def to_python(self):
        return self.root.to_python()


def loads(text):
    """Parse a JSONY object string and return a Python dict."""
    return jsony_parser(text).to_python()
