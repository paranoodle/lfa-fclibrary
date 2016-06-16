import numpy as np
import csv
import time
import random
from scipy import stats


class FuzzyPoint:
    """
    Represents a point, for use in fuzzy clustering algorithms.
    Linked to its containing clusters, with weights.
    """
    def __init__(self, value):
        self.value = value
        self.clusters = {}

    @property
    def weight(self):
        return sum(self.clusters[c] for c in self.clusters)

    def assign_cluster(self, new_cluster, new_weight):
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
    """
    Represents a cluster, for use in fuzzy clustering algorithms.
    Linked to its contained points, with weights.
    """
    def __init__(self, points=None, center=None, fuzziness_index=2):
        self.points = {}
        self.fuzziness_index = fuzziness_index
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
            sumA = np.zeros(len(self.center))
            sumB = 0.
            for point in self.points:
                x = self.points[point] ** self.fuzziness_index
                sumA = np.sum([[X * x for X in point], sumA], axis=0)
                sumB += x

            return [x / sumB for x in sumA]
        else:
            return self.center

    def update_center(self, verbose=False):
        old_center = self.center
        self.center = self.compute_center()
        if verbose: print "    center updated", old_center, "->", self.center
        return np.linalg.norm(np.array(self.center) - np.array(old_center))

    def __str__(self):
        return "cluster at center " + str(self.center)


def csv2array(filename):
    """

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

        out.append(FuzzyPoint(np.array(coord)))

    return out, ids


def simple_C(input, initial_centers, termination_value=1, fuzziness_index=2, verbose=False):
    """
    C-means implementation, sorts a set of data into fuzzy clusters.
    Args:
        - input (nparray[FuzzyPoint]): Array of observations
        - initial_centers (list): List of cluster centers
        - termination_value (float): Total distance from cluster updates allowed before the clusters are considered as updated
        - fuzziness_index (float): How "fuzzy" the cluster thresholds are allowed to be
        - verbose (bool): Whether to output computation details
    Returns:
        - list[FuzzyCluster] of the clusters with their contained points and weights
    """
    clusters = []
    for i in initial_centers:
        clusters.append(FuzzyCluster(center=i, fuzziness_index=fuzziness_index))

    while True:
        fuzzy_membership = {}
        fuzzy_distance = {}

        # assignment
        if verbose: print "assignment step"
        for i, point in enumerate(input):
            if verbose: print "  point", point

            for k, cluster in enumerate(clusters):
                fuzzy_distance[(i,k)] = point.distance_to(cluster.center)
                if verbose: print "    distance to", cluster, ":", fuzzy_distance[(i,k)]

            for j, cluster in enumerate(clusters):
                fil = {k:v for k,v in fuzzy_distance.iteritems() if k[0] == i}

                m = min(fil, key=fil.get)

                if fuzzy_distance[m] == 0.0:
                    fuzzy_membership[(i,j)] = 1.0 if m == (i,j) else 0.0
                else:
                    d = map(lambda x: (fuzzy_distance[(i,j)] / fuzzy_distance[x]) ** (2. / (fuzziness_index - 1)), fil.keys())
                    fuzzy_membership[(i,j)] = 1. / sum(d)

                point.assign_cluster(cluster, fuzzy_membership[(i,j)])
                if verbose: print "    assigned to", cluster, "with membership", fuzzy_membership[(i,j)]

        # update
        if verbose: print "update step"
        cluster_sum = sum(c.update_center(verbose) for c in clusters)
        if verbose: print "testing", cluster_sum, "<", termination_value
        updated = cluster_sum > termination_value

        if not updated:
            print "finish :)"
            return clusters
