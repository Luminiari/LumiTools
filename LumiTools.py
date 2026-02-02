bl_info = {
    "name": "LumiTools",
    "author": "Luminiari",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > 🌙 LumiTools",
    "description": "Why don't I just automate most of this shit instead of waiting for other people to update their own tools?",
    "category": "3D View",
}

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import BoolProperty, PointerProperty


class LUMITOOLS_PG_ui_state(PropertyGroup):
    section_setup: BoolProperty(default=True)
    section_clean_merge_xiv: BoolProperty(default=True)
    section_morph_setup: BoolProperty(default=True)
    section_corrections: BoolProperty(default=True)

    morph_target: PointerProperty(
        name="Morph Target",
        type=bpy.types.Object,
        description="Mesh used as the Surface Deform target",
    )

    armature_target: PointerProperty(
        name="Armature Target",
        type=bpy.types.Object,
        description="Optional armature to assign to Armature modifiers",
    )

    preview_flip_weights: BoolProperty(
        name="Preview Only",
        description="Preview how many vertex group pairs would be swapped without making changes",
        default=False,
    )


class LUMITOOLS_OT_magic_make_mod_button(Operator):
    bl_idname = "lumitools.magic_make_mod_button"
    bl_label = "Magic Make Mod Button"
    bl_description = "It does exactly what it says. Probably"

    def execute(self, context):
        context.window_manager.popup_menu(
            lambda menu, _context: (
                menu.layout.label(text="lmao get blendered idiot"),
                menu.layout.label(text=""),
                menu.layout.label(text="There's no such thing as a magic mod-making button"),
                menu.layout.label(text=""),
                menu.layout.label(text="git gud scrub"),
            ),
            title="Magic Make Mod Button",
            icon="INFO",
        )
        return {"FINISHED"}

class LUMITOOLS_OT_clean_merge_xiv(Operator):
    bl_idname = "lumitools.clean_merge_xiv"
    bl_label = "Merge + Smooth + Triangulate"
    bl_description = (
        "Merge vertices by distance, smooth topology, and triangulate the mesh.\n"
        "Intended for use with Cordy's Cross-Generation Porting Tool"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object

        if not obj or obj.type != "MESH":
            self.report({"ERROR"}, "Active object must be a mesh.")
            return {"CANCELLED"}

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=0.0001, use_sharp_edge_from_normals=True)
        bpy.ops.mesh.subdivide()
        bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
        bpy.ops.object.mode_set(mode="OBJECT")

        return {"FINISHED"}


class LUMITOOLS_OT_morph_setup(Operator):
    bl_idname = "lumitools.morph_setup"
    bl_label = "Modifier Setup"
    bl_description = (
        "Add Surface Deform and Corrective Smooth modifiers to selected meshes.\n"
        "Modifiers are only added if missing"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == "MESH"]

        if not meshes:
            self.report({"ERROR"}, "At least one mesh must be selected.")
            return {"CANCELLED"}

        for obj in meshes:
            existing = [m.type for m in obj.modifiers]

            if "SURFACE_DEFORM" not in existing:
                obj.modifiers.new("Surface Deform", "SURFACE_DEFORM")

            if "CORRECTIVE_SMOOTH" not in existing:
                obj.modifiers.new("Corrective Smooth", "CORRECTIVE_SMOOTH")

        return {"FINISHED"}


