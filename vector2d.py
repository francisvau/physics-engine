from math import cos, sin, sqrt, radians

class Vector2D:
    def __init__(self, *values):
        if len(values) == 2:
            self.x, self.y = values  # sla x en y op
        elif len(values) == 1:
            self.x, self.y = values[0]
        else:
            self.x, self.y = 0.0, 0.0

    def __add__(self, other):
        if len(self) == len(other):
            return Vector2D(self.x + other[0], self.y + other[1])
        raise ValueError("Vectors must have the same dimension for addition.")

    def __sub__(self, other):
        if len(self) == len(other):
            return Vector2D(self.x - other[0], self.y - other[1])
        raise ValueError("Vectors must have the same dimension for subtraction.")

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x * scalar, self.y * scalar)  # vermenigvuldigen met scalar
        raise TypeError("Multiplication only supports scalars.")

    def __rmul__(self, scalar):
        return self * scalar

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x / scalar, self.y / scalar)  # delen door scalar
        raise TypeError("Division only supports scalars.")

    def __neg__(self):
        return Vector2D(-self.x, -self.y)  # negatieve vector

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

    def length(self):
        return sqrt(self.x**2 + self.y**2)

    def normalize(self):
        vector_length = self.length()
        if vector_length == 0:
            raise ValueError("Cannot normalize a zero-length vector.")
        return Vector2D(self.x / vector_length, self.y / vector_length)  # normaalvector maken

    def rotate(self, angle):
        rad_angle = radians(angle)
        cos_theta = cos(rad_angle)
        sin_theta = sin(rad_angle)
        rotated_x = cos_theta * self.x - sin_theta * self.y
        rotated_y = sin_theta * self.x + cos_theta * self.y
        return Vector2D(rotated_x, rotated_y)  # draai de vector

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x 

    def orthogonal(self):
        return Vector2D(self.y, -self.x)
