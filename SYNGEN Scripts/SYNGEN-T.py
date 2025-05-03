import bpy
import os
import random
from mathutils import Vector
import gc

""" The purpose of this script is to generate EXR and mask files of our objects from our 
    CAD model dataset in our custom environment. Each render will only contain TWO objects.
    One is an object of interest (bolt, tshape, yoke), the other is an object that will be
    blocking a portion of the object of interest from the camera view"""

# Function to delete any previously used imported STL models

def delete_models():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name.startswith("Imported_"):
            bpy.data.objects.remove(obj, do_unlink=True)
            print("Objects delete.")
            
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


# Function to reset the object's position, rotation, and animation

def reset_object_and_animation(imported_object, drop_location):
    imported_object.location = drop_location
    imported_object.rotation_euler = (
        random.uniform(0, 2 * 3.14159),  # Random rotation around the X-axis
        random.uniform(0, 2 * 3.14159),  # Random rotation around the Y-axis
        random.uniform(0, 2 * 3.14159)   # Random rotation around the Z-axis
    )
    bpy.context.scene.frame_set(0)
    print("Rotation and animation reset.")


# Function to redefine the origin of the imported object

def redefine_origin(imported_object):
    bpy.context.view_layer.objects.active = imported_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Define CAD model folder paths
stl_folder_path = 'C:/Users/dinob/Desktop/CAD Project/CAD Model Dataset/'
stl_files = [f for f in os.listdir(stl_folder_path) if f.lower().endswith('.stl')]

if not stl_files:
    raise ValueError("No STL files found in the specified folder.")

# Define custom table dimensions
table_length = 1.12
table_width = 0.816
table_height = 0.6

# Create or retrieve the collection for imported models
collection_name = "Scene Collection"
if collection_name in bpy.data.collections:
    import_collection = bpy.data.collections[collection_name]
else:
    import_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(import_collection)

# Delete previous STL models
delete_models()
gc.collect()

# Import and configure the first STL model (object of interest)
first_model = stl_files[1]
file_path = os.path.join(stl_folder_path, first_model)
bpy.ops.import_mesh.stl(filepath=file_path)
imported_object = bpy.context.selected_objects[0]
imported_object.name = f"Imported_{first_model}"
import_collection.objects.link(imported_object)
bpy.context.scene.collection.objects.unlink(imported_object)

# Define dimensions of first object
bbox = imported_object.dimensions
largest_dim = max(bbox)
scale_factor = 0.27 / largest_dim   # Change scale factor
imported_object.scale = (scale_factor, scale_factor, scale_factor)

# Define drop location of first object
drop_location = (0, 0, table_height + 0.6)
imported_object.location = drop_location

# Define rigid body physics for first object
bpy.context.view_layer.objects.active = imported_object
bpy.ops.rigidbody.object_add()
imported_object.rigid_body.type = 'ACTIVE'
imported_object.rigid_body.mass = 1.0
imported_object.rigid_body.friction = 0.5
imported_object.rigid_body.restitution = 0.1
imported_object.rigid_body.collision_shape = 'CONVEX_HULL'
imported_object.rigid_body.collision_margin = 0.001

# Define pass index for masking
imported_object.pass_index = 1

# Change material name
material_name = "resin"
if material_name in bpy.data.materials:
    material = bpy.data.materials[material_name]
    if imported_object.data.materials:
        imported_object.data.materials.clear()
    imported_object.data.materials.append(material)
else:
    print(f"Material '{material_name}' not found in Blender environment.")

# Redefine the origin of the first object
redefine_origin(imported_object)

# Import and configure the second STL model at random
second_model_index = random.choice([0, 3, 4])
second_model = stl_files[second_model_index]
second_file_path = os.path.join(stl_folder_path, second_model)
bpy.ops.import_mesh.stl(filepath=second_file_path)
imported_object_2 = bpy.context.selected_objects[0]
imported_object_2.name = f"Imported_{second_model}"
import_collection.objects.link(imported_object_2)
bpy.context.scene.collection.objects.unlink(imported_object_2)

