import numpy as np
from scipy import misc
import fc_lib_kmean as fc

if __name__ == '__main__':
    im = misc.imread("testing_mini.png")
    print "loaded image"

    rows, cols = im.shape[:2]

    test = []
    for row in xrange(rows):
        for col in xrange(cols):
            test.append(fc.Point(im[row,col]))
    print "converted to points"

    centers = fc.kmpp(test, 4)
    print "calculated centers with k-means++"

    results = fc.simple_K(test, centers)
    print "calculated clusters with k-means"

    test2 = np.array(test).reshape(rows, cols)

    for row in xrange(rows):
        for col in xrange(cols):
            im[row,col] = test2[row,col].cluster.center
    print "finished outputting image"

    misc.imsave("result.png", im)
