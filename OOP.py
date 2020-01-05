"""
The OOP part of the program
Russian Central Bank's web-page parsing

"""

from tkinter import Frame, TOP, BOTH
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,\
    NavigationToolbar2Tk
from matplotlib.figure import Figure


class PlotWindow(Frame):
    """A MatPlotLib window"""

    def __init__(self, window):
        """Class constructor"""

        Frame.__init__(self, window)
        self.grid(row=3, columnspan=4)

    def unpack(self):
        """Delete window with MPL Figure from Tk window"""

        self.destroy()

    def add_mpl_figure(self, figure):
        """Add MatPlotLib Figure"""

        self.mpl_canvas = FigureCanvasTkAgg(figure, self)
        self.mpl_canvas.draw()

        self.toolbar = NavigationToolbar2Tk(self.mpl_canvas, self)
        self.toolbar.update()

        self.mpl_canvas.get_tk_widget().pack(side=TOP,
                                             fill=BOTH, expand=True)
        self.mpl_canvas._tkcanvas.pack(side=TOP,
                                       fill=BOTH, expand=True)


class MPLPlot(Figure):
    """A MatPlotLib figure"""

    def __init__(self):
        """Class constructor"""

        Figure.__init__(self, dpi=100)
        self.plot = self.add_subplot(111)

    def build_plot(self, plot_x, plot_y, label):
        """Add plot on a subplot"""

        self.plot.plot(plot_x, plot_y, label=label)

    def nice_plot(self, x_label=None, y_label=None):
        """Make plot look nice"""

        self.plot.grid(True)
        if x_label and y_label:
            self.plot.set_xlabel(x_label)
            self.plot.set_ylabel(y_label)
        self.plot.legend()
