import bpy
import random 
import gc
from mathutils import Vector 

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
def reset_object_and_animation(obj, drop_location):
    obj.location = drop_location
    obj.rotation_euler = (
        random.uniform(0, 2 * 3.14159),
        random.uniform(0, 2 * 3.14159),
        random.uniform(0, 2 * 3.14159)
    )
    bpy.context.scene.frame_set(0)

delete_existing_stl_models()

# Table dimensions
table_height = 0.6 

# Ensure the 'Table' object exists in the scene
table_object = bpy.data.objects.get('Table')
if table_object is None:
    raise ValueError("Object 'Table' not found in the scene.")

# Ensure the 'Empty' object exists for camera rotation
empty_object = bpy.data.objects.get('Empty')
if empty_object is None:
    raise ValueError("Object 'Empty' not found in the scene.")

# Set the drop location above the table
drop_location = (0, 0, table_height + 0.6)

# Set physics properties for the table
bpy.context.view_layer.objects.active = table_object
bpy.ops.rigidbody.object_add()
table_object.rigid_body.type = 'PASSIVE'
table_object.rigid_body.friction = 1

# Set the frame number when the animation should stop
stop_frame = 25

# Rotation angles for rendering
z_angles = [0, 45, 90, 135, 180, 225, 270, 315]
x_angles = [40, 30, 0, -30, -60, -90]

# Rendering process
for iteration in range(1, 6):
    print(f"\n=== Starting iteration {iteration} ===")

    # Ensure scene updates
    bpy.context.view_layer.update()

    for x_index, x_angle in enumerate(x_angles, start=1):
        for z_index, z_angle in enumerate(z_angles, start=1):
            print(f"Rendering for X angle: {x_angle}° and Z angle: {z_angle}° in iteration {iteration}")

            empty_object.rotation_euler[2] = z_angle * (3.14159 / 180)  
            empty_object.rotation_euler[0] = x_angle * (3.14159 / 180) 

            bpy.context.view_layer.update()
            bpy.context.scene.frame_set(stop_frame)

            # Specify output path
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

            # Render the scene
            bpy.ops.render.render(write_still=False)
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            gc.collect()

    gc.collect()

print("All renders for all iterations completed.")
