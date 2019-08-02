from __future__ import absolute_import
from builtins import object
import re
from distutils.version import LooseVersion
from . import minigraph as mg

class Resolver(object):
    """Class to compute compatible combination of products"""

    def __init__(self, products):
        """Constructor

        :param products: pass the products JSON received from the buyer API call
        """

        # store the products
        self.products = products

        # create a graph (vertices in format product:version and) and create edges with data from compatibility field
        # note that this directed graph by default
        self.graph = mg.MiniGraph()

        for item in self.products:
            app_type = item["app_type"]
            app_version = item["version"]
            product_node = "{0}:{1}".format(app_type, app_version)
            compatible_modules = item["compatible_modules"]

            # add the product node and data which we can use later
            self.graph.add_node(product_node, data={'is_plugin': False})

            for plugin_node in compatible_modules:
                # add plugin node with data, note that we don't have a friendly name for plugin hence type and name will be same
                self.graph.add_node(plugin_node, data={'is_plugin': True})

                # add the edge between product node and plugin node
                self.graph.add_edge(product_node, plugin_node)

    def get_compatible_combinations(self, query, strict_version_matches=False, include_query_types=False):
        """ Method to get bi-directional queries to get compatible combinations between product and plugins

        :param query: pass one or more products or plugins in format [app_type]:[version], [plugin_type]:[version] as list or tuple
        :return: matches product combinations as a dict ex. "{"hou_redshift": {"versions": ["2.6.37", "2.6.38", "2.6.39"], "is_plugin": true}}
        """

        if not query or not isinstance(query, (list, tuple)):
            raise ValueError("query parameter should be list or tuple")

        # get the types from query
        qry_item_types = [item.split(':')[0] for item in query]

        # # compute matches from the graph edges
        edges = self.graph.edges()

        if strict_version_matches:
            left_vertices_match =   [e[1] for e in edges if e[0] in query]
            right_vertices_match =  [e[0] for e in edges if e[1] in query]

            # compute matches from the graph edges
            matches = set(left_vertices_match+right_vertices_match)

        else:
            # make regex patterns so we can match partial versions
            re_queries = []
            for item in query:
                # if only the product name has been requested, fix the query to match all versions
                if ":" not in item:
                    item = item+":[0-9]+"
                item += "(\.|$|(?<=[0-9])[v])"
                re_queries.append(re.compile(item)) # check that our pattern either ends in a . or is the end of the string.
                                                                            #   since nuke uses formatting like 10.5v1, we also match v as if it was a .,
                                                                            #   if it is preceded by a number

            # compare each edge to see if it starts with a query
            matches = set()
            for edge in edges:
                for re_query in re_queries:
                    if re_query.match(edge[0]):
                        matches.add(edge[1])
                        matches.add(edge[0])

                    if re_query.match(edge[1]):
                        matches.add(edge[0])
                        matches.add(edge[1])
            # print " > EDGE MATCHES", matches

            # prune the matches to exclude the elements that dont' match
            pruned_matches = set()
            non_queried_matches = set()
            for match in matches:
                qry_item_type = match.split(':')[0]
                for re_query in re_queries:
                    if re_query.match(match):
                        pruned_matches.add(match)

                    elif qry_item_type not in qry_item_types:
                        non_queried_matches.add(match)

                matches = pruned_matches
            # print " > PRUNED MATCHES", matches

            # add back in the nodes we had edges to, but didn't search for explicitly
            for non_queried_match in non_queried_matches:
                for edge in edges:
                    if non_queried_match in edge:
                        if edge[0] in matches or edge[1] in matches:
                            matches.add(non_queried_match)
            # print " > FINAL MATCHES", matches

        # return the matches aggregated by version for each product type
        result = {}

        for item in matches:
            item_type, item_version = item.split(':')

            # matches list includes the items from query
            # don't need to include any item with the same product type as in query
            if item_type not in qry_item_types or include_query_types:
                # get node data
                node_data = self.graph.node(item)[1]

                if item_type not in result:
                    result[item_type] = dict()
                    result[item_type]['is_plugin'] = node_data['is_plugin']
                    result[item_type]['versions'] = list()
            
                result[item_type]['versions'].append(item_version)

        # sorting of versions done using distutils.version
        # sort the versions in each
        for item_type, version_items in result.items():
            result[item_type]['versions'] = sorted(version_items['versions'], key=LooseVersion)
        
        return result

    def get_versions_by_type(self, query):
        """ method to get the list of version for a item type

        :param query: query is either an app_type for a product or plugin_type for a plugin
        :return: returns an array of version for an item type
        """

        result = []

        # note it is an O(n) iteration for now, we can re-look at this later if we are dealing with a very large list
        for item in self.graph.nodes():
            item_type, item_version = item[0].split(':')

            if item_type == query:
                result.append(item_version)

        # sorting of versions done using distutils.version
        return sorted(result, key=LooseVersion)

    def get_all_types(self):
        """ get all the types and their respective versions
        "return: returns a dict { "hou": { "versions": ["17.5.173", "17.5.229"], "is_plugin": false } }
        """

        result = {}

        for item in self.graph.nodes():
            item_type, item_version = item[0].split(':')

            # get the node data
            node_data = item[1]

            if item_type not in result:
                result[item_type] = dict()
                result[item_type]['is_plugin'] = node_data['is_plugin']
                result[item_type]['versions'] = list()
            
            result[item_type]['versions'].append(item_version)

        # sorting of versions done using distutils.version
        for item_type, version_items in result.items():
            result[item_type]['versions'] = sorted(version_items['versions'], key=LooseVersion)

        return result
