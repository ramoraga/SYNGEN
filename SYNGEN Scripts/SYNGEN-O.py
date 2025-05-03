import bpy
import os
import random
from mathutils import Vector
import gc

""" The purpose of this script is to generate EXR and mask files of our objects from our 
    CAD model dataset in our custom environment. Each render will only contain ONE object"""

# Function to delete any previously used imported STL models

def delete_models():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name.startswith("Imported_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


# Function to reset the object's position, rotation, and animation

def reset_object(imported_object, drop_location):
    imported_object.location = drop_location
    imported_object.rotation_euler = (
        random.uniform(0, 2 * 3.14159),  # Random rotation around the X-axis
        random.uniform(0, 2 * 3.14159),  # Random rotation around the Y-axis
        random.uniform(0, 2 * 3.14159)   # Random rotation around the Z-axis
    )

    # Reset the animation to the start frame
    bpy.context.scene.frame_set(0)


# Function to redefine the origin of the imported object

def redefine_origin(imported_object):

    bpy.context.view_layer.objects.active = imported_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


# Define paths
stl_folder_path = 'C:/Users/dinob/Desktop/CAD Project/CAD Model Dataset/'
stl_files = [f for f in os.listdir(stl_folder_path) if f.lower().endswith('.stl')]

if not stl_files:
    raise ValueError("No STL files found in the specified folder.")

# Define table dimensions for custom environment
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

# Define the object we want to import from our CAD model folder
first_model = stl_files[4]

# Import the selected STL model
file_path = os.path.join(stl_folder_path, first_model)
bpy.ops.import_mesh.stl(filepath=file_path)
imported_object = bpy.context.selected_objects[0]
imported_object.name = f"Imported_{first_model}"

# Move the imported object to the target collection
import_collection.objects.link(imported_object)
bpy.context.scene.collection.objects.unlink(imported_object)  # Unlink from the default scene collection

# Scale the object
bbox = imported_object.dimensions
largest_dim = max(bbox)
scale_factor = 0.27 / largest_dim   # Change scale factor
imported_object.scale = (scale_factor, scale_factor, scale_factor)

# Define drop location
drop_location = (0, 0, table_height + 0.6)

# Assign Rigid Body physics to the object
bpy.context.view_layer.objects.active = imported_object
bpy.ops.rigidbody.object_add()
imported_object.rigid_body.type = 'ACTIVE'
imported_object.rigid_body.mass = 1.0  
imported_object.rigid_body.friction = 0.8  
imported_object.rigid_body.restitution = 0.3 
imported_object.pass_index = 1

# Set drop location
imported_object.location = drop_location
imported_object.rigid_body.collision_shape = 'CONVEX_HULL' 
imported_object.rigid_body.collision_margin = 0.001 

# Ensure to set the table as a passive rigid body
table_object = bpy.data.objects['Table']  
bpy.context.view_layer.objects.active = table_object
bpy.ops.rigidbody.object_add()  
table_object.rigid_body.type = 'PASSIVE'  
table_object.rigid_body.friction = 1  
bpy.context.view_layer.update()

# Change material name
material_name = "resin" 

# Check if the material exists in the Blender environment
if material_name in bpy.data.materials:
    material = bpy.data.materials[material_name]
    
    if imported_object.data.materials:
        imported_object.data.materials.clear()
    
    imported_object.data.materials.append(material)
else:
    print(f"Material '{material_name}' not found in Blender environment.")

# Redefine the origin of the imported object
redefine_origin(imported_object)

# Define the number of frames to simulate, and our camera angles
stop_frame = 25
z_angles = [0, 45, 90, 135, 180, 225, 270, 315] # 8 angles
x_angles = [40, 30, 0, -30, -60, -90]   # 6 angles

# This object contains our camera
empty_object = bpy.data.objects.get('Empty')
if empty_object is None:
    raise ValueError("Object 'Empty' not found in the scene.")

# Start rendering loop
# For each iteration, total number of renders will be num of z angles * num of x_angles
# e.g. 8 angles * 6 angles = 48 renders per iteration. 48 renders * 6 iterations = 288 total renders

for iteration in range(1, 7):   # Change number of iterations
    print(f"\n=== Starting iteration {iteration} ===")

    # Give our object a random position and rotation at our drop location
    reset_object(imported_object, drop_location)

    # Progress through the frames to simulate the object's fall
    for frame in range(stop_frame):
        bpy.context.scene.frame_set(frame)

    # Perform rendering for each combination of Z and X rotation angles
    for x_index, x_angle in enumerate(x_angles, start=1):
        for z_index, z_angle in enumerate(z_angles, start=1):
            print(f"Rendering for X angle: {x_angle}° and Z angle: {z_angle}° in iteration {iteration}")

            # Set the Z and X rotation of the 'Empty' object
            empty_object.rotation_euler[2] = z_angle * (3.14159 / 180) 
            empty_object.rotation_euler[0] = x_angle * (3.14159 / 180) 

            # Update our view
            bpy.context.view_layer.update()
            bpy.context.scene.frame_set(stop_frame)

            # Define output paths w/ class names
            main_output_path = f"C:/Users/dinob/Desktop/CAD Project/Prismatic Geometries/bolt_{iteration}{x_index}{z_index}" # EXR path
            mask_output_path = f"bolt_m{iteration}{x_index}{z_index}"    # Mask path
            
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
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            gc.collect()
    
    gc.collect()

print("All renders for all iterations completed.")
