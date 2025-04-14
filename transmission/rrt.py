import random
import numpy as np
import trimesh
from trimesh.collision import CollisionManager
from scipy.spatial.transform import Rotation as R
import open3d as o3d
from utils import safe_mesh_copy, convert_to_trimesh, as_rotation_matrix
from tqdm import tqdm

STEER_STEPSIZE = 1.0
PATH_STEPSIZE = 1.0
SAMPLING_BIAS = 0.1

class Node:
    def __init__(self, pose, parent=None):
        self.pose = pose  # (x, y, z)(rx, ry, rz)
        self.parent = parent

class Pose:
    def __init__(self, position, rotation_matrix):
        """
        Args:
            position (array-like): [x, y, z] position
            rotation_matrix (np.ndarray): 3x3 rotation matrix
        """
        self.position = np.array(position)
        self.rotation = np.array(rotation_matrix).reshape(3, 3)

    def as_matrix(self):
        """Returns the full 4x4 transformation matrix (SE(3))"""
        T = np.eye(4)
        T[:3, :3] = self.rotation
        T[:3, 3] = self.position
        return T

    def apply_to_mesh(self, mesh):
        mesh_copy = safe_mesh_copy(mesh)
        mesh_copy.rotate(self.rotation, center=mesh_copy.get_center())
        mesh_copy.translate(self.position, relative=False)
        return mesh_copy
    def in_state_transformation(self, mesh):
        mesh.rotate(self.rotation, center=mesh.get_center())
        mesh.translate(self.position, relative=True)
        return mesh
    def __repr__(self):
        pos = np.round(self.position, 2)
        return f"Pose(position={pos.tolist()})"

def check_collision_old(mesh1, enviroment):
    """check for collision between one main mesh and a set of base meshes

    Args:
        mesh1: The main mesh (e.g., Shaft) to check for collisions.
        environment: A list of other meshes (can be Open3D or Trimesh).

    Returns:
        bool: True if a collision is detected, False otherwise.
    """
    # print(type(mesh1))
    checked_meshes = []

    if isinstance(mesh1, trimesh.Trimesh):
        mesh1_checked = mesh1
    if type(mesh1).__name__ == "TriangleMesh":
        mesh1_checked = convert_to_trimesh(mesh1)
    
    else:
        print(f"ERROR: mesh1 must be a Trimesh or Open3D TriangleMesh.\n Currently {type(mesh1)}")
        return None
    for mesh in enviroment:
        if isinstance(mesh, trimesh.Trimesh):
            checked_meshes.append(mesh)
        if type(mesh1).__name__ == "TriangleMesh":
            checked_meshes.append(convert_to_trimesh(mesh))
        else:
            print(f"ERROR:  Enviroment object {i} must be a Trimesh or Open3D TriangleMesh. \n Currently {type(mesh)}")
            return None


    manager = CollisionManager()

    for i, mesh in enumerate(checked_meshes):
        manager.add_object(f"env_{i}", mesh)
    collides, names = manager.in_collision_single(mesh1_checked, return_names=True)
    if collides:
        # print("Collided with:", names)
        pass
    return collides
def check_collision(mesh1, environment, verbose=False):
    mesh1_checked = convert_to_trimesh(mesh1) if isinstance(mesh1, o3d.geometry.TriangleMesh) else mesh1

    for idx, env in enumerate(environment):
        env_checked = convert_to_trimesh(env) if isinstance(env, o3d.geometry.TriangleMesh) else env

        # Quick AABB check first
        if not mesh1_checked.bounds_interleaved.intersects(env_checked.bounds_interleaved):
            continue

        # Triangle-level check
        try:
            if mesh1_checked.is_volume and env_checked.is_volume:
                if mesh1_checked.intersects(env_checked):
                    if verbose:
                        print(f"Collision with volume mesh {idx}")
                    return True
            else:
                # Fallback to point proximity check
                pq = ProximityQuery(env_checked)
                if np.any(pq.signed_distance(mesh1_checked.vertices) < 0):
                    if verbose:
                        print(f"Collision (non-volume mesh) with mesh {idx}")
                    return True
        except Exception as e:
            if verbose:
                print(f"Collision check failed with mesh {idx}: {e}")
            continue

    return False


