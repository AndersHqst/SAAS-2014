

class Entropy():

  @classmethod
  def maxent_est(self, s1, s2, s3, s12, s23, s13, m):

    a = s1/m
    # print 'a', a
    b = s2/m
    # print b
    c = s3/m
    # print c

    ab = s12/m
    # print ab
    bc = s23/m
    # print bc
    ac = s13/m
    # print ac
    
    # lowest and highest possible triple frequency, based on what we have observed.
    low = max( ab+ac-a, ab+bc-b, ac+bc-c )
    high = min ( ab, ac, bc, 1-a-b-c+ab+ac+bc )
    # print 'high', 1-a-b-c+ab+ac+bc 
    est = (ab*bc*ac)/(a*b*c)

    if (est > high): 
      # print 'est > high', (est, low, high)
      return high*m 
    elif (est < low): 
      # print 'est < high', (est, low, high)
      return low*m 
    else: 
      # print 'else ', (est, low, high)
      return est*m

  # from triples.py
  @classmethod
  def maxent_est_rosa(self, s1, s2, s3, s12, s23, s13, m, num=20):
    """
    estimate number of occurences based on rosas max entropy method
    """
    m = float(m)
    a = s1/m
    b = s2/m
    c = s3/m
    ab = s12/m
    bc = s23/m
    ac = s13/m
    
    # lowest and highest possible triple frequency, based on what we have observed.
    low = max( ab+ac-a, ab+bc-b, ac+bc-c, 0  )
    high = min ( ab, ac, bc, 1-a-b-c+ab+ac+bc )
    
    x = 0.0
    for i in range(num):
      x = low + (high-low)/2
      eprod = (a-ab-ac+x)*(b-ab-bc+x)*(c-ac-bc+x)*x
      oprod = (ac-x)*(ab-x)*(bc-x)*(1-a-b-c+ab+ac+bc-x)
      if (eprod > oprod):
        high = low + (high-low)/2
      else:
        low = low + (high-low)/2

    return x*m



# test
# print Entropy().maxent_est_rosa(3000, 3000, 3000,  50,  50, 50, 10000., 20) #* ((20811350)/200000.)

# Hvis ex s3 er meget h0j, vil det presse estimatet ned
                      # (4579, 118, 2292, 15, 200, 27, 1)      

# print Entropy().maxent_est(1500, 1500, 1500, 15, 15, 15, 1000000.)