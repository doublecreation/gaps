import matplotlib.pyplot as plt
import warnings
import matplotlib.cbook

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


class Plot(object):

    def __init__(self, image, title="Initial problem"):
        # Let image fill the figure
        fig = plt.figure(figsize=(9, 7), frameon=False)
        ax = plt.Axes(fig, [0., 0., 1., .9])
        ax.set_axis_off()
        fig.add_axes(ax)

        self._current_image = ax.imshow(image, aspect="auto", animated=True)
        self.show_fittest(image, title)

    def show_fittest(self, image, title):
        plt.suptitle(title, fontsize=20)
        self._current_image.set_data(image)
        plt.draw()

        # Give pyplot 0.05 to draw image
        plt.pause(0.05)
