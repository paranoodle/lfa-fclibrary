import numpy as np
from scipy import misc
import fc_lib_kmean as fck
import fc_lib_cmean as fcc

if __name__ == '__main__':
    im = misc.imread("testing_mini.png")
    print "loaded image"

    rows, cols = im.shape[:2]

    test = []
    for row in xrange(rows):
        for col in xrange(cols):
            test.append(fcc.FuzzyPoint(im[row,col]))
    print "converted to points"

    # cluster_count = fc.sub_clustering(test, 255)
    # print "calculated cluster count with subtractive clustering -", cluster_count

    # centers = fc.kmpp(test, cluster_count)
    centers = fck.kmpp(test, 16)
    print "calculated centers with k-means++"

    results = fcc.simple_C(test, centers, 20)
    print "calculated clusters with c-means"

    test2 = np.array(test).reshape(rows, cols)

    for row in xrange(rows):
        for col in xrange(cols):
            cs = test2[row,col].clusters
            s = 0
            for cluster in cs:
                s += np.multiply(cluster.center, cs[cluster])
            im[row,col] = s
    print "finished outputting image"
    misc.imsave("result.png", im)

    # results = fc.simple_K(test, centers)
    # print "calculated clusters with k-means"
    #
    # test2 = np.array(test).reshape(rows, cols)
    #
    # for row in xrange(rows):
    #     for col in xrange(cols):
    #         im[row,col] = test2[row,col].cluster.center
    # print "finished outputting image"
    #
    # misc.imsave("result.png", im)
