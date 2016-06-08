import numpy as np

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
        assert(self.weight + new_weight <= 1, "cluster weights > 1")

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


def simple_C(input, initial_centers, verbose=True):
    """not actually that simple"""
    clusters = []
    for i in initial_centers:
        clusters.append(Cluster(center=i))

    while True:
        # assignment
        if verbose: print "assignment step"

        # update

        if not updated:
            print "finish :)"
