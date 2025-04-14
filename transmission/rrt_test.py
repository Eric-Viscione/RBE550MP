import open3d as o3d
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation as R
from trimesh.collision import CollisionManager
import random
import time
from tqdm import tqdm

# Helper Functions
def safe_mesh_copy(mesh):
    mesh_copy = o3d.geometry.TriangleMesh()
    mesh_copy.vertices = o3d.utility.Vector3dVector(np.asarray(mesh.vertices))
    mesh_copy.triangles = o3d.utility.Vector3iVector(np.asarray(mesh.triangles))
    mesh_copy.compute_vertex_normals()
    return mesh_copy

def convert_to_trimesh(mesh):
    return trimesh.Trimesh(np.asarray(mesh.vertices), np.asarray(mesh.triangles), process=False)

def rotation_matrix(angles):
    return R.from_euler('xyz', angles).as_matrix()

# Classes
class Pose:
    def __init__(self, position, rotation):
        self.position = np.array(position)
        self.rotation = np.array(rotation).reshape(3, 3)

    def apply_to_mesh(self, mesh):
        mesh_copy = safe_mesh_copy(mesh)
        mesh_copy.rotate(self.rotation, center=mesh_copy.get_center())
        mesh_copy.translate(self.position, relative=False)
        return mesh_copy

class Node:
    def __init__(self, pose, parent=None):
        self.pose = pose
        self.parent = parent

# Collision Checking
def check_collision(mesh, environment):
    manager = CollisionManager()
    mesh_trimesh = convert_to_trimesh(mesh)

    for i, obj in enumerate(environment):
        manager.add_object(f'env_{i}', convert_to_trimesh(obj))

    return manager.in_collision_single(mesh_trimesh)

# RRT Planner Functions
def distance(p1, p2):
    return np.linalg.norm(p1.position - p2.position)

def nearest_node(tree, pose):
    return min(tree, key=lambda node: distance(node.pose, pose))

def steer(from_pose, to_pose, step_size=1.0):
    direction = to_pose.position - from_pose.position
    dist = np.linalg.norm(direction)

    if dist < step_size:
        return to_pose

    new_position = from_pose.position + (direction / dist) * step_size
    return Pose(new_position, from_pose.rotation)

def sample(bounds):
    return np.array([random.uniform(*bounds[axis]) for axis in 'xyz'])

def rrt(start_pose, goal_pose, mesh, environment, bounds, max_iters=5000, step_size=2.0, goal_threshold=5.0):
    tree = [Node(start_pose)]

    for _ in tqdm(range(max_iters), desc="Planning Path"):
        random_pose = Pose(sample(bounds), start_pose.rotation) if random.random() > 0.1 else goal_pose
        nearest = nearest_node(tree, random_pose)
        new_pose = steer(nearest.pose, random_pose, step_size)
        new_mesh = new_pose.apply_to_mesh(mesh)

        if not check_collision(new_mesh, environment):
            new_node = Node(new_pose, nearest)
            tree.append(new_node)

            if distance(new_pose, goal_pose) <= goal_threshold:
                path = []
                current = new_node
                while current:
                    path.append(current.pose)
                    current = current.parent
                return path[::-1]

    return None

# Visualization Functions
def animate(path, mesh, environment, delay=0.02):
    vis = o3d.visualization.Visualizer()
    vis.create_window()

    for obj in environment:
        vis.add_geometry(obj)

    for pose in path:
        mesh_pose = pose.apply_to_mesh(mesh)
        mesh_pose.paint_uniform_color([0.8, 0.2, 0.2])
        vis.add_geometry(mesh_pose)
        vis.update_geometry(mesh_pose)
        vis.poll_events()
        vis.update_renderer()
        time.sleep(delay)

    vis.run()
    vis.destroy_window()

# Main Function
def main():
    bounds = {'x': (-300, 300), 'y': (-50, 50), 'z': (-100, 500)}
    cad_folder = 'RBE550_assignment_transmission_SCAD_files'

    primary_shaft = o3d.io.read_triangle_mesh(f"{cad_folder}/primary_shaft.stl")
    primary_shaft.compute_vertex_normals()
    primary_shaft.translate(-primary_shaft.get_center())

    environment = [o3d.io.read_triangle_mesh(f"{cad_folder}/transmission_without_primary.stl")]

    start_pose = Pose([0, 0, 238], rotation_matrix([0, np.pi / 2, 0]))
    goal_pose = Pose([0, 0, 350], rotation_matrix([0, 0, 0]))

    path = rrt(start_pose, goal_pose, primary_shaft, environment, bounds)

    if path:
        animate(path, primary_shaft, environment)
    else:
        print("Path not found!")

if __name__ == "__main__":
    main()