__all__ = ['draw3d_plotly_networkx']
import plotly
import plotly.plotly as py
from plotly.graph_objs import Line, Scatter3d, Mesh3d, \
    XAxis, YAxis, ZAxis, \
    Scene, Annotation, Annotations, \
    Marker, Font, Margin, \
    Layout, Figure, Data
import networkx as nx
import numpy as np

# import plotly.plotly as py
# plotly.offline.init_notebook_mode()
# colorscale options
# 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
# Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'

def draw3d_plotly_networkx(graph=None,
                           perc_threshold=None,
                           positions_array=None,
                           positions_dict=None,
                           plot_title='',
                           plot_description='',
                           colorscale='Set3'):
    if graph is None:
        graph = nx.random_geometric_graph(200, 0.05)

    marker_size = 7
    marker_edge_width = 2
    link_width = 2
    colorbar_title = 'Node Connections'
    hover_description = '# connections: '

    position_attr = ['x', 'y', 'z']
    if positions_array is not None:
        for node in graph.nodes():
            for ix, attr in enumerate(position_attr):
                graph.node[node][attr] = positions_array[node][ix]
    elif positions_dict is not None:
        for node in graph.nodes():
            for attr in position_attr:
                graph.node[node][attr] = positions_array[node][attr]

    for attr in position_attr:
        if not nx.get_node_attributes(graph, attr):
            raise ValueError('Position attribute {} missing. '
                             'Add it to graph or supply with one of the position inputs'.format(attr))

    if perc_threshold is not None:
        eval_distr = np.array(list(nx.get_edge_attributes(graph, 'weight').values()))
        edge_threshold = np.percentile(eval_distr, perc_threshold)

    edge_trace = Scatter3d(
            x=[],
            y=[],
            z=[],
            mode='lines',
            line=Line(width=marker_edge_width, color='#888'),
            hoverinfo='none',
            )

    def get_position(node):
        "Helper to retun the x, y, z coords of a node"
        return node['x'], node['y'], node['z']

    for src, dest in graph.edges():
        # adding only the strongest edges
        if perc_threshold is None or graph.get_edge_data(src, dest)['weight'] > edge_threshold:
            x0, y0, z0 = get_position(graph.node[src ])  # ['position']
            x1, y1, z1 = get_position(graph.node[dest])  # ['position']
            edge_trace['x'].extend([x0, x1, None])
            edge_trace['y'].extend([y0, y1, None])
            edge_trace['z'].extend([z0, z1, None])


    # empty lists here will be appended with data to be plotted
    node_trace = Scatter3d(
            x=[], y=[], z=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=Marker(
                    symbol='dot',
                    showscale=True,
                    colorscale=colorscale,
                    reversescale=True,
                    color=[],
                    size=marker_size,
                    colorbar=dict(
                            thickness=15,
                            title=colorbar_title,
                            xanchor='left',
                            titleside='right'
                            ),
                    )
            )

    # setting nodal positions and info
    for ix, node in enumerate(graph.nodes()):
        x, y, z = get_position(graph.node[node])
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['z'].append(z)
        node_trace['text'].append(node)
        node_trace['marker']['color'].append(ix)

    axis = dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

    scene = Scene(xaxis=XAxis(axis),
                  yaxis=YAxis(axis),
                  zaxis=ZAxis(axis))

    annotations = Annotations([
        Annotation(showarrow=False, text=plot_description,
                   xref='paper', yref='paper',
                   x=0, y=0.1,  # z=0.05,
                   xanchor='left', yanchor='bottom',  # zanchor='bottom',
                   font=Font(size=14))
        ])

    layout = Layout(
            title=plot_title,
            titlefont=dict(size=16),
            # width=1000,
            # height=1000,
            showlegend=False,
            hovermode='closest',
            scene=scene,
            margin=Margin(t=100),
            # margin=dict(b=20,l=5,r=5,t=40),
            annotations=annotations,
            )

    fig_data = Data([edge_trace, node_trace])

    fig = Figure(data=fig_data, layout=layout)

    # py.iplot(fig, filename='networkx')
    return fig
