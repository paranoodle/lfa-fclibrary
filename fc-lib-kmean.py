import numpy as np
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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


def kmpp(input):
  pass


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
    for line in lines:
        coord = []

        # Keep only float/integer
        for value in line:
            try:
                #print float(value)
                coord.append(float(value))
            except ValueError as ve:
                continue

        out.append(Point(np.array(coord)))
    #print out
    #print out[0], out[1]
    #print np.linalg.norm(out[0]-out[1])
    return out

test =  csv2array("dataset/iris.data")
#test = [Point(1), Point(2), Point(3), Point(4)]
results = simple_K(test, [np.array([5,5,5,5]),np.array([3,3,3,3]), np.array([2,2,2,2])])

#print "\nresults[1].points: ", results[1].points

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
