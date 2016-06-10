import numpy as np
import csv
import time
import random
from scipy import stats

class FuzzyPoint:
    def __init__(self, value):
        self.value = value
        self.clusters = {}

    @property
    def weight(self):
        return sum(self.clusters[c] for c in self.clusters)

    def assign_cluster(self, new_cluster, new_weight):
        #assert(self.weight + new_weight <= 1, "cluster weights > 1")

        self.clusters[new_cluster] = new_weight
        new_cluster.assign_point(self, new_weight)

    def remove_cluster(self, cluster):
        assert(cluster in self.clusters, "trying to remove absent cluster")

        cluster.remove_point(self)
        self.clusters.pop(cluster)

    def distance_to(self, point):
        return np.linalg.norm(self.value - point)

    def __getitem__(self, i):
        return self.value[i]

    def __str__(self):
        return str(self.value)


class FuzzyCluster:
    def __init__(self, points=None, center=None):
        self.points = {}
        if points:
            for p in points:
                self.assign_point(p)

        if center != None:
            self.center = center
        else:
            self.center = self.compute_center()

    def assign_point(self, point, weight=1.0):
        self.points[point] = weight

    def remove_point(self, point):
        assert(point in self.points, "trying to remove absent point")
        self.points.pop(point)

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

        out.append(FuzzyPoint(np.array(coord)))

    return out, ids

"""
@link https://sites.google.com/site/dataclusteringalgorithms/fuzzy-c-means-clustering-algorithm
"""
def simple_C(input, initial_centers, verbose=True, fuzzinessIndex = 1):
    """not actually that simple"""
    clusters = []
    for i in initial_centers:
        clusters.append(FuzzyCluster(center=i))

    while True:
        # assignment
        if verbose: print "assignment step"

        """
        @links https://sites.google.com/site/dataclusteringalgorithms/_/rsrc/1273050108083/fuzzy-c-means-clustering-algorithm/fuzzy1.bmp
        """
        u = [] # uij represents the membership of ith data to jth cluster center.
        d = [] # dij represents the Euclidean distance between ith data and jth cluster center.
        i = 0  # ith point
        for point in input:
            if verbose: print "  point", point
            u.append([])
            d.append([])

            # init
            for k in range(len(clusters)):
                d[i].append(0)
                u[i].append(0)

            j = 0 # jth cluster center
            for cluster in clusters:

                _sum = 0
                d[i][j] = point.distance_to(cluster.center)
                if verbose: print "    distance to", cluster, ":", d[i][j]
                dist = d[i][j] ** 2

                k = 0
                for cluster in clusters:
                    d[i][k] = point.distance_to(cluster.center)

                    _sum += (d[i][j] / d[i][k]) ** (2/fuzzinessIndex - 1)
                    k += 1

                u[i][j] = 1/_sum
                if verbose: print "    weight for", cluster, ":", u[i][j]
                j += 1

            for j in range(len(clusters)):
                point.assign_cluster(clusters[j], u[i][j])

            i += 1


        # update
        if verbose: print "update step"
        updated = False
        for c in clusters:
            updated = c.update_center() or updated

        if not updated:
            print "finish :)"
            return clusters
