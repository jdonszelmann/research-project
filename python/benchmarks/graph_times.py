import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

colors = [
    (204, 68, 82),
    (36, 97, 128),
    (128, 29, 39),
    (47, 152, 204),
    (17, 128, 42),
    (67, 204, 98),
    (57, 204, 174),
    (102, 82, 74),
    (128, 124, 23),
    (204, 111, 78),
]
background = (34, 39, 46)


def lighten(r, g, b, amount):
    return int(min(255, r + 255*amount)), int(min(255, g + 255*amount)), int(min(255, b + 255*amount))


def rgb_to_colour(r, g, b, transparency_fraction=None):
    if transparency_fraction is None:
        return f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}"
    else:
        return f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}{hex(int(transparency_fraction * 255))[2:]}"


def average(l: list) -> float:
    return sum(l) / len(l) if len(l) != 0 else -1


def percentile(l: list[float], perc: float) -> float:
    if len(l) == 0:
        return -1

    l.sort()
    index = len(l) * (perc/100)

    i = int(index)
    f = index - i

    v1 = l[i]
    v2 = l[i + 1] if i + 1 < len(l) else l[i]
    return v1 * f + v2 * (1 - f)


black = True

def graph_results(*args, under,
                  save=True,
                  bounds=True,
                  fill_between=False,
                  graph_times=False,
                  graph_percentage=True,
                  legend=True,
                  ):
    plt.style.use('seaborn-whitegrid')

    if black:
        plt.rcParams['axes.facecolor'] = rgb_to_colour(*background)
        plt.rcParams['axes.edgecolor'] = '#FFFFFF'
        plt.rcParams['axes.labelcolor'] = '#FFFFFF'
        plt.rcParams['figure.facecolor'] = rgb_to_colour(*background)
        plt.rcParams['xtick.color'] = '#FFFFFF'
        plt.rcParams['ytick.color'] = '#FFFFFF'
        plt.grid(color='#FFFFFF', linestyle='-', linewidth=0.7)
        plt.rcParams['font.size'] = '20'
        plt.rcParams['legend.frameon'] = 'True'


    if graph_times and graph_percentage:
        if black:
            plt.rcParams["figure.figsize"] = (9, 5)
        else:
            plt.rcParams["figure.figsize"] = (7, 5)

        fig, (percentage, times) = plt.subplots(2, 1, sharex=True)
    elif graph_times or graph_percentage:
        if black:
            plt.rcParams["figure.figsize"] = (8, 4)
        else:
            plt.rcParams["figure.figsize"] = (7, 3)

        fig, (subplt) = plt.subplots(1, 1)
        if graph_percentage:
            percentage = subplt
        else:
            times = subplt
    else:
        assert False, "should graph something"

    if not black:
        plt.rcParams['font.size'] = '14'


    if graph_percentage and graph_times:
        if not black:
            plt.subplots_adjust(hspace=0.3)
            plt.tight_layout(pad=0)
            plt.margins(0, 0)

    if graph_percentage:
        percentage.set_title("% solved out of 200 maps")
    if graph_times:
        if bounds:
            times.set_title("time to solution of solved maps")
        else:
            times.set_title("mean time to solution of solved maps")

    if graph_percentage:
        percentage.xaxis.set_major_locator(MaxNLocator(integer=True))
        percentage.set_ylabel("% solved")
        if not graph_times:
            percentage.set_xlabel(under)

    if graph_times:
        times.xaxis.set_major_locator(MaxNLocator(integer=True))
        times.set_xlabel("number of agents")
        times.set_ylabel("seconds")

    if graph_percentage:
        percentage.set_ylim(0, 105)

    save_location = args[-1]
    ppydata = []

    plt.tight_layout()

    longest = 0

    for plt_index, (fn, label) in enumerate(args[:-1]):
        with open(fn, "r") as f:
            if graph_percentage:
                percentagexdata = []
                percentageydata = []

            if graph_times:
                timesxdata = []
                times10pydata = []
                times50pydata = []
                times90pydata = []

            lines = f.readlines()
            longest = int(lines[-1].split(":")[0])
            for l in [l.strip() for l in lines if l.strip() != ""]:
                before, after = l.split(":")
                after_list = eval(after)
                num_agents = int(before)

                fraction_solved = (len(after_list) - after_list.count(None)) / len(after_list)

                solved_times = [i for i in after_list if i is not None]

                if fraction_solved != 0:
                    if graph_percentage:
                        percentagexdata.append(num_agents)
                        percentageydata.append(fraction_solved * 100)

                    if graph_times and len(solved_times) != 0:
                        timesxdata.append(num_agents)
                        times10pydata.append(percentile(solved_times, 10))
                        times50pydata.append(percentile(solved_times, 50))
                        times90pydata.append(percentile(solved_times, 90))
                elif len(percentageydata) > 0 and percentageydata[-1] != 0 and graph_percentage:
                    percentagexdata.append(num_agents)
                    percentageydata.append(0)

            if graph_percentage:
                percentage.plot(
                    percentagexdata,
                    percentageydata,
                    color=rgb_to_colour(*colors[plt_index]),
                    label=label,
                    linewidth=3,
                )

                if fill_between:
                    if not ppydata:
                        percentage.fill_between(
                            percentagexdata,
                            0,
                            percentageydata,
                            color=rgb_to_colour(*lighten(*colors[plt_index], 0.2), transparency_fraction=50/100)
                        )
                    else:
                        while len(ppydata) < len(percentageydata):
                            ppydata.append(0)
                        percentage.fill_between(
                            percentagexdata,
                            ppydata,
                            percentageydata,
                            color=rgb_to_colour(*lighten(*colors[plt_index], 0.2), transparency_fraction=50 / 100)
                        )

                    ppydata = percentageydata

            if graph_times:
                times.plot(
                    timesxdata,
                    times50pydata,
                    color=rgb_to_colour(*colors[plt_index]),
                    label=label,
                    linewidth=3,
                )

                if bounds:
                    times.fill_between(
                        timesxdata,
                        times10pydata,
                        times90pydata,
                        color=rgb_to_colour(*lighten(*colors[plt_index], 0.2), transparency_fraction=50/100)
                    )

    if graph_percentage:
        percentage.set_xlim(0, longest)
    else:
        times.set_xlim(0, longest + 1)

    if legend:
        plt.legend()
    if black:
        plt.legend(facecolor=rgb_to_colour(*background), labelcolor='w', prop={'size': 13})
    plt.show()
    if save:
        if black:
            # fig.savefig(f"{save_location}.black.eps", bbox_inches="tight", pad_inches=0, format='eps')
            fig.savefig(f"{save_location}.black.png", bbox_inches="tight", pad_inches=0, format='png')
        else:
            fig.savefig(f"{save_location}.eps", bbox_inches="tight", pad_inches=0, format='eps')
            fig.savefig(f"{save_location}.png", bbox_inches="tight", pad_inches=0, format='png')
