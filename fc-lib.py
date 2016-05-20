import numpy


class Point:
  def __init__(self, value):
    self.value = value
    self.cluster = None
    
  def assign_cluster(self, new_cluster):
    if self.cluster:
      print "had cluster", self.cluster
      self.cluster.points.remove(self)
      
    self.cluster = new_cluster
    new_cluster.points.append(self)
    
  def __str__(self):
    return str(self.value)


class Cluster:
  def __init__(self, points=[], center=None):
    self.points = points
    
    if center != None:
      self.center = center
    else:
      self.center = self.compute_center()
    
  def compute_center(self):
    if self.points:
      return sum(p.value for p in self.points) / float(len(self.points))
      #return numpy.mean(self.points)
    else:
      return self.center
    
  def update_center(self):
    old_center = self.center
    self.center = self.compute_center()
    print [p.value for p in self.points]
    print " ", old_center, "->", self.center
    return (old_center != self.center)
    
  def __str__(self):
    return "c: " + str(self.center) #+ ";" + str(self.points)


def wcss(clusters):
  sum = 0
  
  for c in clusters:
    for x in c.points:
      sum += (x - c.center) ** 2
      
  return sum


def simple_K(input, initial_centers):
  clusters = []
  for i in initial_centers:
    clusters.append(Cluster(center=i))
  
  while True:
    # assignment
    print "assignment step"
    for x in input:
      min = (None, numpy.inf)
      for c in clusters:
        dist = (x.value - c.center) ** 2
        print "dist for", c, ":", dist
        if dist < min[1]:
          min = (c, dist)
      print x, "->", min[0]
      x.assign_cluster(min[0])
      print x.cluster, ";", [p.value for p in x.cluster.points]
      
    # update
    print "update step"
    updated = False
    for c in clusters:
      updated = c.update_center() or updated
      print updated
        
    if not updated:
      return clusters
    
test = [Point(1), Point(2), Point(3), Point(4)]
print simple_K(test, [0,5])
  