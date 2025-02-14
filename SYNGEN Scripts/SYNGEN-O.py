import bpy
import os
import random
from mathutils import Vector
import gc

# Function to delete only the imported STL models
def delete_existing_stl_models():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name.startswith("Imported_"):
            bpy.data.objects.remove(obj, do_unlink=True)
    # Clean orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


# Function to reset the object's position, rotation, and animation
def reset_object_and_animation(imported_object, drop_location):
    # Reset the object's position and random rotation for a new drop
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

# Set the path to folder containing STL models
stl_folder_path = 'C:/Users/dinob/Desktop/CAD Project/CAD Model Dataset/'
stl_files = [f for f in os.listdir(stl_folder_path) if f.lower().endswith('.stl')]

if not stl_files:
    raise ValueError("No STL files found in the specified folder.")

# Table dimensions
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
delete_existing_stl_models()
gc.collect()

# Select the STL file to import
first_model = stl_files[3]

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
scale_factor = 0.15 / largest_dim
imported_object.scale = (scale_factor, scale_factor, scale_factor)

# Set the object's location to the center of the table (x = 0, y = 0)
drop_location = (0, 0, table_height + 0.6)

# Assign Rigid Body physics to the object
bpy.context.view_layer.objects.active = imported_object
bpy.ops.rigidbody.object_add()
imported_object.rigid_body.type = 'ACTIVE'
imported_object.rigid_body.mass = 1.0  
imported_object.rigid_body.friction = 0.8  
imported_object.rigid_body.restitution = 0.3 
imported_object.pass_index = 1

# Set the initial position above the table
imported_object.location = drop_location

imported_object.rigid_body.collision_shape = 'CONVEX_HULL' 
imported_object.rigid_body.collision_margin = 0.001 

# Ensure to set the table as a passive rigid body
table_object = bpy.data.objects['Table']  
bpy.context.view_layer.objects.active = table_object
bpy.ops.rigidbody.object_add()  
table_object.rigid_body.type = 'PASSIVE'  
table_object.rigid_body.friction = 1  

# Update the scene
bpy.context.view_layer.update()

# Apply an existing material to the imported object
material_name = "resin" 

# Check if the material exists in the Blender environment
if material_name in bpy.data.materials:
    material = bpy.data.materials[material_name]
    
    # If the object already has materials, clear them
    if imported_object.data.materials:
        imported_object.data.materials.clear()
    
    # Assign the existing material to the object
    imported_object.data.materials.append(material)
else:
    print(f"Material '{material_name}' not found in Blender environment.")

# Redefine the origin of the imported object
redefine_origin(imported_object)

# Set the frame number when the animation should stop
stop_frame = 25

# List of rotation angles
z_angles = [0, 45, 90, 135, 180, 225, 270, 315]
x_angles = [40, 30, 0, -30, -60, -90]

empty_object = bpy.data.objects.get('Empty')

if empty_object is None:
    raise ValueError("Object 'Empty' not found in the scene.")

# Repeat the process
for iteration in range(1, 5):
    print(f"\n=== Starting iteration {iteration} ===")

    # Reset the object's random position and rotation
    reset_object_and_animation(imported_object, drop_location)

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

            # Update the scene before rendering
            bpy.context.view_layer.update()

            # Set the frame to the last one and render
            bpy.context.scene.frame_set(stop_frame)

            # Specify the output path for each combination of Z and X angle renders
            main_output_path = f"C:/Users/dinob/Desktop/CAD Project/Prismatic Geometries/null_{iteration}{x_index}{z_index}"
            mask_output_path = f"null_m{iteration}{x_index}{z_index}"
            
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
