import re
import unicodedata
import zlib


PAGE_WIDTH = 595.28
PAGE_HEIGHT = 841.89
LEFT = 56
RIGHT = 56
TOP = 56
BOTTOM = 48


def _plain_text(markdown: str) -> str:
    value = re.sub(r"\*\*(.+?)\*\*", r"\1", markdown)
    value = re.sub(r"\*(.+?)\*", r"\1", value)
    value = value.replace("`", "")
    value = value.replace("&nbsp;", " ")
    return value


def _pdf_text(value: str) -> str:
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", value.replace("\u20b9", "INR "))
        if not unicodedata.combining(char)
    )
    encoded = normalized.encode("cp1252", errors="replace")
    return "<" + encoded.hex().upper() + ">"


def _wrap(text: str, font_size: float, max_width: float) -> list[str]:
    max_chars = max(24, int(max_width / (font_size * 0.51)))
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        while len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


class _PdfLayout:
    def __init__(self) -> None:
        self.pages: list[list[str]] = [[]]
        self.y = PAGE_HEIGHT - TOP

    def _new_page(self) -> None:
        self.pages.append([])
        self.y = PAGE_HEIGHT - TOP

    def _ensure_space(self, height: float) -> None:
        if self.y - height < BOTTOM:
            self._new_page()

    def text(self, value: str, *, size: float, font: str = "F1", x: float = LEFT, color: str = "0.15 0.17 0.19") -> None:
        lines = _wrap(value, size, PAGE_WIDTH - RIGHT - x)
        leading = size * 1.45
        self._ensure_space(len(lines) * leading + 2)
        for line in lines:
            self.pages[-1].append(
                f"BT /{font} {size:.1f} Tf {color} rg 1 0 0 1 {x:.1f} {self.y:.1f} Tm {_pdf_text(line)} Tj ET"
            )
            self.y -= leading
        self.y -= 3

    def heading(self, value: str, *, title: bool = False) -> None:
        size = 20 if title else 12
        self._ensure_space(size * 2.2)
        if not title:
            self.y -= 7
        self.text(value, size=size, font="F2", color="0.10 0.16 0.22")
        if not title:
            line_y = self.y + 3
            self.pages[-1].append(f"0.78 0.81 0.84 RG 0.6 w {LEFT} {line_y:.1f} m {PAGE_WIDTH - RIGHT} {line_y:.1f} l S")

    def rule(self) -> None:
        self._ensure_space(16)
        self.y -= 4
        self.pages[-1].append(f"0.78 0.81 0.84 RG 0.6 w {LEFT} {self.y:.1f} m {PAGE_WIDTH - RIGHT} {self.y:.1f} l S")
        self.y -= 10

    def finish(self) -> list[list[str]]:
        for page_number, page in enumerate(self.pages, start=1):
            page.append(
                f"BT /F1 8 Tf 0.40 0.44 0.48 rg 1 0 0 1 {LEFT} 25 Tm {_pdf_text('ScopeGuard Local - Draft for discussion')} Tj ET"
            )
            page.append(
                f"BT /F1 8 Tf 0.40 0.44 0.48 rg 1 0 0 1 {PAGE_WIDTH - RIGHT - 42} 25 Tm {_pdf_text(f'Page {page_number}')} Tj ET"
            )
        return self.pages


def _markdown_pages(markdown: str) -> list[list[str]]:
    layout = _PdfLayout()
    for block in re.split(r"\n\s*\n", markdown.strip()):
        block = block.strip()
        if not block:
            continue
        if re.fullmatch(r"-{3,}", block):
            layout.rule()
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", block)
        if heading:
            layout.heading(_plain_text(heading.group(2)), title=len(heading.group(1)) == 1)
            continue
        lines = block.splitlines()
        if all(line.startswith("> ") for line in lines):
            for line in lines:
                layout.text(_plain_text(line[2:]), size=9, font="F3", x=LEFT + 12, color="0.27 0.31 0.34")
            continue
        if all(re.match(r"^[-*]\s+", line) for line in lines):
            for line in lines:
                item = re.sub(r"^[-*]\s+", "", line)
                layout.text("-  " + _plain_text(item), size=9.5, x=LEFT + 8)
            continue
        layout.text(" ".join(_plain_text(line) for line in lines), size=9.5)
    return layout.finish()


def render_proposal_pdf(markdown: str) -> bytes:
    pages = _markdown_pages(markdown)
    objects: list[bytes] = []

    def add_object(data: bytes) -> int:
        objects.append(data)
        return len(objects)

    catalog_id = add_object(b"")
    pages_id = add_object(b"")
    font_regular_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font_bold_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    font_italic_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")
    page_ids: list[int] = []

    for commands in pages:
        stream = zlib.compress(("\n".join(commands) + "\n").encode("ascii"))
        content_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" /Filter /FlateDecode >>\nstream\n"
            + stream + b"\nendstream"
        )
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH:.2f} {PAGE_HEIGHT:.2f}] "
            f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R /F3 {font_italic_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>".encode("ascii")
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii")
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")

    output = bytearray(b"%PDF-1.4\n%ScopeGuard\n")
    offsets = [0]
    for object_number, data in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_number} 0 obj\n".encode("ascii"))
        output.extend(data)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)