def pose_distance(p1, p2, w_rot=1.0):
    """
    Computes distance between two Pose objects.
    - Position: Euclidean distance
    - Orientation: angle between rotation matrices (in radians)
    """
    # Positional distance
    dp = np.linalg.norm(p1.position - p2.position)
    
    # Rotational distance (angle between rotation matrices)
    R_diff = p1.rotation.T @ p2.rotation
    angle = np.arccos(np.clip((np.trace(R_diff) - 1) / 2.0, -1.0, 1.0))

    return dp + w_rot * angle
def find_nearest_node(tree, sampled_pose):
    """
    Returns the nearest node in the tree to the sampled pose.
    """
    best_node = None
    min_dist = float('inf')
    
    for node in tree:
        dist = pose_distance(node.pose, sampled_pose)
        if dist < min_dist:
            min_dist = dist
            best_node = node
            
    return best_node
def is_goal_reached(pose, goal_pose, pos_threshold=1.0, rot_threshold=np.deg2rad(15)):
    pos_dist = np.linalg.norm(pose.position - goal_pose.position)

    R_diff = pose.rotation.T @ goal_pose.rotation
    angle = np.arccos(np.clip((np.trace(R_diff) - 1) / 2.0, -1.0, 1.0))

    return pos_dist < pos_threshold and angle < rot_threshold
def steer(from_pose, to_pose, step_size=STEER_STEPSIZE):
    direction = to_pose.position - from_pose.position
    dist = np.linalg.norm(direction)

    if dist < step_size:
        return to_pose  # already close enough

    direction = direction / dist
    new_position = from_pose.position + step_size * direction

    # Interpolate rotation (simple version: reuse from from_pose)
    new_rotation = from_pose.rotation  # or interpolate between matrices

    return Pose(new_position, new_rotation)

def is_path_collision_free(from_pose, to_pose, primary, environment, step_size=PATH_STEPSIZE):
    direction = to_pose.position - from_pose.position
    dist = np.linalg.norm(direction)
    direction = direction / dist
    steps = int(dist / step_size)

    for i in range(1, steps + 1):
        interp_position = from_pose.position + i * step_size * direction
        interp_pose = Pose(interp_position, from_pose.rotation)  # optionally interpolate rotation too
        mesh = interp_pose.apply_to_mesh(primary)
        if check_collision(mesh, environment):
            return False
    return True

def sample_random_point(bounds):
    x = random.uniform(*bounds['x'])
    y = random.uniform(*bounds['y'])
    z = random.uniform(*bounds['z'])
    roll = random.uniform(-np.pi, np.pi)
    pitch = random.uniform(-np.pi, np.pi)
    yaw = random.uniform(-np.pi, np.pi)
    rot_matrix = as_rotation_matrix([roll, pitch, yaw])
    return np.array([x, y, z]), rot_matrix

def sample_biased(bounds, goal, sample_rate=SAMPLING_BIAS):
    if random.random() < sample_rate:
        return goal.position, goal.rotation
    xyz, rot = sample_random_point(bounds)
    return xyz, rot

def rrt_algo(bounds,init_pose, goal ,primary, environment,samples = 1000):

    init_node = Node(init_pose)
    tree = [init_node]

    for _ in tqdm(range(samples), desc="Running RRT"):
        sampled_xyz, rot_matrix = sample_biased(bounds, goal) #return x y z and rx ry rz
        sampled_pose = Pose(sampled_xyz, rot_matrix)
        nearest_node = find_nearest_node(tree, sampled_pose)
        new_pose = steer(nearest_node.pose, sampled_pose)
        sampled_mesh = new_pose.apply_to_mesh(primary)
        if is_path_collision_free(nearest_node.pose, new_pose, primary, environment):
            new_node = Node(sampled_pose, parent=nearest_node)
            tree.append(new_node)
            if is_goal_reached(new_pose, goal):
                print("Goal reached!")
                return extract_path_from_node(new_node)
    print("Goal not reached.")
    return tree


def extract_path_from_node(goal_node):
    path = []
    current = goal_node
    while current:
        path.append(current)
        current = current.parent
    return path[::-1]  # from start to goal
