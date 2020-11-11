import bpy
from bpy_extras.io_utils import ImportHelper
import os
# load font list
C = bpy.context
fontlist = []
fontpaths = []
fontindex = []
op = 0
for root, dirs, files in os.walk(bpy.path.abspath('//fonts/')):
    for file in files:
        if not file.startswith('.'):
            op =  op + 1
            fontlist.append(file)
            fontpaths.append(root+'/'+file)
            fontindex.append('op' + str(op))
merged_list = list(zip(fontlist, fontlist, fontindex))
bpy.context.scene["fonts"] = merged_list

class PRINT_PANEL(bpy.types.Panel):
    bl_label = "3D print toolbox"
    bl_idname = "ADDONNAME_PT_TemplatePanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_category = "3D print toolbox"
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="3D print setting", icon='WORLD_DATA')
        row = layout.row()
        row.operator("wm.textbox", text= "Create text sign", icon= 'OUTLINER_OB_FONT')
        row = layout.row()
        row.operator("wm.remesh", text= "Remesh (fix topology", icon= 'MOD_REMESH')
        layout.row().separator()
        row = layout.row()
        row.label(text="Save&export", icon='DISK_DRIVE')
        row = layout.row()
        row.operator("wm.exportstl", text= "Export STL", icon= 'FILE')
        row.operator("wm.openfile", text= "Open in Slicer", icon= 'OUTPUT')

# save export
class OT_Remesh(bpy.types.Operator):
    bl_idname = "wm.remesh"
    bl_label = "Remesh"

    def execute(self, context):
        print ("REMESH")
        for obj in bpy.context.scene.objects:
            #  convert font to mesh          
            if obj.type == 'FONT':
                obj.select_set(True)
                obj = context.active_object
                bpy.ops.object.convert()
                bpy.ops.object.modifier_add(type="REMESH")
                bpy.context.object.modifiers["Remesh"].mode = 'SHARP'
                bpy.context.object.modifiers["Remesh"].octree_depth = 8
                bpy.context.object.modifiers["Remesh"].scale = 0.5
                bpy.context.object.modifiers["Remesh"].use_remove_disconnected = False
                bpy.context.object.modifiers["Remesh"].use_smooth_shade = False
                bpy.ops.object.modifier_apply(modifier="Remesh")
            if obj.type == 'MESH':
                obj.select_set(True)
                bpy.ops.object.modifier_add(type="REMESH")
                bpy.context.object.modifiers["Remesh"].mode = 'SHARP'
                bpy.context.object.modifiers["Remesh"].octree_depth = 9
                bpy.context.object.modifiers["Remesh"].scale = 0.5
                bpy.context.object.modifiers["Remesh"].use_remove_disconnected = False
                bpy.context.object.modifiers["Remesh"].use_smooth_shade = False
                bpy.ops.object.modifier_apply(modifier="Remesh")
        return {'FINISHED'}

def remove_objects():
    try:
            for obj in bpy.context.scene.objects:
                    if "Text" in obj.name:
                        obj.select_set(True)
                        print (obj.name)
                        bpy.ops.object.delete()
                    else:
                        obj.select_set(False)
    except:
        print ('nothing to remove')

