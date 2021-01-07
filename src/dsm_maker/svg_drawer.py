import drawSvg as draw
from .base_drawer import BaseDrawer


class GraphDrawer(BaseDrawer):

    def init(self):
        self.square_size = max(2, min(500 / self.size, 10))
        self.offset = 20 * self.square_size
        self.width = self.size * self.square_size + self.offset
        self.height  = self.size * self.square_size + self.offset
        self.line_width = self.square_size / 10.0
        self.dwg = draw.Drawing(self.width, self.height, profile="tiny", origin=(0, 0))
        background = draw.Rectangle(0, 0, self.width, self.height, fill='white')
        self.dwg.append(background)

    def draw_grid(self):
        for i, n in enumerate(range(self.offset, self.width, self.square_size)):
            self._draw_square(i, i, self.nodes[i], fill='gray')
            self.dwg.append(draw.Line(self.offset, n - self.offset,
                                      self.width, n - self.offset,
                                      stroke_width=self.line_width,
                                      stroke='#909096'))
            self.dwg.append(draw.Line(n, self.offset - self.offset,
                                      n, self.height - self.offset,
                                      stroke_width=self.line_width,
                                      stroke='#909096'))

    def _draw_square(self, x, y, title=None, fill='black'):
        rect = draw.Rectangle(
            self.offset + x * self.square_size,
            self.height - (y + 1) * self.square_size - self.offset,
            self.square_size, self.square_size,
            fill=fill,
            stroke='#909096',
            stroke_width=self.line_width)
        if title is not None:
            rect.appendTitle(title)
        self.dwg.append(rect)

    def draw_square(self, x, node_x, y, node_y):
        if (node_x, node_y) not in self.edges:
            title = "%s -> %s" % (node_y.replace('"', ''),
                                  node_x.replace('"', ''))
            self._draw_square(x, y, title, fill='darkblue')
            if not self.one_way:
                title = "%s <- %s" % (node_y.replace('"', ''),
                                      node_x.replace('"', ''))
                self._draw_square(y, x, title, fill='darkgreen')
        else:
            title = "%s <-> %s" % (node_y.replace('"', ''),
                                   node_x.replace('"', ''))
            self._draw_square(x, y, title, fill='red')

    def _format_label(self, label, length=40):
        node_text = label.replace('"', '')
        if len(node_text) > length:
            node_text = node_text[:length - 3] + "..."
        return node_text

    def add_vertical_labels(self):
        for y, node_y in enumerate(self.nodes, 1):
            self.dwg.append(draw.Text(self._format_label(node_y),
                                      self.square_size,
                                      0, self.height - self.square_size * y - self.offset,
                                      fill='blue'))

    def add_horizontal_labels(self):
        for x, node_x in enumerate(self.nodes):
            center = self.square_size * x + self.offset, self.height
            rotation_center = center[0], -center[1]
            self.dwg.append(draw.Text(self._format_label(node_x),
                                      self.square_size,
                                      center[0], center[1],
                                      transform='rotate(90 %f,%f)' % rotation_center,
                                      fill='blue'))

    def close(self):
        self.dwg.saveSvg(self.filename)
