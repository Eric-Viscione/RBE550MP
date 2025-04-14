import open3d as o3d
import numpy as np
import trimesh
from trimesh.collision import CollisionManager
from random import random
import math
import time
import matplotlib.pyplot as plt 
from rrt import check_collision, Pose, rrt_algo, Node
from utils import safe_mesh_copy, convert_to_trimesh, as_rotation_matrix
from scipy.spatial.transform import Rotation as R

colors = [
    (1, 0, 0),       # Red
    (0, 1, 0),       # Green
    (0, 0, 1),       # Blue
    (1, 1, 0),       # Yellow
    (1, 0, 1),       # Magenta
    (0, 1, 1),       # Cyan
    (1, 0.5, 0),     # Orange
    (0.5, 0, 0.5),   # Purple
    (0.5, 0.5, 0.5), # Gray
    (0.6, 0.3, 0),   # Brown
    (0, 0, 0),       # Black
    (0.8, 0.8, 0.8), # Light Gray
    (0, 0.5, 0),     # Dark Green
    (0, 0, 0.5),     # Dark Blue
    (0.5, 0, 0),     # Dark Red
]


def format_point(unformatted_point):
    return np.round(unformatted_point, 0)


def load_mesh_trimesh(file_path):
    return trimesh.load_mesh(file_path)

def load_mesh_open3d(filepath, color=[1, 0, 0]):
    if color == [1,0,0]:
        color = [random(), random(), random()]
    mesh = o3d.io.read_triangle_mesh(filepath)
    mesh.compute_vertex_normals()
    mesh.paint_uniform_color(color)

    return mesh


def build_rrt_lines(tree):
    points = []
    lines = []

    point_idx = {}  # Map Node -> point index
    idx = 0

    for node in tree:
        p = node.pose.position
        points.append(p)
        point_idx[node] = idx
        idx += 1

    for node in tree:
        if node.parent:
            lines.append([point_idx[node.parent], point_idx[node]])

    return points, lines
def create_rrt_lineset(points, lines, color=[0, 0, 1]):
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(np.array(points))
    line_set.lines = o3d.utility.Vector2iVector(np.array(lines))
    line_set.colors = o3d.utility.Vector3dVector([color] * len(lines))
    return line_set
def move_sin_wave(num_points):
    path = []
    for i in range(num_points):
        z = 0* math.sin(0*2)
        point = [0.0,0.0, z]
        path.append(point)
    return path
def plot_path(path):
    x_values = [point[0] for point in path]
    y_values = [point[1] for point in path]
    z_values = [point[2] for point in path]

    fig, ax = plt.subplots()
    ax.plot(z_values, label='z')
    ax.plot(x_values, label='x')
    ax.legend()
    plt.axis('equal')
    plt.show()
def animate(path, mesh1, enviroment, vis, delay=0.05, debug_plot=False):
    nodes = False

    if path is None:
        path = [mesh1.get_center()]
    elif  isinstance(path, list) and isinstance(path[0], Pose):
        nodes = True

    if debug_plot:
        plot_path(path)
    # print(path)

    for i, point in enumerate(path):
        mesh_copy = safe_mesh_copy(mesh1)
        

        # mesh_copy.vertices = o3d.utility.Vector3dVector(np.asarray(mesh1.vertices))
        # mesh_copy.triangles = o3d.utility.Vector3iVector(np.asarray(mesh1.triangles))
        # mesh_copy.compute_vertex_normals()
        # mesh_copy = safe_mesh_copy(mesh1)

        if nodes:
            if point == path[0]:
                 mesh_copy = safe_mesh_copy(mesh1)
            else:
                mesh_copy = point.apply_to_mesh(mesh_copy)
        else: 
            current_center = mesh_copy.get_center()
            target_position = np.array(point)
            delta = target_position - current_center
            mesh_copy.translate(delta, relative=True)

        if i == len(path) - 1:
            mesh_copy.paint_uniform_color([1, 1, 0])  # Yellow for final point
        # if check_collision(mesh_copy, enviroment):
        #     mesh_copy.paint_uniform_color([0,0,0])
        #     # print("In Collision")
        # else:
        #     mesh_copy.paint_uniform_color([1,0.5,0.5])
        else:
            mesh_copy.paint_uniform_color(colors[i])
        vis.add_geometry(mesh_copy)
        vis.update_geometry(mesh_copy)
        vis.poll_events()
        vis.update_renderer()
        time.sleep(delay)

def animate_path(mesh, path, static_mesh, delay=0.05):
    vis = o3d.visualization.Visualizer()
    vis.create_window()

    # Add static mesh only once
    vis.add_geometry(static_mesh)

    # Copy the mesh for animation
    moving_mesh = safe_mesh_copy(mesh)
    vis.add_geometry(moving_mesh)

    for pose in path:
        transformed_mesh = pose.apply_to_mesh(mesh)

        moving_mesh.vertices = transformed_mesh.vertices
        moving_mesh.triangles = transformed_mesh.triangles
        moving_mesh.vertex_normals = transformed_mesh.vertex_normals

        vis.update_geometry(moving_mesh)
        vis.poll_events()
        vis.update_renderer()

        time.sleep(delay)

    # Keep the window open until manually closed
    print("Animation done. Close the visualization window to exit.")
    vis.run()  # keeps the window open
    vis.destroy_window()

def main():
    case_thickness = 25
    case_length = 280
    case_width = 210
    case_height = 300
    bounds_x = (case_length/2)+150 
    bounds = {
    'x': (-150, 150),
    'y': (-10, 10),
    'z': (-100, 500)
    }
    cad_folder = 'RBE550_assignment_transmission_SCAD_files'
    filename_full_case = f"{cad_folder}/transmission_without_primary.stl"
    filename_primary_shaft = f"{cad_folder}/primary_shaft.stl"

    primary_shaft = load_mesh_open3d(filename_primary_shaft)
    primary_shaft.scale(0.8, center=primary_shaft.get_center())
    full_case = load_mesh_open3d(filename_full_case)

#facing from side, x is in horizontal in plane, y is out of plane laterally, z is in plane vertically 

    sphere = o3d.geometry.TriangleMesh.create_box(width=1.0, height=500.0, depth=100.0)
    sphere.compute_vertex_normals()
    sphere.paint_uniform_color([0,0,0])
    primary_shaft.translate(-primary_shaft.get_center())

    R = as_rotation_matrix([0, np.pi/2, 0])
    # R = as_rotation_matrix([0,0,0])
    # print(R)
    position = np.array([0, 0, 238])
    # position = np.array([0,0,0])
    
    init_pose = Pose(position, R)
    primary_shaft = init_pose.apply_to_mesh(primary_shaft)
    primary_shaft.compute_vertex_normals()



    goal_pose = Pose(position=[0,0, 350], rotation_matrix=np.eye(3))
    


    tree = rrt_algo(bounds, init_pose, goal_pose, primary_shaft, [full_case])
    print(len(tree))
    # print([node.pose.position for node in tree])
    # print([node.pose.rotation for node in tree ])
    points, lines = build_rrt_lines(tree)
    line_set = create_rrt_lineset(points, lines)
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(full_case)
    vis.add_geometry(line_set)
    # vis.add_geometry(primary_shaft)
    poses = [node.pose for node in tree]
    # animate_path(primary_shaft, poses, full_case)
    animate(poses, primary_shaft ,[full_case],vis, delay=0.5)
    vis.run()
    vis.destroy_window()

if __name__ == "__main__":
    main()