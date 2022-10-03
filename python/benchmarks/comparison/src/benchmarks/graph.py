from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import statistics
import numpy as np
import scipy.stats as st

import matplotlib.pyplot as plt

from src.benchmarks.parser import BenchmarkResult, Field


class GraphSetting:
    def __init__(self,
                 x_field: Field,
                 y_field: Field,
                 line_field: Optional[Field],
                 title: Optional[str],
                 x_text: Optional[str],
                 y_text: str,
                 scatter: bool = False,
                 plot_confidence_interval: bool = False,
                 x_scale: str = "linear",
                 y_scale: str = "linear"):
        self.x_field = x_field
        self.y_field = y_field
        self.line_field = line_field

        self.title = title
        self.x_text = x_text
        self.y_text = y_text

        self.scatter = scatter

        self.plot_confidence_interval = plot_confidence_interval

        self.x_scale = x_scale
        self.y_scale = y_scale


class GraphSettings:
    def __init__(self, settings: List[GraphSetting], sync_x: bool):
        self.settings = settings
        self.sync_x = sync_x


def get_percentage_solved(datas: List[BenchmarkResult],
                          group_by: Field) -> List[Tuple[Any, float]]:
    solved_by_field_value: Dict[Any, (int, int)] = defaultdict(lambda: (0, 0))

    for data in datas:
        for orig_data in data.orig_results:
            field_value = orig_data.get_field(group_by)

            if field_value is None:
                print(
                    f"Trying to get % of empty field {group_by} for data {orig_data}, skipping"
                )
                continue

            current_value = solved_by_field_value[field_value]

            if not orig_data.has_solved():
                solved_by_field_value[field_value] = (current_value[0],
                                                      current_value[1] + 1)
            else:
                solved_by_field_value[field_value] = (current_value[0] + 1,
                                                      current_value[1])

    return [(k, 100 * (solved / (solved + not_solved)))
            for k, (solved, not_solved) in solved_by_field_value.items()]


prev_id = 0


def plot_data(datas: List[BenchmarkResult], graph_settings: GraphSettings,
              out_path: Path):
    global prev_id
    plt.figure(prev_id)
    prev_id += 1

    plt.style.use("seaborn-whitegrid")

    plt.rcParams["figure.figsize"] = (7, 5)
    plt.rcParams["font.family"] = "CMU Serif"
    plt.rcParams["font.size"] = 13
    plt.rcParams["axes.unicode_minus"] = False
    plt.margins(0, 0)

    fig, graphs = plt.subplots(len(graph_settings.settings),
                               1,
                               sharex=graph_settings.sync_x)

    if len(graph_settings.settings) == 1:
        graphs = [graphs]

    for graph, settings in zip(graphs, graph_settings.settings):
        grouped_by_line: Dict[Any, List[BenchmarkResult]] = defaultdict(list)
        for data in datas:
            if settings.line_field is None:
                grouped_by_line[0].append(data)
            else:
                grouped_by_line[data.get_field(
                    settings.line_field)].append(data)

        # solve_ratio = list(map(lambda vs: f"{len(list(filter(lambda b: b.has_solved(), vs)))} / {len(vs)}", grouped_by_line.values()))
        # print(solve_ratio)

        if settings.title is not None:
            graph.set_title(settings.title)

        graph.set_ylabel(settings.y_text)

        if settings.x_text is not None:
            graph.set_xlabel(settings.x_text)

        graph.set_yscale(settings.y_scale)
        graph.set_xscale(settings.x_scale)

        for line_value, samples in grouped_by_line.items():
            if settings.y_field == Field.PERCENTAGE_SOLVED:
                combined = get_percentage_solved(samples, settings.x_field)
            else:
                solved_samples = list(filter(lambda s: s.has_solved(),
                                             samples))

                # Average the results based on the x axis (e.g. nr of agents)
                # in the y axis if we are not scattering (then we want all results)
                if not settings.scatter:
                    grouped_by_x: Dict[
                        Any, List[BenchmarkResult]] = defaultdict(list)
                    for sample in solved_samples:
                        grouped_by_x[sample.get_field(
                            settings.x_field)].append(sample)

                    items = list(grouped_by_x.items())
                    xs = list(map(lambda i: i[0], items))

                    ys = [[y.get_field(settings.y_field) for y in ys[1]]
                          for ys in items]
                    confidence_intervals = [
                        st.t.interval(
                            0.95, len(y) - 1, loc=np.mean(y), scale=st.sem(y))
                        if len(y) > 1 else None for y in ys
                    ]
                    ys = [statistics.mean(y) for y in ys]
                    combined = zip(xs, ys, confidence_intervals)
                else:
                    xs = list(
                        map(lambda s: s.get_field(settings.x_field),
                            solved_samples))
                    ys = list(
                        map(lambda s: s.get_field(settings.y_field),
                            solved_samples))
                    combined = zip(xs, ys)

            combined = sorted(combined, key=lambda c: c[0])

            xs = list(map(lambda c: c[0], combined))
            ys = list(map(lambda c: c[1], combined))

            label = None if settings.line_field is None else line_value
            if settings.scatter:
                graph.scatter(xs, ys, 1, label=label)
            else:
                p = graph.plot(xs, ys, label=label)

                if settings.plot_confidence_interval:
                    confidence_intervals = list(map(lambda c: c[2], combined))
                    indices_to_plot = [
                        i for i, v in enumerate(confidence_intervals)
                        if v is not None
                    ]
                    low = [confidence_intervals[i][0] for i in indices_to_plot]
                    high = [
                        confidence_intervals[i][1] for i in indices_to_plot
                    ]
                    graph.fill_between([xs[i] for i in indices_to_plot],
                                       low,
                                       high,
                                       color=p[0].get_color(),
                                       alpha=0.5)

    plt.tight_layout(pad=1, h_pad=2.5)

    legend = plt.legend()
    for legend_handle in legend.legendHandles:
        legend_handle._sizes = [30]

    plt.savefig(out_path, format='pdf')
    plt.show()
