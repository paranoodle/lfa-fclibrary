import numpy as np
from scipy import stats
import random
import time


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
    # TODO: check equal dimensions
    # TODO: adapt to 2+ dimensions
    return abs(self.value - point)

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
      return sum(p.value for p in self.points) / float(len(self.points))
      #return np.mean(self.points)
    else:
      return self.center

  def update_center(self, verbose=False):
    old_center = self.center
    self.center = self.compute_center()
    if verbose: print " ", self, "with", [p.value for p in self.points]
    if verbose: print "    center updated", old_center, "->", self.center
    return (old_center != self.center)

  def __str__(self):
    return "cluster at center " + str(self.center)


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
    centers.append(input[rand.rvs()].value)
    if verbose: print "  new center", centers[-1], "->", centers

  print "K-means++ complete, time taken:", time.clock() - start, "seconds"
  return centers


def simple_K(input, initial_centers, verbose=False):
  """Basic K-means.

  Args:
      input (nparray[Point]): Array of observations
      initial_centers (list[?]): Array of initial centers"""

  start = time.clock()

  clusters = []
  for i in initial_centers:
    clusters.append(Cluster(center=i))

  while True:
    # assignment
    if verbose: print "assignment step"
    for x in input:
      if verbose: print "  point", x
      min = (None, np.inf)
      for c in clusters:
        dist = x.distance_to(c.center) ** 2
        if verbose: print "    distance to", c, ":", dist
        if dist < min[1]:
          min = (c, dist)
      if verbose: print "    point", x, "added to", min[0]
      x.assign_cluster(min[0])
      if verbose: print "   ", x.cluster, "contains points", [p.value for p in x.cluster.points]

    # update
    if verbose: print "update step"
    updated = False
    for c in clusters:
      updated = c.update_center(verbose) or updated
      if verbose: print "   ", updated

    if not updated:
      if verbose: print "Final clusters:", [str(c) for c in clusters]
      print "K-means complete, time taken:", time.clock() - start, "seconds"
      return clusters

test = [Point(1), Point(2), Point(3), Point(4)]
simple_K(test, kmpp(test, 2))

simple_K(test, [0,5])
