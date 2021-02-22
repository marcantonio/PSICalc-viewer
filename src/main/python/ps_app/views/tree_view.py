from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QAction
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.legend_handler import HandlerPatch
from ps_app.views.csv_view import ClusterData

import csv
import numpy as np
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches


class HandlerEllipse(HandlerPatch):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        center = 0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent
        p = mpatches.Ellipse(xy=center, width=width + xdescent,
                             height=height + ydescent)
        self.update_prop(p, orig_handle, legend)
        p.set_transform(trans)
        return [p]


class ApplicationWindow(QtWidgets.QMainWindow):
    """Tree Window View"""
    def __init__(self, path, csv_logo):
        super().__init__()
        self.path = path
        if type(self.path) is dict:
             self.lines = [[str(k), str(v[0]), str(v[1])] for k, v in self.path.items()]
        else:
            with open(self.path) as f:
                self.lines = list(csv.reader(f))
            self.lines = self.lines[1:] # ignores header

        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        self.draw_tree(0)

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.tabs = QtWidgets.QTabWidget()
        layout = QtWidgets.QVBoxLayout(self._main)

        self.table = ClusterData(self.path)
        self.tabs.addTab(self.canvas, "Tree View")
        self.tabs.addTab(self.table, "Cluster Data")
        layout.addWidget(self.tabs)
        self.nav_bar = self.addToolBar(NavigationToolbar(self.canvas, self))

        csv_img = csv_logo
        save_file_action = QAction(QtGui.QIcon(csv_img), 'Save CSV', self)
        save_file_action.triggered.connect(self.table.save_sheet)
        self.toolbar = self.addToolBar('Data')
        self.toolbar.addAction(save_file_action)

        self.primeSpinBox = QtWidgets.QDoubleSpinBox()
        self.primeSpinBox.setRange(0.00, 1.00)
        self.primeSpinBox.setSingleStep(0.01)
        self.primeSpinBox.setValue(0.00)
        self.primeSpinBox.setGeometry(QtCore.QRect(90, 320, 42, 22))
        self.primeSpinBox.setObjectName("primeSpinBox")
        self.primeSpinBox.valueChanged.connect(self.primeSpinBox_handler)
        self.toolbar.addWidget(self.primeSpinBox)

    def primeSpinBox_handler(self):
        prime_cluster_val = round(self.primeSpinBox.value(), 3)
        self.draw_tree(prime_cluster_val)
        self.canvas.draw()

    # reformats sequence of numbers with hyphens
    @staticmethod
    def get_line_numbers_concat(line_nums):
        seq = []
        final = []
        last = 0

        for index, val in enumerate(line_nums):

            if last + 1 == val or index == 0:
                seq.append(val)
                last = val
            else:
                if len(seq) > 1:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq) - 1]))
                else:
                    final.append(str(seq[0]))
                seq = list()
                seq.append(val)
                last = val

            if index == len(line_nums) - 1:
                if len(seq) > 1:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq) - 1]))
                else:
                    final.append(str(seq[0]))

        final_str = ', '.join(map(str, final))
        final_str = ''.join(('(', final_str, ')'))
        return final_str

    def draw_tree(self, cutoff):
        """
        This is the main tree drawing method
        """
        prime_cluster = .33
        font_size = 6
        # TODO: Refactor this area
        data = self.lines

        # TODO fix this using split or other method
        data = [e for e in data if len(e) != 0]
        values = [entry for entry in data if float(entry[1]) >= cutoff]  # modified variable
        tree_list = [(entry[0].strip('()'), entry[1]) for entry in values]
        tree_list = [(i[0].split(','), i[1]) for i in tree_list]
        tree_list = [(list(map(int, i[0])), float(i[1])) for i in tree_list]
        max_len = max([len(s[0]) for s in tree_list])

        # Create graph and set default attributes for nodes
        G = nx.Graph()
        for i in G.nodes:
            G.nodes[i]['parent'] = False
            G.nodes[i]['color'] = None
            G.nodes[i]['sr_mode'] = None
            G.nodes[i]['prime_cluster'] = False

        n_order = 1
        while n_order < max_len:

            n_order += 1
            next_set = [(s[0], s[1]) for s in tree_list if len(s[0]) == n_order]
            next_set = [(tuple(t[0]), t[1]) for t in next_set]
            next_set = sorted(list(set(next_set)))

            for i in next_set:
                G.add_node(i[0], color=None, parent=False, sr_mode=i[1], prime_cluster=False)

            # Draw edges between nodes
            for i in G.nodes:
                if G.nodes[i]['sr_mode'] >= prime_cluster:  # set prime cluster value
                    G.nodes[i]['prime_cluster'] = True
                    G.nodes[i]['color'] = 'purple'
                else:
                    G.nodes[i]['color'] = '#00000000'  # everything else is a clear color

                # Checks for supersets
                if G.nodes[i]['parent'] is not True:
                    for j in G.nodes:
                        if i != j and set(i).issubset(set(j)):
                            G.add_edge(i, j)
                            G.nodes[i]['parent'] = True

        for v, w in G.edges:
            if G.nodes[v]["parent"] is True:
                G.edges[v, w]["subset"] = True
            else:
                G.edges[v, w]["subset"] = False

        # -------Node Positioning Calculator----------
        y_pos = 1000
        n_order = 1
        ytick_list = list()
        xtick_list = list()
        xtick_labels = list()
        ytick_labels = list()
        max_node_len = max([len(s) for s in G.nodes])

        while n_order < max_node_len:
            n_order += 1
            next_set = [s for s in G.nodes if len(s) == n_order]
            # Set x tick labels to identify pairwise cluster locations
            if n_order == 2:
                xtick_labels = [(next_set.index(x) + 1) for x in next_set]
            if len(next_set) != 0:
                # Set Y axis
                ytick_labels.append(str(n_order))
                y_pos -= 100
                ytick_list.append([y_pos, n_order])

        pos = graphviz_layout(G, prog='dot')

        for i, j in ytick_list:
            for each, coord in pos.items():
                if len(each) == j:
                    pos[each] = (coord[0], (i + 3))
        x_label = 1
        for each, coord in pos.items():
            if len(each) == 2:
                xtick_list.append(coord[0])
                xtick_labels.append(x_label)
                x_label += 1

        pos = {self.get_line_numbers_concat(k): v for k, v in pos.items()}
        # noinspection PyTypeChecker
        G = nx.relabel_nodes(G, lambda x: self.get_line_numbers_concat(x))

        """
        All of the custom graph drawing 
        """
        self.fig.clear()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_ylabel('Order \n (n)', rotation=-0, fontsize=8, weight='bold')
        self.ax.yaxis.set_label_coords(0, 1.02)
        self.ax.set_xlabel('Site location in the Multiple Sequence Alignment', fontsize=8, weight='bold')
        self.ax.xaxis.set_label_coords(0.5, 1.12)
        self.ax.format_coord = lambda x, y: ""
        node_colors = [G.nodes[i]['color'] for i in G.nodes]

        # Draw nodes
        rx, ry = .6, .25
        area = rx * ry * np.pi
        theta = np.arange(0, 2 * np.pi + 0.01, 0.1)
        verts = np.column_stack([rx / area * np.cos(theta), ry / area * np.sin(theta)])
        nx.draw_networkx_nodes(G, pos=pos, ax=self.ax, node_color='#00000000', edgecolors=node_colors, node_shape=verts,
                               node_size=1000)
        nx.draw_networkx_labels(G, pos=pos, ax=self.ax, font_color='k', font_weight='bold', font_size=font_size)

        # Draw edges
        edges_p = [e for e in G.edges if G.edges[e]["subset"]]
        edges_s = [e for e in G.edges if not G.edges[e]["subset"]]
        nx.draw_networkx_edges(G, pos=pos, ax=self.ax, style='solid', edgelist=edges_p, edge_color='k', alpha=.5)
        nx.draw_networkx_edges(G, pos=pos, ax=self.ax, style='dashed', edge_color='#DB7093', edgelist=edges_s, width=1.5,
                               alpha=.5)

        plt.grid(True, axis='y')

        y_ticks = [k for k, v in ytick_list]
        self.ax.yaxis.set_ticks(y_ticks)
        self.ax.yaxis.set_ticklabels(ytick_labels, visible=True)
        self.ax.xaxis.set_ticks(xtick_list)
        self.ax.xaxis.set_ticklabels(xtick_labels, visible=True)
        c = mpatches.Circle((0.5, 0.5), 0.25, facecolor="white",
                            edgecolor="purple", linewidth=3)
        self.ax.legend([c], ["High Sr Mode Cluster"], loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=2, handler_map={mpatches.Circle: HandlerEllipse()})

        for i, k in enumerate(self.ax.xaxis.get_ticklabels()):
            label = self.ax.xaxis.get_ticklabels()[i]
            label.set_bbox(dict(facecolor='white', edgecolor='black'))
        self.ax.tick_params(labelbottom=False, labeltop=True, labelleft=True, labelright=False, bottom=False,
                       top=False, left=False, right=False)