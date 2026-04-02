"""
Math utils
"""
import math
from maya.api import OpenMaya


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

    # iterator methods
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
        if isinstance(other, (Vector, list, tuple)) and len(other) == 3:
            return True
        return False

    def __add__(self, other):

        if not self._isCompatible(other):
            raise TypeError('Can only add to another vector of the same dimension.')

        return Vector(*[a + b for a, b in zip(self, other)])

    def __sub__(self, other):

        if not self._isCompatible(other):
            raise TypeError('Can only subtract another vector of the same dimension.')

        return Vector(*[a - b for a, b in zip(self, other)])

    def __mul__(self, other):

        if self._isCompatible(other):
            return Vector(*[a * b for a, b in zip(self, other)])
        elif isinstance(other, (float, int)):
            return Vector(*[x * float(other) for x in self])
        else:
            raise TypeError("Can't multiply {} with {}".format(self, other))

    def __div__(self, other):
        '''
        Python 2.7
        '''
        if isinstance(other, (float, int)):
            return Vector(*[x / float(other) for x in self])
        else:
            raise TypeError("Can't divide {} by {}".format(self, other))

    def __truediv__(self, other):
        '''
        Python 3
        '''
        if isinstance(other, (float, int)):
            return Vector(*[x / float(other) for x in self])
        else:
            raise TypeError("Can't divide {} by {}".format(self, other))

    def magnitude(self):
        return math.sqrt(sum([x ** 2 for x in self]))

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
            return self / d
        return self

    def dot(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only perform dot product with another Vector object of equal dimension.')
        return sum([a * b for a, b in zip(self, other)])

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
        return axis, angle


def lerp_matrix(matrix_a, matrix_b, lerp_value):
    """
    haha you want to lerp a matrix. ok I will do. Matrix is decoupled, lerped, then recoupled
    """

    a = OpenMaya.MMatrix(matrix_a)
    b = OpenMaya.MMatrix(matrix_b)

    a_translation, a_rotation, a_scale, a_shear = decouple_position_matrix(a)

    b_translation, b_rotation, b_scale, b_shear = decouple_position_matrix(b)

    lerp_translation = lerp(a_translation, b_translation, lerp_value)
    lerp_rotation = OpenMaya.MQuaternion.slerp(a_rotation, b_rotation, lerp_value)
    lerp_scale = lerp(a_scale, b_scale, lerp_value)

    # I am using a_shear as is because lerping the shear could cause issues. you want shear to be 0,0,0
    lerped_matrix = recouple_position_matrix(lerp_translation, lerp_rotation, lerp_scale, a_shear)

    return lerped_matrix


def lerp(a, b, t):
    """
    lerp between 2 tuples
    :param tuple a: first vector
    :param tuple b: second vector
    :param float t: float value to lerp to
    """
    av = OpenMaya.MVector(*a)
    bv = OpenMaya.MVector(*b)
    return (1 - t) * av + (t * bv)


def decouple_position_matrix(om_matrix):
    """
    :param om_matrix: OpenMaya MMatrix object
    decouple a position matrix into translation, rotation, scale and shear
    """
    om_transform = OpenMaya.MTransformationMatrix(om_matrix)
    translation = om_transform.translation(OpenMaya.MSpace.kWorld)
    rotation = om_transform.rotation(asQuaternion=True)
    scale = om_transform.scale(OpenMaya.MSpace.kWorld)
    shear = om_transform.shear(OpenMaya.MSpace.kTransform)

    return translation, rotation, scale, shear


def recouple_position_matrix(translation, rotation, scale, shear):
    """
    recouple a position matrix
    return OpenMaya.MMatrix object
    """
    recoupled_position_transform = OpenMaya.MTransformationMatrix()
    recoupled_position_transform.setTranslation(translation, OpenMaya.MSpace.kWorld)
    recoupled_position_transform.setRotation(rotation)
    recoupled_position_transform.setScale(scale, OpenMaya.MSpace.kWorld)
    recoupled_position_transform.setShear(shear, OpenMaya.MSpace.kTransform)

    recoupled_position_matrix = recoupled_position_transform.asMatrix()
    return recoupled_position_matrix
