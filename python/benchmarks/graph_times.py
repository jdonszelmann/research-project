import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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


def graph_results(*args, save=True, bounds=True, fill_between=False):
    plt.style.use('seaborn-whitegrid')

    plt.rcParams["figure.figsize"] = (7, 5)
    plt.rcParams['font.size'] = '14'
    plt.tight_layout(pad=0)
    plt.margins(0, 0)

    fig, (percentage, times) = plt.subplots(2, 1, sharex=True)

    plt.subplots_adjust(hspace=0.3)

    percentage.set_title("% solved out of 200 maps")
    if bounds:
        times.set_title("time to solution (10, 50 and 90th percentile)")
    else:
        times.set_title("mean time to solution")


    percentage.xaxis.set_major_locator(MaxNLocator(integer=True))
    percentage.set_ylabel("% solved")
    times.xaxis.set_major_locator(MaxNLocator(integer=True))

    times.set_xlabel("number of agents")
    times.set_ylabel("seconds")
    percentage.set_ylim(0, 105)

    save_location = args[-1]
    ppydata = []

    for plt_index, (fn, label) in enumerate(args[:-1]):
        with open(fn, "r") as f:
            percentagexdata = []
            percentageydata = []

            timesxdata = []
            times10pydata = []
            times50pydata = []
            times90pydata = []

            for l in [l.strip() for l in f.readlines() if l.strip() != ""]:
                before, after = l.split(":")
                after_list = eval(after)
                num_agents = int(before)

                fraction_solved = (len(after_list) - after_list.count(None)) / len(after_list)

                solved_times = [i for i in after_list if i is not None]

                if fraction_solved != 0:
                    percentagexdata.append(num_agents)
                    percentageydata.append(fraction_solved * 100)

                    if len(solved_times) != 0:
                        timesxdata.append(num_agents)
                        times10pydata.append(percentile(solved_times, 10))
                        times50pydata.append(percentile(solved_times, 50))
                        times90pydata.append(percentile(solved_times, 90))

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
            # times.plot(
            #     "--",
            #     color=rgb_to_colour(*colors[plt_index]),
            #     linewidth=1,
            # )
            #
            # times.plot(
            #     timesxdata,
            #     times90pydata,
            #     "--",
            #     color=rgb_to_colour(*colors[plt_index]),
            #     linewidth=1,
            # )

    plt.legend()
    plt.show()
    if save:
        fig.savefig(save_location, bbox_inches="tight", pad_inches=0)