import chefkoch.recipe as rcp
import chefkoch.container as cntnr
import os
import chefkoch as ck

# flav = rec.readfile('flavour',
# 'flavour.yaml')
# recdict = cntnr.YAMLContainer('/mnt/c/Users/makle/PycharmProjects/chefkoch/test2/recipe.yml')
#
# reci = rcp.readrecipe(recdict.data)
# reci = rcp.readfile('recipe',
#                     '/home/maka/PycharmProjects/chefkoch/test/recipe.yaml')
#
# # x = (reci.getPrerequisits(4))
# # x.reverse()
#
# y = rcp.Plan(reci, "prisma_volume", "collect_volume")
#
# # for i in x:
# #     print(i.name)
#
# print(y)
# dir = os.getcwd()[:-5]
dir = os.getcwd()[:-9]
# cheffile = dir + "/testdirectory"
cheffile = dir + "\\testdirectory_maria"
args = {
    "options": None,
    "cheffile": None,
    "resource": None,
    "flavour": None,
    "kitchen": None,
    "recipe": None,
    "link": None,
    "targets": None,
}
chef = ck.Chefkoch(cheffile, args)
# y = rcp.Plan(chef.recipe, fridge=chef.fridge)
print(chef)
# os.system('chef test')
