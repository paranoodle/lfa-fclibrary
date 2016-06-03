import numpy as np
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import random
from scipy import stats


def kmpp(input, cluster_count, verbose=False):
  """K-means++. Computes starting cluster centers from a list of points.

  Args:
      input (nparray[Point]): Array of observations
      cluster_count (int): Number of desired clusters
      verbose (bool): """

  start = time.clock()

  # choose first random center
  i = random.randint(0,len(input)-1)
  centers = [input[i].value]

  for iter in xrange(cluster_count - 1):
    # calculate distance
    if verbose: print "step 1"
    dist = []
    for x in input:
      dist.append(min([x.distance_to(c) for c in centers]))
    if verbose: print "  dist",dist

    # obtain new center
    if verbose: print "step 2"
    xk = np.arange(len(input))
    dist_2 = map(lambda d: d ** 2, dist)
    dist_s = float(sum(dist_2))
    pk = map(lambda d: d / dist_s, dist_2) # probabilities, sum=1
    if verbose: print "  probabilities", pk
    rand = stats.rv_discrete(values=(xk, pk))
    centers.append(np.asarray(input[rand.rvs()].value))
    if verbose: print "  new center", centers[-1], "->", centers

  print "K-means++ complete, time taken:", time.clock() - start, "seconds"
  return centers


class Point:
  def __init__(self, value):
    self.value = value
    self.cluster = None

  def assign_cluster(self, new_cluster):
    if self.cluster:
      self.cluster.points.remove(self)

    self.cluster = new_cluster
    new_cluster.points.append(self)

  def distance_to(self, point):
    return np.linalg.norm(self.value - point)
    #return self.value - point

  def __getitem__(self, i):
    return self.value[i]

  def __str__(self):
    return str(self.value)


class Cluster:
  def __init__(self, points=None, center=None):
    if points:
      self.points = points
    else:
      self.points = []

    if center != None:
      self.center = center
    else:
      self.center = self.compute_center()

  def compute_center(self):
    if self.points:
      #return sum(p.value for p in self.points) / float(len(self.points))
      return np.mean([p.value for p in self.points], axis=0)
    else:
      return self.center

  def update_center(self):
    old_center = self.center
    self.center = self.compute_center()
    print " ", self, "with", [p.value for p in self.points]
    print "    center updated", old_center, "->", self.center
    return not np.array_equal(old_center, self.center)

  def __str__(self):
    return "cluster at center " + str(self.center)


def wcss(clusters):
  sum = 0

  for c in clusters:
    for x in c.points:
      sum += (x - c.center) ** 2

  return sum

def simple_K(input, initial_centers):
  clusters = []
  for i in initial_centers:
    clusters.append(Cluster(center=i))

  while True:
    # assignment
    print "assignment step"
    for x in input:
      print "  point", x
      min = (None, np.inf)
      for c in clusters:
        dist = x.distance_to(c.center) ** 2
        print "    distance to", c, ":", dist
        if dist < min[1]:
          min = (c, dist)
      print "    point", x, "added to", min[0]
      x.assign_cluster(min[0])
      #print "   ", x.cluster, "contains points", [p.value for p in x.cluster.points]

    # update
    print "update step"
    updated = False
    for c in clusters:
      updated = c.update_center() or updated
      print "   ", updated

    if not updated:
      print "\nfinal clusters:", [str(c) for c in clusters]
      return clusters

def csv2array(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)

    out = []
    ids = []
    for line in lines:
        coord = []

        # Keep only float/integer
        for value in line:
            try:
                #print float(value)
                coord.append(float(value))
            except ValueError as ve:
                ids.append(value)
                continue

        out.append(Point(np.array(coord)))



    #print out
    #print out[0], out[1]
    #print np.linalg.norm(out[0]-out[1])
    return out, ids


test, ids =  csv2array("dataset/iris.data")
print len(ids)


centers =  kmpp(test, 3)

results = simple_K(test, centers)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for t in results[0].points:
    ax.scatter(t.value[0], t.value[1], t.value[2], c="yellow")
for t in results[1].points:
    ax.scatter(t.value[0], t.value[1], t.value[2], c="red")
for t in results[2].points:
    ax.scatter(t.value[0], t.value[1], t.value[2], c="blue")

ax.set_xlabel('sepal length')
ax.set_ylabel('sepal width')
ax.set_zlabel('petal length')

plt.show()



print "len(points): %i" % len(results[0].points)
print "len(points): %i" % len(results[1].points)
print "len(points): %i" % len(results[2].points)

def getClusterSpecy(points, values):
    matches = [0,0,0]
    i = 0
    for v in values:
        for coord in points:
            point = [coord.value[0], coord.value[1], coord.value[2], coord.value[3]]

            if (point == test[i][:4]).all():
                matches[i/50] += 1
        i += 1

    return max(enumerate(matches), key=lambda x: x[1])[0]

cluster_ids = []
cluster_ids.append(getClusterSpecy(results[0].points, test))
cluster_ids.append(getClusterSpecy(results[1].points, test))
cluster_ids.append(getClusterSpecy(results[2].points, test))
print cluster_ids

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for n in range(3):
    for v in test[50*cluster_ids[n]:50*(cluster_ids[n]+1)]:
        color = "red"
        for coord in results[n].points:
            point = [round(coord.value[0], 1), round(coord.value[1], 1), round(coord.value[2], 1), round(coord.value[3], 1)]

            if (point == v[:4]).all():
                color = "blue"
                break


        ax.scatter(v[0], v[1], v[2], c=color)


ax.set_xlabel('sepal length')
ax.set_ylabel('sepal width')
ax.set_zlabel('petal length')

plt.show()
