from graph import Graph, Graph3D, visuals
import matplotlib
import chefkoch.recipe as rcp
import chefkoch.container as cntnr

recdict = cntnr.YAMLContainer('/mnt/c/Users/makle/PycharmProjects/chefkoch/test2/recipe.yml')
print(recdict.data)
reci = rcp.readrecipe(recdict.data)

gr = reci.graph

print("matrix ", gr.adjacency_matrix())


# g = Graph()
# g.add_node((0, 0))
# g.add_node((2, 1))
# g.add_node((3, 2))
# g.add_node((3, 3))
# g.add_node((2, 4))
# g.add_node((0, 5))
# g.add_node((0, 6))
# g.add_node((4, 4))
# g.add_node((5, 5))
#
# g.add_edge((0, 0), (2, 1))
# g.add_edge((0, 0), (3, 2))
# g.add_edge((2, 1), (3, 2))
# g.add_edge((2, 1), (3, 3))
# g.add_edge((3, 2), (2, 4))
# g.add_edge((2, 4), (0, 5))
# g.add_edge((0, 5), (0, 6))
# g.add_edge((4, 4), (5, 5))
#
# # dist, tour = g.solve_tsp()
# plt = visuals.plot_2d(g)
# # visuals.
# # start = g.node((0, 0))
# # xs, ys = [c[0] for c in start], [c[1] for c in start]
# plt.plot(6, 6, 'rD', clip_on=False)
# plt.show()

# print(g)

