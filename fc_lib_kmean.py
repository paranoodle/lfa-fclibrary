import numpy as np
import csv

import time
import random
import math
from scipy import stats


class Point:
    """
    Represents a point, for use in hard clustering algorithms.
    Linked to its containing cluster.
    """
    def __init__(self, value):
        self.value = value
        self.cluster = None

    # applies assignment in both directions
    def assign_cluster(self, new_cluster):
        if self.cluster:
            self.cluster.points.remove(self)

        self.cluster = new_cluster
        new_cluster.points.append(self)

    def distance_to(self, point):
        return np.linalg.norm(self.value - point)

    def __getitem__(self, i):
        return self.value[i]

    def __str__(self):
        return str(self.value)


class Cluster:
    """
    Represents a cluster, for use in hard clustering algorithms.
    Linked to its contained points.
    """
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

    # used from the outside to update the centers if possible
    # returns True if the centers have changed, False otherwise
    def update_center(self, verbose=False):
        old_center = self.center
        self.center = self.compute_center()
        if verbose: print " ", self, "with", [p.value for p in self.points]
        if verbose: print "    center updated", old_center, "->", self.center
        return not np.array_equal(old_center, self.center)

    def __str__(self):
        return "cluster at center " + str(self.center)


def sub_clustering(input, radius=1.0, threshold=0.1, verbose=False):
    """
    Algorithm to compute the number of clusters appropriate for a given set of data.
    Args:
        - radius (float): maximum distance to allow from clusters;
        - threshold (float): [0;1], is the proportion of points of data that are allowed to be outside cluster radii.
        - verbose (bool): Whether to output computation details
    Returns:
        - cluster count
    """
    def exp(point1, point2):
        return math.exp(-((point1.distance_to(point2.value))**2)/((radius/2)**2))

    centers = []
    available = [point for point in input]

    if verbose: print "starting with", len(available), "input points"
    while len(available) > (len(input) * threshold):
        densities = {}
        for point in available:
            dm = 0.0
            for point2 in input:
                dm += exp(point, point2)
            densities[point] = dm

        new_center = max(densities, key=densities.get)
        centers.append(new_center)
        if verbose: print "max", max(densities.values())
        if verbose: print "min", min(densities.values())
        if verbose: print "new center", new_center

        for point in available:
            dist = point.distance_to(new_center.value)
            if dist < radius:
                available.remove(point)

        if verbose: print len(available), "points still available"

    return len(centers)


def kmpp(input, cluster_count, verbose=False):
    """
    K-means++. Computes starting cluster centers from a list of points.
    Args:
        - input (nparray[Point] or nparray[FuzzyPoint]): Array of observations
        - cluster_count (int): Number of desired clusters
        - verbose (bool): Whether to output computation details
    Returns:
        - list of cluster centers
    """

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
    """
    K-means implementation, sorts a set of data into clusters.
    Args:
        - input (nparray[Point]): Array of observations
        - initial_centers (list): List of cluster centers
        - verbose (bool): Whether to output computation details
    Returns:
        - list[Cluster] of the clusters with their contained points
    """
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
    """
    Parse a csv file to array
    Args:
        - filename: full path and filename to csv file
    """
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
