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


def rgb_to_colour(r, g, b):
    return f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}"


def average(l: list) -> float:
    return sum(l) / len(l)


def graph_results(*args):
    plt.style.use('seaborn-whitegrid')

    fig, (percentage, times) = plt.subplots(2, 1)
    plt.subplots_adjust(hspace=0.3)

    percentage.set_title("% solved out of 200 maps")
    times.set_title("average time to solution (of solved maps)")

    percentage.xaxis.set_major_locator(MaxNLocator(integer=True))
    times.xaxis.set_major_locator(MaxNLocator(integer=True))

    percentage.set_ylim(0, 105)

    for plt_index, (fn, label) in enumerate(args):
        with open(fn, "r") as f:
            percentagexdata = []
            percentageydata = []

            timesxdata = []
            timesydata = []

            for l in [l.strip() for l in f.readlines() if l.strip() != ""]:
                before, after = l.split(":")
                after_list = eval(after)
                num_agents = int(before)

                fraction_solved = (len(after_list) - after_list.count(None)) / len(after_list)

                solved_times = [i for i in after_list if i is not None]

                percentagexdata.append(num_agents)
                percentageydata.append(fraction_solved * 100)

                timesxdata.append(num_agents)
                timesydata.append(average(solved_times))


            percentage.plot(
                percentagexdata,
                percentageydata,
                color=rgb_to_colour(*colors[plt_index]),
                label=label,
                linewidth=3,
            )


            times.plot(
                timesxdata,
                timesydata,
                color=rgb_to_colour(*colors[plt_index]),
                label=label,
                linewidth=3,
            )

    plt.legend()
    plt.show()
