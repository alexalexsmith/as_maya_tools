"""
Math utils
"""
import math


class Vector:

    def __init__(self, x=0, y=0, z=0):
        '''
        Initialize the vector with 3 values, or else
        :param float or tuple(float,float,float) x: can pass a tuple for x,y,z vector or single float value
        :param float y: if x is a single float value this value will be used
        :param float z: if x is a single float value this value will be used
        '''

        if self._isCompatible(x):
            x = x[0]
            y = x[1]
            z = x[2]
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return 'Vector({0:.2f}, {1:.2f}, {2:.2f})'.format(*self)

    #iterator methods
    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        [self.x, self.y, self.z][key] = value

    def __len__(self):
        return 3

    def _isCompatible(self, other):
        '''
        Return true if the provided argument is a vector
        '''
        if isinstance(other,(Vector,list,tuple)) and len(other)==3:
            return True
        return False


    def __add__(self, other):

        if not self._isCompatible(other):
            raise TypeError('Can only add to another vector of the same dimension.')

        return Vector(*[a+b for a,b in zip(self,other)])


    def __sub__(self, other):

        if not self._isCompatible(other):
            raise TypeError('Can only subtract another vector of the same dimension.')

        return Vector(*[a-b for a,b in zip(self,other)])


    def __mul__(self, other):

        if self._isCompatible(other):
            return Vector(*[a*b for a,b in zip(self,other)])
        elif isinstance(other, (float,int)):
            return Vector(*[x*float(other) for x in self])
        else:
            raise TypeError("Can't multiply {} with {}".format(self, other))

    def __div__(self, other):
        '''
        Python 2.7
        '''
        if isinstance(other, (float,int)):
            return Vector(*[x/float(other) for x in self])
        else:
            raise TypeError("Can't divide {} by {}".format(self, other))
    
    def __truediv__(self, other):
        '''
        Python 3
        '''
        if isinstance(other, (float,int)):
            return Vector(*[x/float(other) for x in self])
        else:
            raise TypeError("Can't divide {} by {}".format(self, other))

    def magnitude(self):
        return math.sqrt(sum([x**2 for x in self]))


    def normalize(self):
        d = self.magnitude()
        if d:
            self.x /= d
            self.y /= d
            self.z /= d
        return self


    def normalized(self):
        d = self.magnitude()
        if d:
            return self/d
        return self


    def dot(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only perform dot product with another Vector object of equal dimension.')
        return sum([a*b for a,b in zip(self,other)])


    def cross(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only perform cross product with another Vector object of equal dimension.')
        return Vector(self.y * other.z - self.z * other.y,
                       -self.x * other.z + self.z * other.x,
                       self.x * other.y - self.y * other.x)

    def axis_angle(self, other):
        if not self._isCompatible(other):
            raise TypeError('Vectors arent compatible for axis/angle.')
        a = self.normalized()
        b = other.normalized()
        angle = math.acos(a.dot(b))
        axis = a.cross(b)
        return axis,angle