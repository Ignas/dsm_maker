import svgwrite
import base_drawer


class GraphDrawer(base_drawer.BaseDrawer):

    def init(self):
        self.square_size = max(2, 500 / self.size)
        self.offset = 20 * self.square_size
        self.width = self.size * self.square_size + self.offset
        self.height  = self.size * self.square_size + self.offset
        self.line_width = self.square_size / 10.0
        self.dwg = svgwrite.Drawing(self.filename, height=self.width, width=self.height, profile="tiny")

    def draw_grid(self):
        for n in range(self.offset, self.width + 1, self.square_size):
            self.dwg.add(self.dwg.line((self.offset, n),
                                       (self.width, n),
                                       stroke_width=self.line_width,
                                       stroke=svgwrite.rgb(10, 10, 16, '%')))
            self.dwg.add(self.dwg.line((n, self.offset),
                                       (n, self.height),
                                       stroke_width=self.line_width,
                                       stroke=svgwrite.rgb(10, 10, 16, '%')))

    def draw_square(self, x, node_x, y, node_y):
        rect = self.dwg.rect(insert=(self.offset + x * self.square_size,
                                     self.offset + y * self.square_size),
                             size=(self.square_size, self.square_size),
                             fill='black',
                             stroke=svgwrite.rgb(10, 10, 16, '%'),
                             stroke_width=self.line_width)
        title = "%s -> %s" % (node_y.replace('"', ''),
                              node_x.replace('"', ''))
        rect.set_desc(title)
        self.dwg.add(rect)

    def add_vertical_labels(self):
        for y, node_y in enumerate(self.nodes, 1):
            self.dwg.add(self.dwg.text(node_y.replace('"', ''),
                                       insert=(0, self.square_size * y + self.offset),
                                       fill='blue',
                                       font_size=self.square_size))

    def add_horizontal_labels(self):
        for x, node_x in enumerate(self.nodes):
            center = self.square_size * x + self.offset, 0
            self.dwg.add(self.dwg.text(node_x.replace('"', ''),
                                       transform='rotate(90  %f,%f)' % center,
                                       insert=center,
                                       fill='blue',
                                       font_size=self.square_size))

    def close(self):
        self.dwg.save()
