import numpy as np
import csv

import time
import random
from scipy import stats

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
      return np.mean([p.value for p in self.points], axis=0)
    else:
      return self.center

  def update_center(self, verbose=False):
    old_center = self.center
    self.center = self.compute_center()
    if verbose: print " ", self, "with", [p.value for p in self.points]
    if verbose: print "    center updated", old_center, "->", self.center
    return not np.array_equal(old_center, self.center)

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

    # update
    if verbose: print "update step"
    updated = False
    for c in clusters:
      updated = c.update_center() or updated
      if verbose: print "   ", updated

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
                coord.append(float(value))
            except ValueError as ve:
                ids.append(value)
                continue

        out.append(Point(np.array(coord)))

    return out, ids
