import ratios as rat
import matplotlib.pyplot as plt
import numpy as np
import copy

# def plot_matrix(matrix):
#   # matrix = copy.deepcopy(matrix).reverse()
#   # plt.matshow(matrix)
#   # plt.colorbar()
#   # plt.show()
#   # plt.clf()
#
#   fig = plt.figure()
#   ax = fig.add_subplot(1,1,1)
#   ax.set_aspect('equal')
#   #plt.imshow(matrix, interpolation='nearest', cmap=plt.cm.ocean)
#   #plt.imshow(matrix, interpolation='nearest', extent=(0.5,18.5,0.5,18.5))
#   plt.imshow(matrix, interpolation='nearest', cmap=plt.cm.ocean)
#   plt.colorbar()
#   plt.show()

def plot_cube(cube, rows=3, cols=6):
  npcube = np.array(cube)
  fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(18, 10))

  for y in range(rows):
    for x in range(cols):
      i = y*6+x
      matrix = npcube[:,:,i]
      ax = plt.subplot(rows,cols,i+1)
      ax.set_title('Slice %i' % (i+1))
      if x == 0: ax.set_ylabel('singleton threshold')
      ax.set_xlabel('pair threshold')
      plt.imshow(matrix, interpolation='nearest')
      #plt.colorbar()

  plt.show()

def main():
  c = rat.error_ratios_cross_val('../tmp/cv_200000_30/')
  cr = copy.deepcopy(c) # copy

  for x in range(19):
    for y in range(19):
      for z in range(19):
        t = cr[x][y][z]
        maxent_best = t[2]
        ext_best = t[3]
        try:
          cr[x][y][z] = maxent_best/float(ext_best)
        except:
          cr[x][y][z] = maxent_best

  # for i in range(19):
  #   plot_matrix(cr[:][:][i])

  plot_cube(cr)


if __name__ == '__main__':
  main()
