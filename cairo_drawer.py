import cairo
import math
import base_drawer

class GraphDrawer(base_drawer.BaseDrawer):

    def init(self):
        fo = file(self.filename, 'w')
        WIDTH, HEIGHT  = 1200, 1200
        self.surface = cairo.SVGSurface(fo, WIDTH, HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(WIDTH/1.0, HEIGHT/1.0) # Normalizing the canvas

    def draw_grid(self):
        for n in range(self.size):
            self.ctx.move_to(n * self.square_size, 0)
            self.ctx.line_to(n * self.square_size, 1)

            self.ctx.move_to(0, n * self.square_size)
            self.ctx.line_to(1, n * self.square_size)

        self.ctx.set_source_rgb(0.3, 0.3, 0.3)
        self.ctx.set_line_width(0.0001)
        self.ctx.stroke()

    def draw_square(self, x, node_x, y, node_y):
        self.ctx.rectangle(x * self.square_size, y * self.square_size,
                           self.square_size, self.square_size)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.fill()

    def add_vertical_labels(self):
        for x, node_x in enumerate(self.nodes):
            self.ctx.set_source_rgb(0, 0, 1)
            self.ctx.set_font_size(self.square_size)
            self.ctx.move_to(0, (x + 1) * self.square_size)
            self.ctx.show_text(node_x.replace('"', ''))

    def add_horizontal_labels(self):
        self.ctx.save()
        self.ctx.translate(0.5, 0.5)
        self.ctx.rotate(math.pi / 2)
        self.ctx.translate(-0.5, -0.5)
        for x, node_x in enumerate(reversed(self.nodes)):
            if x < (len(self.nodes) - 11):
                self.ctx.set_source_rgb(0, 0, 1)
                self.ctx.set_font_size(self.square_size)
                self.ctx.move_to(0, (x + 1) * self.square_size)
                self.ctx.show_text(node_x.replace('"', ''))
        self.ctx.restore()

    def close(self):
        self.surface.finish()