class LUMITOOLS_OT_bind_surface_deform(Operator):
    bl_idname = "lumitools.bind_surface_deform"
    bl_label = "Bind Surface Deform"
    bl_description = (
        "Assign the selected Morph Target and bind all Surface Deform modifiers\n"
        "on the currently selected meshes"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ui = context.scene.lumitools_ui
        target = ui.morph_target

        if not target:
            self.report({"ERROR"}, "Morph target must be set.")
            return {"CANCELLED"}

        if target.type != "MESH":
            self.report({"ERROR"}, "Morph target must be a mesh.")
            return {"CANCELLED"}

        meshes = [o for o in context.selected_objects if o.type == "MESH"]
        if not meshes:
            self.report({"ERROR"}, "At least one mesh must be selected.")
            return {"CANCELLED"}

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        vl = context.view_layer
        old_active = vl.objects.active

        bound = 0

        for obj in meshes:
            if obj == target:
                continue

            vl.objects.active = obj
            for mod in obj.modifiers:
                if mod.type == "SURFACE_DEFORM":
                    mod.target = target
                    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
                    bound += 1

        vl.objects.active = old_active

        if bound:
            self.report({"INFO"}, "Surface Deform bound successfully.")
        else:
            self.report({"WARNING"}, "No Surface Deform modifiers were bound.")

        return {"FINISHED"}


class LUMITOOLS_OT_cleanup_armature(Operator):
    bl_idname = "lumitools.cleanup_armature"
    bl_label = "Clean-Up"
    bl_description = (
        "Apply Surface Deform and Corrective Smooth modifiers, then ensure\n"
        "an Armature modifier exists. Optionally assigns an Armature Target\n"
        "and parents to that armature"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ui = context.scene.lumitools_ui
        arm_target = ui.armature_target

        if arm_target and arm_target.type != "ARMATURE":
            self.report({"ERROR"}, "Armature Target must be an Armature.")
            return {"CANCELLED"}

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        vl = context.view_layer
        old_active = vl.objects.active

        for obj in list(context.selected_objects):
            for o in context.selected_objects:
                o.select_set(False)

            obj.select_set(True)
            vl.objects.active = obj

            if obj.type != "MESH":
                try:
                    bpy.ops.object.convert(target="MESH")
                except RuntimeError:
                    continue

            if obj.type != "MESH":
                continue

            for mod in list(obj.modifiers):
                if mod.type in {"SURFACE_DEFORM", "CORRECTIVE_SMOOTH"}:
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    except RuntimeError:
                        pass

            arm = None
            for m in obj.modifiers:
                if m.type == "ARMATURE":
                    arm = m
                    break

            if not arm:
                arm = obj.modifiers.new("Armature", "ARMATURE")

            if arm_target:
                arm.object = arm_target
                obj.parent = arm_target
                obj.matrix_parent_inverse = arm_target.matrix_world.inverted()

        vl.objects.active = old_active
        self.report({"INFO"}, "Clean-up complete.")

        return {"FINISHED"}


class LUMITOOLS_OT_flip_weights(Operator):
    bl_idname = "lumitools.flip_weights"
    bl_label = "Flip Weights"
    bl_description = (
        "Swap vertex group names.\n"
        "Made with FFXIV and BG3 meshes in mind, so rip if you mod\n"
        "for anything else I guess.\n"
        "This does not recalculate weights, it only renames groups."
    )
    bl_options = {"REGISTER", "UNDO"}

    preview_only: BoolProperty(
        name="Preview Only",
        description="Preview how many vertex group pairs would be swapped without making changes",
        default=False,
    )

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == "MESH"]

        if not meshes:
            self.report({"ERROR"}, "At least one mesh must be selected.")
            return {"CANCELLED"}

        total_pairs = 0

        for obj in meshes:
            vgs = obj.vertex_groups
            names = [vg.name for vg in vgs]
            pairs = set()

            for name in names:
                if name.endswith(".L"):
                    other = name[:-2] + ".R"
                    if other in names:
                        pairs.add(tuple(sorted((name, other))))
                elif name.endswith(".R"):
                    other = name[:-2] + ".L"
                    if other in names:
                        pairs.add(tuple(sorted((name, other))))

                bits = name.split("_")
                for i, bit in enumerate(bits):
                    if bit in {"l", "r", "L", "R"}:
                        swap = "r" if bit == "l" else "l" if bit == "r" else "R" if bit == "L" else "L"
                        new_bits = bits[:]
                        new_bits[i] = swap
                        other = "_".join(new_bits)
                        if other in names:
                            pairs.add(tuple(sorted((name, other))))

            if not pairs:
                continue

            total_pairs += len(pairs)

            if self.preview_only:
                continue

            tmp = {}
            for a, b in pairs:
                vg = vgs.get(a)
                t = a + "__TMP__"
                vg.name = t
                tmp[t] = b

            for a, b in pairs:
                vgs.get(b).name = a

            for t, b in tmp.items():
                vgs.get(t).name = b

        if total_pairs:
            msg = f"{total_pairs} L/R vertex group pairs would be swapped."
            lvl = {"INFO"}
        else:
            msg = "No swappable L/R vertex group pairs were found."
            lvl = {"WARNING"}

        if self.preview_only:
            self.report(lvl, f"Preview: {msg}")
            context.window_manager.popup_menu(
                lambda m, c: m.layout.label(text=msg),
                title="Flip Weights (Preview)",
                icon="INFO" if total_pairs else "ERROR",
            )
        else:
            if total_pairs:
                self.report({"INFO"}, f"Swapped {total_pairs} L/R vertex group pairs.")
            else:
                self.report({"WARNING"}, msg)

        return {"FINISHED"}


class LUMITOOLS_PT_sidebar(Panel):
    bl_idname = "LUMITOOLS_PT_sidebar"
    bl_label = "🌙 LumiTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "🌙 LumiTools"

    def draw(self, context):
        layout = self.layout
        ui = context.scene.lumitools_ui
        
        box = layout.box()
        row = box.row(align=True)
        row.prop(
            ui,
            "section_setup",
            text="",
            emboss=False,
            icon="TRIA_DOWN" if ui.section_setup else "TRIA_RIGHT",
        )
        row.label(text="Setup", icon="COLLECTION_COLOR_01")

        if ui.section_setup:
            box.operator(
                "lumitools.magic_make_mod_button",
                text="Magic Make Mod Button",
                icon="SOLO_ON",
            )

        box = layout.box()
        row = box.row(align=True)
        row.prop(ui, "section_clean_merge_xiv", text="", emboss=False,
                 icon="TRIA_DOWN" if ui.section_clean_merge_xiv else "TRIA_RIGHT")
        row.label(text="Clean Merge (XIV)", icon="COLLECTION_COLOR_07")

        if ui.section_clean_merge_xiv:
            box.operator("lumitools.clean_merge_xiv",
                         text="Merge + Smooth + Triangulate",
                         icon="AUTOMERGE_ON")

        box = layout.box()
        row = box.row(align=True)
        row.prop(ui, "section_morph_setup", text="", emboss=False,
                 icon="TRIA_DOWN" if ui.section_morph_setup else "TRIA_RIGHT")
        row.label(text="Morph Setup", icon="COLLECTION_COLOR_06")

        if ui.section_morph_setup:
            box.operator("lumitools.morph_setup", text="Modifier Setup", icon="MOD_SMOOTH")
            box.prop(ui, "morph_target", text="Morph Target")
            box.operator("lumitools.bind_surface_deform",
                         text="Bind Surface Deform",
                         icon="MOD_MESHDEFORM")
            box.prop(ui, "armature_target", text="Armature Target")
            box.operator("lumitools.cleanup_armature",
                         text="Clean-Up",
                         icon="OUTLINER_OB_MESH")

        box = layout.box()
        row = box.row(align=True)
        row.prop(ui, "section_corrections", text="", emboss=False,
                 icon="TRIA_DOWN" if ui.section_corrections else "TRIA_RIGHT")
        row.label(text="Corrections", icon="COLLECTION_COLOR_05")

        if ui.section_corrections:
            box.prop(ui, "preview_flip_weights")
            txt = "Flip Weights (Preview)" if ui.preview_flip_weights else "Flip Weights"
            op = box.operator("lumitools.flip_weights", text=txt, icon="BONE_DATA")
            op.preview_only = ui.preview_flip_weights


CLASSES = (
    LUMITOOLS_PG_ui_state,
    LUMITOOLS_OT_magic_make_mod_button,
    LUMITOOLS_OT_clean_merge_xiv,
    LUMITOOLS_OT_morph_setup,
    LUMITOOLS_OT_bind_surface_deform,
    LUMITOOLS_OT_cleanup_armature,
    LUMITOOLS_OT_flip_weights,
    LUMITOOLS_PT_sidebar,
)


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)
    bpy.types.Scene.lumitools_ui = PointerProperty(type=LUMITOOLS_PG_ui_state)


def unregister():
    del bpy.types.Scene.lumitools_ui
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