# Set dimensions of second object
bbox_2 = imported_object_2.dimensions
largest_dim_2 = max(bbox_2)

# Different models will have different scale factors.
# This IF THEN statement accomodates for that
if second_model_index == 4:
    scale_factor_2 = 0.27 / largest_dim_2
else:
    scale_factor_2 = 0.15 / largest_dim_2

imported_object_2.scale = (scale_factor_2, scale_factor_2, scale_factor_2)

# Randomize the second drop location
random_x = random.choice([0.1, -0.1])
random_y = random.choice([0.1, -0.1])
drop_location_2 = (random_x, random_y, table_height + 1)
imported_object_2.location = drop_location_2

# Apply physics to second object
bpy.context.view_layer.objects.active = imported_object_2
bpy.ops.rigidbody.object_add()
imported_object_2.rigid_body.type = 'ACTIVE'
imported_object_2.rigid_body.mass = 1.0
imported_object_2.rigid_body.friction = 0.5
imported_object_2.rigid_body.restitution = 0.1
imported_object_2.rigid_body.collision_shape = 'CONVEX_HULL'
imported_object_2.rigid_body.collision_margin = 0.001

# Change pass index for masking
imported_object_2.pass_index = 9

# Apply material
if material_name in bpy.data.materials:
    if imported_object_2.data.materials:
        imported_object_2.data.materials.clear()
    imported_object_2.data.materials.append(material)
else:
    print(f"Material '{material_name}' not found in Blender environment.")

# Redefine the origin of the second object
redefine_origin(imported_object_2)

# Update view
bpy.context.view_layer.update()
print("Both models imported and configured successfully.")

# Change total frames and our camera angles
stop_frame = 25
z_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]   # 16 angles
x_angles = [45, 30, 15, 0, -60, -90, -120]  # 7 angles

# Get camera object from scene
empty_object = bpy.data.objects.get('Empty')
if empty_object is None:
    raise ValueError("Object 'Empty' not found in the scene.")

# Start rendering loop
# For each iteration, total number of renders will be num of z angles * num of x_angles
# e.g. 16 angles * 7 angles = 112 renders per iteration. 112 renders * 5 iterations = 560 total renders

for iteration in range(1, 6):  # Adjust number of iterations as needed
    print(f"\n=== Starting iteration {iteration} ===")

    # Reset the objects' positions and rotations
    reset_object_and_animation(imported_object, drop_location)
    reset_object_and_animation(imported_object_2, drop_location_2)

    # Progress through the frames to simulate the object's fall
    for frame in range(stop_frame):
        bpy.context.scene.frame_set(frame)

    # Perform rendering for each combination of Z and X rotation angles
    for x_index, x_angle in enumerate(x_angles, start=1):
        for z_index, z_angle in enumerate(z_angles, start=1):
            print(f"Rendering for X angle: {x_angle}° and Z angle: {z_angle}° in iteration {iteration}")

            # Set the Z and X rotation of the camera object
            empty_object.rotation_euler[2] = z_angle * (3.14159 / 180)
            empty_object.rotation_euler[0] = x_angle * (3.14159 / 180)

            # Update view
            bpy.context.view_layer.update()
            bpy.context.scene.frame_set(stop_frame)

            # Define output paths w/ class names
            main_output_path = f"C:/Users/dinob/Desktop/CAD Project/Prismatic Geometries/bolt_{iteration}{x_index}{z_index}"    # EXR file
            mask_output_path = f"bolt_m{iteration}{x_index}{z_index}"    # Mask file
            
            # Set paths for each output node
            node_tree = bpy.context.scene.node_tree
            for node in node_tree.nodes:
                if node.type == 'OUTPUT_FILE':
                    if node.name == "MainOutput":
                        node.base_path = main_output_path
                    elif node.name == "MaskOutput":
                        node.file_slots[0].path = mask_output_path

            # Render the scene (the compositing nodes will handle output)
            bpy.ops.render.render(write_still=False)

            # Release memory after each render
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            gc.collect()

    gc.collect()

print("All renders for all iterations completed.")