import trimesh

# Load the .obj file
mesh = trimesh.load_mesh('assets\cube.obj')

# Access the vertex normals
normals = mesh.vertex_normals

# Access the vertices of the mesh
vertices = mesh.vertices

# Access the faces of the mesh
faces = mesh.faces

print(vertices)
print(normals)
print(faces)