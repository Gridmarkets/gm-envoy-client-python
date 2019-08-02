"""
The MIT License (MIT)

Copyright (c) 2015 Michael Wayne Goodman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMI++
TED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from builtins import filter
from builtins import object
import warnings
from collections import namedtuple, defaultdict

#Node = namedtuple('Node', ('id', 'data', 'edges', 'in_edges'))
#Edge = namedtuple('Edge', ('start', 'end', 'label', 'data', 'directed'))

class MiniGraphError(Exception): pass
class MiniGraphWarning(Warning): pass

# todo: consider functools.lru_cache for the retrieval methods

class MiniGraph(object):
    __slots__ = ('_graph',)

    def __init__(self, nodes=None, edges=None):

        self._graph = {}
        # nodes
        if nodes is None:
            nodes = {}
        self.add_nodes(nodes)
        # edges
        if edges is None:
            edges = {}
        self.add_edges(edges)

    @classmethod
    def fast_init(cls, nodes=None, edges=None):
        """
        Initializes the graph without argument checking of edges, which
        means that all edges must be 5-tuples of:
          (start, end, label, data, directed)
        """
        mg = cls(nodes)
        if edges is not None:
            mg._fast_add_edges1(edges)
        return mg

    @classmethod
    def fast_init2(cls, nodes, edges=None):
        """
        Initializes the graph without argument checking of edges, which
        means that all edges must be 5-tuples of:
          (start, end, label, data, directed)
        Furthermore, all edges must only uses nodes specified in the
        nodes argument.
        """
        mg = cls(nodes)
        if edges is not None:
            mg._fast_add_edges2(edges)
        return mg

    def __getitem__(self, idx):
        """
        Fancy graph queries:
          - if idx is an integer, return the node given by idx
          - if idx is a slice, return the edges matching
            start:end:label. Note that not specifying the label uses
            the label of None, which is a valid label. If you want to
            consider all labels, use Ellipsis: (g[0:1:...]). All edges
            can be retrieved with g[::...].
        """

        try:
            start, end, label = idx.start, idx.stop, idx.step
            if label is Ellipsis:
                return self.find_edges(start, end)
            else:
                return self.find_edges(start, end, label=label)
        except AttributeError:
            return (idx, self.nodes[idx])

    def add_node(self, nodeid, data=None):
        # if nodeid in self.nodes:
        #     raise MiniGraphError('Node already exists: {}'.format(nodeid))
        #self.nodes[nodeid] = dict(data or [])
        if data is None:
            data = {}
        if nodeid in self._graph:
            self._graph[nodeid][1].update(data)
        else:
            self._graph[nodeid] = (nodeid, data, {}, {})

    def add_nodes(self, nodes):
        for node in nodes:
            try:
                node, data = node
            except TypeError:
                data = {}
            self.add_node(node, data=data)

    def remove_node(self, nodeid):
        g = self._graph
        if nodeid not in g:
            raise KeyError(nodeid)
        _prune_edges(g, nodeid)
        del g[nodeid]

    def node(self, nodeid):
        return self._graph[nodeid]

    def nodes(self):
        return [(nid, n[1]) for nid, n in list(self._graph.items())]

    def add_edge(self, start, end, label=None, data=None, directed=True):
        self.add_edges([(start, end, label, data, directed)])

    #@profile
    def add_edges(self, edges):
        g = self._graph
        add_edge = _add_edge

        for edge in edges:
            edgelen = len(edge)
            if edgelen == 5:
                start, end, label, data, directed = edge
            elif edgelen == 2:
                start, end = edge; label = data = None; directed = True
            elif edgelen == 4:
                start, end, label, data = edge; directed = True
            elif edgelen == 3:
                start, end, label = edge; data = None; directed = True
            else:
                raise MiniGraphError('Invalid edge: {}'.format(edge))

            if data is None: data = {}
            if start not in g: g[start] = (start, {}, {}, {})
            if end not in g: g[end] = (end, {}, {}, {})

            e = (start, end, label, data, directed)

            #add_edge(g[start][2], label, end, e)
            d = g[start][2]
            if label not in d:
                d[label] = innerdict = {}
            else:
                innerdict = d[label]
            if end not in innerdict:
                innerdict[end] = e
            else:
                if innerdict[end][4] != e[4]:
                    raise MiniGraphError(
                        'Cannot update directed and undirected edges.'
                    )
                innerdict[end][3].update(e[3])

            
            #add_edge(g[end][3], label, start, e)
            d = g[end][3]
            if label not in d:
                d[label] = innerdict = {}
            else:
                innerdict = d[label]
            if start not in innerdict:
                innerdict[start] = e
            else:
                if innerdict[start][4] != e[4]:
                    raise MiniGraphError(
                        'Cannot update directed and undirected edges.'
                    )
                innerdict[start][3].update(e[3])

            if directed is False:
                #add_edge(g[end][2], label, start, e)
                d = g[end][2]
                if label not in d:
                    d[label] = innerdict = {}
                else:
                    innerdict = d[label]
                if start not in innerdict:
                    innerdict[start] = e
                else:
                    if innerdict[start][4] != e[4]:
                        raise MiniGraphError(
                            'Cannot update directed and undirected edges.'
                        )
                    innerdict[start][3].update(e[3])

                #add_edge(g[start][3], label, end, e)
                d = g[start][3]
                if label not in d:
                    d[label] = innerdict = {}
                else:
                    innerdict = d[label]
                if end not in innerdict:
                    innerdict[end] = e
                else:
                    if innerdict[end][4] != e[4]:
                        raise MiniGraphError(
                            'Cannot update directed and undirected edges.'
                        )
                    innerdict[end][3].update(e[3])

    def _fast_add_edges1(self, edges):
        g = self._graph
        add_edge = _add_edge

        for e in edges:
            start = e[0]
            end = e[1]
            label = e[2]
            directed = e[4]
            if start not in g:
                g[start] = (start, {}, {}, {})
            if end not in g:
                g[end] = (end, {}, {}, {})

            #add_edge(g[start][2], label, end, e)
            d = g[start][2]
            if label not in d:
                d[label] = innerdict = {}
            else:
                innerdict = d[label]
            if end not in innerdict:
                innerdict[end] = e
            else:
                if innerdict[end][4] != e[4]:
                    raise MiniGraphError(
                        'Cannot update directed and undirected edges.'
                    )
                innerdict[end][3].update(e[3])

            
            #add_edge(g[end][3], label, start, e)
            d = g[end][3]
            if label not in d:
                d[label] = innerdict = {}
            else:
                innerdict = d[label]
            if start not in innerdict:
                innerdict[start] = e
            else:
                if innerdict[start][4] != e[4]:
                    raise MiniGraphError(
                        'Cannot update directed and undirected edges.'
                    )
                innerdict[start][3].update(e[3])

            if directed is False:
                #add_edge(g[end][2], label, start, e)
                d = g[end][2]
                if label not in d:
                    d[label] = innerdict = {}
                else:
                    innerdict = d[label]
                if start not in innerdict:
                    innerdict[start] = e
                else:
                    if innerdict[start][4] != e[4]:
                        raise MiniGraphError(
                            'Cannot update directed and undirected edges.'
                        )
                    innerdict[start][3].update(e[3])

                #add_edge(g[start][3], label, end, e)
                d = g[start][3]
                if label not in d:
                    d[label] = innerdict = {}
                else:
                    innerdict = d[label]
                if end not in innerdict:
                    innerdict[end] = e
                else:
                    if innerdict[end][4] != e[4]:
                        raise MiniGraphError(
                            'Cannot update directed and undirected edges.'
                        )
                    innerdict[end][3].update(e[3])

    def _fast_add_edges2(self, edges):
        g = self._graph
        add_edge = _add_edge

        for e in edges:
            start = e[0]
            end = e[1]
            label = e[2]
            directed = e[4]
            add_edge(g[start][2], label, end, e)
            add_edge(g[end][3], label, start, e)
            if directed is False:
                add_edge(g[end][2], label, start, e)
                add_edge(g[start][3], label, end, e)

    def remove_edge(self, start, end, label=None, directed=None):
        g = self._graph
        if start not in g: raise KeyError(start)
        edges = g[start][2]
        if label not in edges: raise KeyError(label)
        if end not in edges[label]: raise KeyError(end)
        _dir = g[start][2][label][end][4]
        if directed is not None:
            assert _dir == directed

        try:
            in_edges = g[end][3]
            del edges[label][end]
            if len(edges[label]) == 0:
                del edges[label]
            del in_edges[label][start]
            if len(in_edges[label]) == 0:
                del in_edges[label]
            # undirected links are listed twice (except simple loops)
            if not _dir and start != end:
                edges = g[end][2]
                in_edges = g[start][3]
                del edges[label][start]
                if len(edges[label]) == 0:
                    del edges[label]
                del in_edges[label][end]
                if len(in_edges[label]) == 0:
                    del in_edges[label]

        except KeyError:
            raise
            warnings.warn(
                'Unexpected KeyError while removing {} edge ({}, {}, {})'
                .format('directed' if directed else 'undirected',
                        start, end, label),
                MiniGraphWarning
            )

    def edge(self, start, end, label=None, directed=None):
        e = self._graph[start][2][label][end]
        if directed is not None:
            assert e[4] == directed
        return e

    def edges(self):
        return [e
            for nid, n in list(self._graph.items())
            for ed in list(n[2].values())
            for e in list(ed.values())
            # only include undirected links from the source node (whatever
            # the source node was when it was instantiated)
            if e[4] or e[0] == nid
        ]

    def find_edges(self, start=None, end=None, **kwargs):
        if start is Ellipsis: start = None
        if end is Ellipsis: end = None

        # get appropriate edge dicts (both if 'directed' is unspecified)
        if 'directed' in kwargs:
            if kwargs['directed'] is True: xs = [self.edges]
            elif kwargs['directed'] is False: xs = [self.uedges]
            else: xs = [self.edges, self.uedges]

        # filter by start, if specified
        if start is None:
            xs = [(s, sd) for d in xs for s, sd in list(d.items())]
        else:
            xs = [(start, d[start]) for d in xs if start in d]

        # filter by label, if specified
        try:
            lbl = kwargs['label']
            xs = ((s, lbl, sd[lbl]) for s, sd in xs if lbl in sd)
        except KeyError:
            xs = ((s, lbl, ld) for s, sd in xs for lbl, ld in list(sd.items()))

        # filter by end, if specified
        if end is None:
            xs = ((s, e, lbl, d) for s, lbl, ld in xs for e, d in list(ld.items()))
        else:
            xs = ((s, end, lbl, ld[end]) for s, lbl, ld in xs if end in ld)

        # filter by data, if specified
        try:
            data = kwargs['data']
            xs = list(filter(
                lambda s,e,l,d: all(d.get(k) == v for k, v in list(data.items())),
                xs
            ))
        except KeyError:
            pass

        return list(xs)

    def order(self):
        return len(self._graph)

    def size(self):
        return len(self.edges())

    def degree(self, nodeid):
        n = self._graph[nodeid]
        return (
            sum(len(ed) for ed in list(n[2].values())) +
            len([
                e for ed in list(n[3].values()) for e in list(ed.values())
                # only count undirected edges here if they are simple loops
                if e[4] or e[0] == e[1]
            ])
        )

    def out_degree(self, nodeid):
        n = self._graph[nodeid]
        return sum(len(ed) for ed in list(n[2].values()))
        # return (
        #     sum(len(ed) for ed in n[2].values()) +
        #     len([e  for ed in n[3].values()
        #             for e in ed.values()
        #             if e[4] == False and e[0] != e[1]])
        # )

    def in_degree(self, nodeid):
        n = self._graph[nodeid]
        return sum(len(ed) for ed in list(n[3].values()))
        # return (
        #     sum(len(ed) for ed in n[3].values()) +
        #     len([e  for ed in n[2].values()
        #             for e in ed.values()
        #             if e[4] == False and e[0] != e[1]])
        # )

    def subgraph(self, nodeids):
        g = self._graph
        nidset = set(nodeids)
        return MiniGraph(
            nodes=[(nid, g[nid][1]) for nid in nodeids],
            edges=[e for start in nodeids
                     for label, ed in list(g[start][2].items())
                     for end, e in list(ed.items()) if end in nidset]
        )

    # def connected(self):
    #     nodeset = set()
    #     remaining = set(self.nodes.keys())

    #     for start in self.nodes:
    #         if node not in nodeset:
    #             nodeset.add(node)

# def _degree(nodeid, edgedicts):
#     ds = []
#     for d in edgedicts:
#         if nodeid in d:
#             ds.append(d[nodeid])
#     return sum(len(ld) for d in ds for ld in d.values())

def _prune_edges(graph, nodeid):
    g = graph[nodeid]
    # forward links; remove reverse links on ends
    edict = defaultdict(list)
    for ed in list(g[2].values()):
        for e in list(ed.values()):
            if e[1] != nodeid:  # this will get removed anyway
                edict[e[1]].append(e)
    for end, es in list(edict.items()):
        ld = graph[end][3]
        for e in es:
            del ld[e[2]][e[0]]
            if len(ld[e[2]]) == 0:
                del ld[e[2]]
    # backward links; remove forward links on starts
    edict = defaultdict(list)
    for ed in list(g[3].values()):
        for e in list(ed.values()):
            if e[0] != nodeid:  # this will get removed anyway
                edict[e[0]].append(e)
    for start, es in list(edict.items()):
        ld = graph[start][2]
        for e in es:
            del ld[e[2]][e[1]]
            if len(ld[e[2]]) == 0:
                del ld[e[2]]

# for a bit more speed, this can be inlined directly
def _add_edge(d, label, idx, e):
    if label not in d:
        d[label] = innerdict = {}
    else:
        innerdict = d[label]
    if idx not in innerdict:
        innerdict[idx] = e
    else:
        if innerdict[idx][4] != e[4]:
            raise MiniGraphError(
                'Cannot update directed and undirected edges.'
            )
        innerdict[idx][3].update(e[3])
