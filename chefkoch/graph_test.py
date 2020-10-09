from graph import Graph
import chefkoch.recipe as rcp
import chefkoch.container as cntnr

recdict = cntnr.YAMLContainer('/home/maka/Downloads/recipe.yml')
print(recdict.data)
reci = rcp.readrecipe(recdict.data)

g = reci.graph
print(g)
# g.add_node(1)
# g.add_node(2)
# g.add_node(3)
# g.add_node(4)
# g.add_node(5)
# g.add_node(6)

