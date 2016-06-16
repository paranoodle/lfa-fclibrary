import numpy as np
from scipy import misc
import fc_lib_kmean as fck
import fc_lib_cmean as fcc

import sys


# usage:
#   python fc_images_cmeans.py [c]/[k] [IMAGE_NAME] [CLUSTER_COUNT]
if __name__ == '__main__':
    if len(sys.argv) <= 1 or sys.argv[1] not in ['k', 'c', 'K', 'C']:
        print "Usage: %s c|k IMAGE_NAME CLUSTER_COUNT" % sys.argv[0]
        exit()

    c_mode = sys.argv[1] in ['C', 'c']

    if len(sys.argv) > 2:
        im_name = sys.argv[2]
    else:
        im_name = "testing_mini"

    im = misc.imread(im_name + ".png")
    print "loaded image"

    rows, cols = im.shape[:2]

    test = []
    if c_mode:
        for row in xrange(rows):
            for col in xrange(cols):
                test.append(fcc.FuzzyPoint(im[row,col]))
    else:
        for row in xrange(rows):
            for col in xrange(cols):
                test.append(fck.Point(im[row,col]))
    print "converted to points"

    if len(sys.argv) > 3:
        cluster_count = int(sys.argv[3])
    else:
        cluster_count = fck.sub_clustering(test, 255)
        print "calculated cluster count with subtractive clustering -", cluster_count

    centers = fck.kmpp(test, cluster_count)
    print "calculated centers with k-means++"

    if c_mode:
        results = fcc.simple_C(test, centers, 5*cluster_count)
        print "calculated clusters with c-means"
    else:
        results = fck.simple_K(test, centers)
        print "calculated clusters with k-means"

    test2 = np.array(test).reshape(rows, cols)

    if c_mode:
        for row in xrange(rows):
            for col in xrange(cols):
                cs = test2[row,col].clusters
                s = 0
                for cluster in cs:
                    s += np.multiply(cluster.center, cs[cluster])
                im[row,col] = s
    else:
        for row in xrange(rows):
            for col in xrange(cols):
                im[row,col] = test2[row,col].cluster.center
    print "finished outputting image"

    misc.imsave("result_" + im_name + "_" + sys.argv[1] + "_" + str(cluster_count) + ".png", im)
