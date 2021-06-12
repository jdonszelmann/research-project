from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from python.benchmarks.graph_times import rgb_to_colour, colors, average


def graph_results(*args, save=True):
    plt.style.use('seaborn-whitegrid')

    plt.rcParams["figure.figsize"] = (7, 4)
    plt.rcParams['font.size'] = '14'
    plt.tight_layout(pad=0)
    plt.margins(0, 0)

    fig, expansions = plt.subplots(1, 1)

    expansions.set_title("average expansion size")

    expansions.xaxis.set_major_locator(MaxNLocator(integer=True))
    expansions.set_ylabel("average expansion size")
    expansions.set_yscale('log')
    expansions.set_ylim(1, 10**5)

    expansions.set_xlabel("number of agents")

    save_location = args[-1]

    for plt_index, (fn, label) in enumerate(args[:-1]):
        with open(fn, "r") as f:
            expansionsxdata = []
            expansionsydata = []

            for l in [l.strip() for l in f.readlines() if l.strip() != ""]:
                before, after = l.split(":")
                after_list: list[Optional[list[int]]] = eval(after)
                num_agents = int(before)

                fraction_solved = (len(after_list) - after_list.count(None)) / len(after_list)

                solved_averages = [average(i) for i in after_list if i is not None]


                if fraction_solved != 0:
                    expansionsxdata.append(num_agents)
                    expansionsydata.append(average(solved_averages))


            expansions.plot(
                expansionsxdata,
                expansionsydata,
                color=rgb_to_colour(*colors[plt_index]),
                label=label,
                linewidth=3,
            )


    plt.legend()
    plt.show()
    if save:
        fig.savefig(f"{save_location}.eps", bbox_inches="tight", pad_inches=0, format='eps')
        fig.savefig(f"{save_location}.png", bbox_inches="tight", pad_inches=0, format='png')
