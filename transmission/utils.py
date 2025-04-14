import open3d as o3d
import numpy as np
from scipy.spatial.transform import Rotation as R
import trimesh

def safe_mesh_copy(mesh):
    mesh_copy = o3d.geometry.TriangleMesh()
    mesh_copy.vertices = o3d.utility.Vector3dVector(np.asarray(mesh.vertices))
    mesh_copy.triangles = o3d.utility.Vector3iVector(np.asarray(mesh.triangles))

    if mesh.has_vertex_normals():
        mesh_copy.vertex_normals = o3d.utility.Vector3dVector(np.asarray(mesh.vertex_normals))
    if mesh.has_vertex_colors():
        mesh_copy.vertex_colors = o3d.utility.Vector3dVector(np.asarray(mesh.vertex_colors))

    return mesh_copy   
def convert_to_trimesh(open_mesh):
    vertices = np.asarray(open_mesh.vertices)
    faces = np.asarray(open_mesh.triangles)
    trimesh_mesh = trimesh.Trimesh(vertices, faces, process=False)

    return trimesh_mesh
def as_rotation_matrix(rotations):
    rot = R.from_euler('xyz', [rotations[0], rotations[1], rotations[2]])
    rotation_matrix = rot.as_matrix()
    return rotation_matrix

