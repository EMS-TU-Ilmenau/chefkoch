from graph import Graph
import chefkoch.recipe as rcp
import chefkoch.container as cntnr

# recdict = cntnr.YAMLContainer('/home/maka/Downloads/recipe.yml')
# print(recdict.data)
# reci = rcp.readrecipe(recdict.data)
#
# g = reci.graph
# print(g.nodes())
# print(g.edges())
# print(g.adjacency_matrix())
# print("compute_a" in g)
# paths = g.all_paths("compute_a", "render_figure_z")
# print("fff")

g2 = Graph()

g2.add_node(1)
g2.add_node(2)
g2.add_node(3)
g2.add_node(4)
g2.add_node(5)
g2.add_node(6)

g2.add_edge(1, 2)
g2.add_edge(1, 3)
g2.add_edge(2, 4)
g2.add_edge(2, 5)
g2.add_edge(3, 4)
g2.add_edge(3, 5)
g2.add_edge(4, 6)
g2.add_edge(5, 6)

p2 = g2.all_paths(1, 6)
p3 = g2.all_paths(4, 6)


g3 = g2.subgraph_from_nodes([1, 2, 4, 5, 6, 2, 2])

print(2)
print("fff")

