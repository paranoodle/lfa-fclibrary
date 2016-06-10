from fc_lib_cmean import *
from fc_lib_kmean import kmpp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

if __name__ == '__main__':
    test, ids =  csv2array("dataset/iris.data")
    print len(ids)

    centers =  kmpp(test, 3)

    results = simple_C(test, centers, True)


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


    print "len(points): %i" % len(results[0].points)
    print "len(points): %i" % len(results[1].points)
    print "len(points): %i" % len(results[2].points)

    def getClusterSpecy(points, values):
        matches = [0,0,0]
        i = 0
        for v in values:
            for coord in points:
                point = [coord.value[0], coord.value[1], coord.value[2], coord.value[3]]

                if (point == test[i][:4]).all():
                    matches[i/50] += 1
            i += 1

        return max(enumerate(matches), key=lambda x: x[1])[0]


    cluster_ids = []
    cluster_ids.append(getClusterSpecy(results[0].points, test))
    cluster_ids.append(getClusterSpecy(results[1].points, test))
    cluster_ids.append(getClusterSpecy(results[2].points, test))
    print cluster_ids

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for n in range(3):
        for v in test[50*cluster_ids[n]:50*(cluster_ids[n]+1)]:
            color = "red"
            for coord in results[n].points:
                point = [round(coord.value[0], 1), round(coord.value[1], 1), round(coord.value[2], 1), round(coord.value[3], 1)]

                if (point == v[:4]).all():
                    color = "blue"
                    break

            ax.scatter(v[0], v[1], v[2], c=color)

    ax.set_xlabel('sepal length')
    ax.set_ylabel('sepal width')
    ax.set_zlabel('petal length')

    plt.show()
