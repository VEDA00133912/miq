import textwrap
import unicodedata
from itertools import groupby
from PIL import ImageFont
from pilmoji import Pilmoji

east_asian_widths = {
    'W': 2,   # Wide
    'F': 2,   # Full-width (wide)
    'Na': 1,  # Narrow
    'H': 1,   # Half-width (narrow)
    'N': 1,   # Neutral (not East Asian, treated as narrow)
    'A': 1    # Ambiguous (usually treated as narrow here)
}

def column_width(text):
    """
    Calculate the display width of a string based on East Asian Width properties.
    """
    combining_correction = sum([-1 for c in text if unicodedata.combining(c)])
    width = sum([east_asian_widths[unicodedata.east_asian_width(c)] for c in text])
    return width + combining_correction

class TextWrapper(textwrap.TextWrapper):
    def _wrap_chunks(self, chunks):
        lines = []

        chunks.reverse()

        while chunks:
            cur_line = []
            cur_len = 0

            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            width = self.width - column_width(indent)

            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = column_width(chunks[-1])

                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l
                else:
                    break

            if chunks and column_width(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                del cur_line[-1]

            if cur_line:
                lines.append(indent + ''.join(cur_line))

        return lines

    def _break_word(self, word, space_left):
        total = 0
        for i, c in enumerate(word):
            total += column_width(c)
            if total > space_left:
                return word[:i - 1], word[i - 1:]
        return word, ''

    def _split(self, text):
        split = lambda t: textwrap.TextWrapper._split(self, t)
        chunks = []
        for chunk in split(text):
            for w, g in groupby(chunk, column_width):
                if w == 1:
                    chunks.extend(split(''.join(g)))
                else:
                    chunks.extend(list(g))
        return chunks

    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        space_left = max(width - cur_len, 1)
        if self.break_long_words:
            l, r = self._break_word(reversed_chunks[-1], space_left)
            cur_line.append(l)
            reversed_chunks[-1] = r
        elif not cur_line:
            cur_line.append(reversed_chunks.pop())

def fw_wrap(text, width=50):
    w = TextWrapper(width=width)
    return w.wrap(text)

def drawText(im, ofs, string, font="fonts/MPLUSRounded1c-Regular.ttf", size=16, color=(0, 0, 0, 255),
             split_len=None, padding=4, disable_dot_wrap=False, max_height=None):
    """
    Draws text onto an image, adjusting font size and wrapping to ensure it fits within the specified area.
    """
    font_path = font
    font_size = size
    while font_size > 8:  
        fontObj = ImageFont.truetype(font_path, font_size)
        lines = fw_wrap(string, width=split_len or 50)
        line_heights = [fontObj.getsize(line)[1] + padding for line in lines]
        total_height = sum(line_heights)

        if max_height is None or total_height <= max_height:
            break

        font_size -= 2

    else:
        fontObj = ImageFont.truetype(font_path, font_size)
        lines = fw_wrap(string, width=split_len or 50)
        max_lines = max_height // (fontObj.getsize("A")[1] + padding)
        lines = lines[:max_lines] 
        if lines and len(lines) == max_lines:
            lines[-1] = lines[-1][:-3] + "..."  

    dy = 0
    draw_lines = []
    for line in lines:
        tsize = fontObj.getsize(line)
        x = int(ofs[0] - (tsize[0] / 2))
        draw_lines.append((x, ofs[1] + dy, line))
        dy += tsize[1] + padding

    adj_y = -30 * (len(draw_lines) - 1)
    for dl in draw_lines:
        with Pilmoji(im) as p:
            p.text((dl[0], adj_y + dl[1]), dl[2], font=fontObj, fill=color)

    return font_size
