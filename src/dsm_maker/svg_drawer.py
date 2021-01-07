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
        for i, n in enumerate(range(self.offset, self.width + 1, self.square_size)):
            self._draw_square(i, i, self.nodes[i - 1], fill='gray')
            self.dwg.append(draw.Line(self.offset, n,
                                      self.width, n,
                                      stroke_width=self.line_width,
                                      stroke='#F0F0F6'))
            self.dwg.append(draw.Line(n, self.offset,
                                      n, self.height,
                                      stroke_width=self.line_width,
                                      stroke='#F0F016'))

    def _draw_square(self, x, y, title=None, fill='black'):
        rect = draw.Rectangle(
            self.offset + x * self.square_size,
            self.offset + y * self.square_size,
            self.square_size, self.square_size,
            fill=fill,
            stroke='#000016',
            stroke_width=self.line_width)
        if title is not None:
            rect.appendTitle(title)
        self.dwg.append(rect)

    def draw_square(self, x, node_x, y, node_y):
        if (node_x, node_y) not in self.edges:
            title = "%s -> %s" % (node_y.replace('"', ''),
                                  node_x.replace('"', ''))
            self._draw_square(x, y, title, fill='darkblue')
            # title = "%s <- %s" % (node_y.replace('"', ''),
            #                       node_x.replace('"', ''))
            # self._draw_square(y, x, title, fill='darkgreen')
        else:
            title = "%s <-> %s" % (node_y.replace('"', ''),
                                   node_x.replace('"', ''))
            self._draw_square(x, y, title, fill='red')

    def add_vertical_labels(self):
        for y, node_y in enumerate(self.nodes, 1):
            self.dwg.append(draw.Text(node_y.replace('"', ''),
                                      self.square_size,
                                      0, self.square_size * y + self.offset - self.square_size,
                                      fill='blue'))

    def add_horizontal_labels(self):
        for x, node_x in enumerate(self.nodes):
            center = self.square_size * x + self.offset, self.offset
            rotation_center = center[0], -center[1]
            self.dwg.append(draw.Text(node_x.replace('"', ''),
                                      self.square_size,
                                      center[0], center[1],
                                      transform='rotate(90 %f,%f)' % rotation_center,
                                      fill='blue'))

    def close(self):
        self.dwg.saveSvg(self.filename)
