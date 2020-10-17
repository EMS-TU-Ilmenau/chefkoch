import chefkoch.recipe as rcp
import chefkoch.container as cntnr
# flav = rec.readfile('flavour',
# 'flavour.yaml')
recdict = cntnr.YAMLContainer('/mnt/c/Users/makle/PycharmProjects/chefkoch/test2/recipe.yml')

reci = rcp.readrecipe(recdict.data)
# reci = rcp.readfile('recipe',
#                     '/home/maka/PycharmProjects/chefkoch/test/recipe.yaml')

# x = (reci.getPrerequisits(4))
# x.reverse()

y = rcp.Plan(reci, "render_figure_z")
# for i in x:
#     print(i.name)
print(y.getItems())
print(y)
