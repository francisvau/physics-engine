import sys
from math import copysign, inf
import pygame
from vector2d import Vector2D


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None  # lijnen zijn parallel

    d = (det(*line1), det(*line2))
    return Vector2D(det(d, xdiff) / div, det(d, ydiff) / div)


class SquareBody:
    def __init__(self, width, height, x, y, angle=0.0, mass=None, restitution=0.5):
        self.position = Vector2D(x, y)
        self.width, self.height, self.angle = width, height, angle
        self.velocity = Vector2D(0.0, 0.0)
        self.angular_velocity, self.torque = 0.0, 0.0
        self.forces = Vector2D(0.0, 0.0)
        self.mass = mass if mass else width * height
        self.restitution, self.inertia = restitution, self.mass * (width**2 + height**2) / 12

        self.sprite = pygame.Surface((width, height))
        self.sprite.set_colorkey((0, 0, 0))
        pygame.draw.rect(self.sprite, (255, 255, 255), (0, 0, width - 2, height - 2), 2)

    def draw(self, surface):
        self.sprite.fill((200, 200, 200) if self.mass == inf else (0, 0, 0))  # grijs = oneindige massa
        if self.mass != inf:
            pygame.draw.rect(self.sprite, (255, 255, 255), (0, 0, self.width - 2, self.height - 2), 2)
        rotated = pygame.transform.rotate(self.sprite, self.angle)
        surface.blit(rotated, self.position - (rotated.get_rect().width / 2, rotated.get_rect().height / 2))

    def add_world_force(self, force, offset):
        if abs(offset[0]) <= self.width / 2 and abs(offset[1]) <= self.height / 2:
            self.forces += force
            self.torque += offset.cross(force.rotate(self.angle))  # moment opwekken

    def reset(self):
        self.forces, self.torque = Vector2D(0.0, 0.0), 0.0

    def update(self, dt):
        self.velocity += (self.forces / self.mass) * dt  # versnelling toepassen
        self.position += self.velocity * dt
        self.angular_velocity += (self.torque / self.inertia) * dt
        self.angle += self.angular_velocity * dt
        self.reset()

    @property
    def vertices(self):
        return [self.position + Vector2D(v).rotate(-self.angle) for v in (
            (-self.width / 2, -self.height / 2), (self.width / 2, -self.height / 2),
            (self.width / 2, self.height / 2), (-self.width / 2, self.height / 2)
        )]

    @property
    def edges(self):
        return [Vector2D(v).rotate(self.angle) for v in (
            (self.width, 0), (0, self.height), (-self.width, 0), (0, -self.height)
        )]

    def collide(self, other):
        if (self.position - other.position).length() > max(self.width, self.height) + max(other.width, other.height):
            return False, None, None  # geen botsing, bodies te ver

        def project(vertices, axis):
            dots = [vertex.dot(axis) for vertex in vertices]
            return Vector2D(min(dots), max(dots))

        collision_depth, collision_normal = sys.maxsize, None
        for edge in self.edges + other.edges:
            axis = Vector2D(edge).orthogonal().normalize()
            proj1, proj2 = project(self.vertices, axis), project(other.vertices, axis)
            overlap = min(max(proj1), max(proj2)) - max(min(proj1), min(proj2))
            if overlap < 0:
                return False, None, None  # geen overlap op deze as
            if overlap < collision_depth:
                collision_depth, collision_normal = overlap, axis
        return True, collision_depth, collision_normal

    def get_collision_edge(self, normal):
        max_projection, support_point = -sys.maxsize, None
        for i, vertex in enumerate(self.vertices):
            projection = vertex.dot(normal)
            if projection > max_projection:
                max_projection, support_point = projection, vertex
                left_vertex, right_vertex = self.vertices[i - 1], self.vertices[(i + 1) % len(self.vertices)]
        return (right_vertex, support_point) if right_vertex.dot(normal) > left_vertex.dot(normal) else (support_point, left_vertex)


class PhysicsWorld:
    def __init__(self, gravity=9.8):
        self.bodies, self.gravity = [], gravity

    def add(self, *bodies):
        self.bodies.extend(bodies)  # bodies toevoegen

    def remove(self, body):
        self.bodies.remove(body)

    def update(self, dt):
        tested = []
        for body in self.bodies:
            if body.mass != inf:
                body.add_world_force(Vector2D(0, body.mass * self.gravity), Vector2D(0, 0))  # zwaartekracht toepassen

            for other_body in self.bodies:
                if other_body not in tested and other_body is not body:
                    collision, depth, normal = body.collide(other_body)
                    if collision:
                        normal = normal.normalize()
                        rel_vel = body.velocity - other_body.velocity
                        j = -(1 + body.restitution) * rel_vel.dot(normal) / normal.dot(
                            normal * (1 / body.mass + 1 / other_body.mass))

                        direction, magnitude = body.position - other_body.position, normal.dot(body.position - other_body.position)
                        if body.mass != inf:
                            body.position += normal * depth * copysign(1, magnitude)
                        if other_body.mass != inf:
                            other_body.position -= normal * depth * copysign(1, magnitude)

                        body.velocity += j / body.mass * normal
                        other_body.velocity -= j / other_body.mass * normal

                        contact_point = line_intersection(
                            body.get_collision_edge(-direction), other_body.get_collision_edge(direction)
                        )
                        if contact_point:
                            for b, factor in ((body, 1), (other_body, -1)):
                                radius = b.position - contact_point
                                b.angular_velocity += factor * radius.dot(j * normal / b.inertia)

            tested.append(body)
            body.update(dt)