class OT_Text_box(bpy.types.Operator):
    bl_idname = "wm.textbox"
    bl_label = "Choose setting"
    text : bpy.props.StringProperty(name="Sign text", default="Text")    
    preset_enum: bpy.props.EnumProperty(
        name= 'Custom font',
        items= merged_list
    )
    char_spacing : bpy.props.FloatProperty(name= "Character spacing", default= 1, min=0, max=5)
    bend_size : bpy.props.FloatProperty(name= "Bend", default= 0, min=0, max=5)
    extrude_amount : bpy.props.FloatProperty(name= "Extrude Amount", default= 1, min=0, max=20, unit="LENGTH")
    text_profile_amount : bpy.props.FloatProperty(name= "Text profile size", default= 0, min=0, max=0.4,unit="LENGTH")
    outline : bpy.props.BoolProperty(name= "outline", default= False)
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        remove_objects()

        ea = self.extrude_amount
        pa = self.text_profile_amount
        b = self.bend_size
        t = self.text
        o = self.outline
        ch = self.char_spacing

        bpy.ops.object.text_add(location=(0, 0, 0), rotation=(0, 0, 0))
        txt = bpy.data.objects['Text']
        bpy.context.object.data.size = 25
        txt.data.body = t
        fbxPath = bpy.path.abspath("//fonts/"+ str(self.preset_enum))
        fnt = bpy.data.fonts.load(fbxPath)
        txt.data.font = fnt
        bpy.context.object.data.space_character = ch
        bpy.context.object.data.align_x = 'CENTER'
        bpy.context.object.data.align_y = 'CENTER'
        #        add material
        obj = context.active_object
        bpy.data.materials.new(name="GOLD")
        mat_gold = bpy.data.materials.new(name="GOLD") #set new material to variable
        obj.data.materials.append(mat_gold) #add the material to the object
        bpy.context.object.active_material.diffuse_color = hex_to_rgb('FFE453') #change color
        bpy.context.object.active_material.metallic = (1)    

        if ea != 0:
            bpy.context.object.data.extrude = ea
            bpy.context.object.data.resolution_u = 5
            if pa != 0:
                try:
                    bpy.context.object.data.bevel_mode = 'ROUND'
                except:
                    print ('old blender')
                bpy.context.object.data.bevel_depth = pa
        bpy.ops.object.convert()
        scn = bpy.context.scene
        mesh = obj.data
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.transform.shrink_fatten(value=0.0001)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.convert()

        if o == True:
            #/remesh object first for better result
            obj.select_set(True)
            bpy.ops.object.modifier_add(type="REMESH")
            bpy.context.object.modifiers["Remesh"].mode = 'SHARP'
            bpy.context.object.modifiers["Remesh"].octree_depth = 9
            bpy.context.object.modifiers["Remesh"].scale = 0.5
            bpy.context.object.modifiers["Remesh"].use_remove_disconnected = False
            bpy.context.object.modifiers["Remesh"].use_smooth_shade = False
            bpy.ops.object.modifier_apply(modifier="Remesh")            

            dup = bpy.data.objects.new(obj.name, mesh.copy())
            bpy.context.collection.objects.link(dup)
            dup = context.active_object
            dup.name = 'Text_Outline'
            black_mat = bpy.data.materials.new(name="BLACK") #set new material to variable
            dup.active_material = black_mat
            bpy.context.object.active_material.diffuse_color = (0, 0, 0,1)
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.transform.shrink_fatten(value=0.52, use_even_offset=False, proportional_size=1)
            bpy.ops.object.editmode_toggle()
            bpy.ops.transform.translate(value=(0, 0, -1.3), orient_type='GLOBAL')

        if b != 0:
            for obj in bpy.context.scene.objects:
                if "Text" in obj.name:
                    mod = obj.modifiers.new("SimpleDeform", 'SIMPLE_DEFORM')
                    mod.deform_method = "BEND"
                    mod.angle = b
                    mod.deform_axis = "Z"
                    mod.origin = bpy.data.objects['Camera']
                    bpy.ops.object.modifier_apply(modifier="SimpleDeform")

        bpy.ops.object.select_all(action='DESELECT')  
        return {'FINISHED'}

# save export
class OT_ExportSTL(bpy.types.Operator):
    bl_idname = "wm.exportstl"
    bl_label = "Export STL"

    def execute(self, context):
        print ("EXPORTING")
        dir = bpy.path.abspath('//stlexport/')
        # Create Directory (If Necessary)
        if not os.path.exists(dir): os.makedirs(dir)
        for obj in bpy.context.scene.objects:
            #  convert font to mesh          
            if obj.type == 'FONT':
                obj = context.active_object
                bpy.ops.object.convert()
            if "Text" in obj.name:
                obj.select_set(True)
                bpy.ops.mesh.print3d_clean_non_manifold()
        bpy.ops.export_mesh.stl(filepath = dir, batch_mode = 'OBJECT')
        return {'FINISHED'}

class OT_OpenSlicer(bpy.types.Operator):
    bl_idname = "wm.openfile"
    bl_label = "Open in slicer"
    def execute(self, context):
        files = []
        print ("OPENING")
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                if "." in obj.name:
                    obj.select_set(True)
                    obj.name = obj.name.replace(".", "_")   
                files.append("'" + bpy.path.abspath('//stlexport/') + obj.name + '.stl' + "'")
        print ("open" + " " + " ".join(files))
        os.system("open" + " " + " ".join(files))
        return {'FINISHED'}

# helper functions
def hex_to_rgb(value):
    gamma = 2.2
    value = value.lstrip('#')
    lv = len(value)
    fin = list(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    r = pow(fin[0] / 255, gamma)
    g = pow(fin[1] / 255, gamma)
    b = pow(fin[2] / 255, gamma)
    fin.clear()
    fin.append(r)
    fin.append(g)
    fin.append(b)
    fin.append(1.0)
    return tuple(fin)

def register():
    bpy.utils.register_class(PRINT_PANEL)
    bpy.utils.register_class(OT_Text_box)
    bpy.utils.register_class(OT_ExportSTL)
    bpy.utils.register_class(OT_OpenSlicer)
    bpy.utils.register_class(OT_Remesh)

def unregister():
    bpy.utils.unregister_class(PRINT_PANEL)
    bpy.utils.unregister_class(OT_Text_box)
    bpy.utils.unregister_class(OT_ExportSTL)
    bpy.utils.unregister_class(OT_OpenSlicer)
    bpy.utils.unregister_class(OT_Remesh)

if __name__ == "__main__":
    register()
