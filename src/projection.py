import numpy as np
from constants import r


def generate_great_circle(normal, num_points=100):
    """Generate points along a great circle with given normal."""
    normal = normal / np.linalg.norm(normal)
    if np.allclose(normal, [0, 0, 1]):
        v1 = np.array([1, 0, 0])
    else:
        v1 = np.cross(normal, [0, 0, 1])
        v1 = v1 / np.linalg.norm(v1)
    v2 = np.cross(normal, v1)
    t = np.linspace(0, 2 * np.pi, num_points)
    circle = np.outer(np.cos(t), v1) + np.outer(np.sin(t), v2)
    return circle[:, 0] * r, circle[:, 1] * r, circle[:, 2] * r


def get_rotation_matrices(tilt, roll, pan):
    """Compute rotation matrices from Euler angles."""
    cos_t, sin_t = np.cos(tilt), np.sin(tilt)
    cos_r, sin_r = np.cos(roll), np.sin(roll)
    cos_p, sin_p = np.cos(pan), np.sin(pan)

    Rx = np.array([
        [1, 0, 0],
        [0, cos_t, -sin_t],
        [0, sin_t, cos_t]
    ])
    Ry = np.array([
        [cos_r, 0, sin_r],
        [0, 1, 0],
        [-sin_r, 0, cos_r]
    ])
    Rz = np.array([
        [cos_p, -sin_p, 0],
        [sin_p, cos_p, 0],
        [0, 0, 1]
    ])
    return Rz @ Ry @ Rx


def rotate_sphere_fast(x, y, z, R):
    """Apply rotation matrix to coordinates."""
    coords = np.vstack((x.flatten(), y.flatten(), z.flatten()))
    rotated = R @ coords
    return rotated[0].reshape(x.shape), rotated[1].reshape(y.shape), rotated[2].reshape(z.shape)


def get_projection(x, y, z, r, projection):
    """Project 3D coordinates to 2D based on projection type."""
    if projection == "Orthographic":
        return x, y
    elif projection == "Stereographic":
        with np.errstate(divide='ignore', invalid='ignore'):
            factor = 1.0 / (1 - z / r)
            factor = np.where((1 - z / r) < 0.01, np.nan, factor)
            return x * factor, y * factor
    elif projection == "Azimuthal":
        phi_val = np.arcsin(z / r)
        lambda_val = np.arctan2(y, x)
        phi_0 = np.pi / 2
        lambda_0 = 0
        cos_angle = (
            np.sin(phi_0) * np.sin(phi_val) +
            np.cos(phi_0) * np.cos(phi_val) * np.cos(lambda_val - lambda_0)
        )
        rho = r * np.arccos(cos_angle)
        numerator = np.cos(phi_val) * np.sin(lambda_val - lambda_0)
        denominator = (
            np.cos(phi_0) * np.sin(phi_val) -
            np.sin(phi_0) * np.cos(phi_val) * np.cos(lambda_val - lambda_0)
        )
        theta_az = np.arctan2(numerator, denominator)
        scale = 0.5 * np.pi * r
        return -rho * np.cos(theta_az) / scale, rho * np.sin(theta_az) / scale
    else:
        return x, y
