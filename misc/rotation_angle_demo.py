from scipy.spatial.transform import Rotation as R
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

plt.ioff()


def plot_rotated_axes(ax, r, name=None, offset=(0, 0, 0), scale=1, linestyle="-"):
    colors = ("#FF6666", "#005533", "#1199EE")  # Colorblind-safe RGB
    loc = np.array([offset, offset])

    for i, (axis, c) in enumerate(zip((ax.xaxis, ax.yaxis, ax.zaxis),
                                      colors)):
        if i == 2:
            scale=.5
        axlabel = axis.axis_name
        axis.set_label_text(axlabel)
        axis.label.set_color(c)
        axis.line.set_color(c)
        axis.set_tick_params(colors=c)

        line = np.zeros((2, 3))
        line[1, i] = scale
        line_rot = r.apply(line)
        line_plot = line_rot + loc
        ax.plot(line_plot[:, 0], line_plot[:, 1], line_plot[:, 2], c, linestyle=linestyle)

        # if i in [0, 1]:
        #     line[0, 1-i] = scale
        #     line[0, i] = scale
        #     line_rot = r.apply(line)
        #     line_plot = line_rot + loc
        #     ax.plot(line_plot[:, 0], line_plot[:, 1], line_plot[:, 2], colors[1-i])

        text_loc = line[1]*1.2
        text_loc_rot = r.apply(text_loc)
        text_plot = text_loc_rot + loc[0]
        ax.text(*text_plot, axlabel.upper(), color=c,
                va="center", ha="center")
    ax.text(*offset, name, color="k", va="center", ha="center",
            bbox={"fc": "w", "alpha": 0.8, "boxstyle": "circle"})


r0 = R.identity()
#rzyx1 = R.from_euler("ZYX", [90, 0, 0], degrees=True)  # intrinsic
rzyx2 = R.from_euler("ZYX", [0, 45, 0], degrees=True)  # intrinsic
rzyx3 = R.from_euler("ZYX", [0, 45, 45], degrees=True)  # intrinsic

#rzxy1 = R.from_euler("ZXY", [90, 0, 0], degrees=True)  # intrinsic
rzxy2 = R.from_euler("ZYX", [0, 0, 0], degrees=True)  # intrinsic
rzxy3 = R.from_euler("ZYX", [0, 0, 45], degrees=True)  # intrinsic

ax = plt.figure().add_subplot(projection="3d", proj_type="ortho")
plot_rotated_axes(ax, r0, name="r0", offset=(0, 0, 0))

plot_rotated_axes(ax, rzyx2, name="P", offset=(3, 0, 0))
plot_rotated_axes(ax, r0, name="", offset=(3, 0, 0), linestyle="--")

plot_rotated_axes(ax, rzyx3, name="R", offset=(6, 0, 0))
plot_rotated_axes(ax, rzyx2, name="", offset=(6, 0, 0), linestyle="--")


# plot_rotated_axes(ax, r0, name="r0", offset=(0, -3, 0))
# plot_rotated_axes(ax, rzxy2, name=" ", offset=(3, -3, 0))
# plot_rotated_axes(ax, rzxy3, name="R", offset=(6, -3, 0))
# plot_rotated_axes(ax, r0, name="", offset=(6, -3, 0), scale=2, linestyle="--")

ax.set(xlim=(-1.25, 8.25), ylim=(-2.25, 2.25), zlim=(-1.25, 1.25))
ax.set(xticks=range(-1, 9), yticks=range(-2, 3), zticks=range(-2, 2))
ax.set_aspect("equal", adjustable="box")
#ax.figure.set_size_inches(6, 5)

# ax.view_init(elev=10., azim=0)

#plt.tight_layout()

plt.show()
