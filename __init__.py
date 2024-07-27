import bpy
import os

from bpy.types import Menu, Operator, AddonPreferences
from bpy.props import StringProperty


def get_current_mode(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    import darkdetect
    addon_prefs.current_mode = darkdetect.theme()

    return addon_prefs.current_mode


def set_theme_from_system(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    light_theme_path = addon_prefs.light_theme_path
    dark_theme_path = addon_prefs.dark_theme_path
    current_mode = get_current_mode(context)

    # Default to dark.
    switch_to_theme = dark_theme_path

    if current_mode == 'Light':
        switch_to_theme = light_theme_path

    # Set the theme.
    bpy.ops.script.execute_preset(
        filepath=switch_to_theme,
        menu_idname="USERPREF_MT_interface_theme_presets",
    )

    # Set the theme name as label for dropdowns.
    WM_MT_autoswitch_theme_light.bl_label = bpy.path.display_name(light_theme_path)
    WM_MT_autoswitch_theme_dark.bl_label = bpy.path.display_name(dark_theme_path)


def load_post_handler(context):
    set_theme_from_system(bpy.context)


class WM_AutoThemePreferences(AddonPreferences):
    bl_idname = __package__

    scripts_path = bpy.utils.script_paths()[0]
    themes_path = os.path.join(scripts_path, "presets/interface_theme")

    light_theme_path: StringProperty(
        name='Light Theme Filepath',
        description='Filepath to use as light theme',
        default=os.path.join(themes_path, "Blender_Light.xml"),
    )

    dark_theme_path: StringProperty(
        name='Dark Theme Filepath',
        description='Filepath to use as dark theme',
        default=os.path.join(themes_path, "Blender_Dark.xml"),
    )

    current_mode: StringProperty(
        name='Light or Dark',
        default="Not detected yet",
    )

    def draw(self, _context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        split = col.split(factor=0.4)
        split.alignment = 'RIGHT'
        split.label(text="System Appearance Mode")
        split = split.column()
        row = split.row()
        row.label(text=self.current_mode)
        row.operator("wm.autoswitch_set_theme_auto", text="", icon='FILE_REFRESH')

        col.separator(type='LINE')

        sub = col.column(heading="Light Theme")
        sub.menu("WM_MT_autoswitch_theme_light", text=WM_MT_autoswitch_theme_light.bl_label)

        sub = col.column(heading="Dark Theme")
        sub.menu("WM_MT_autoswitch_theme_dark", text=WM_MT_autoswitch_theme_dark.bl_label)


class WM_OT_autoswitch_set_theme_auto(Operator):
    """Switch the theme to follow system light/dark mode"""
    bl_idname = "wm.autoswitch_set_theme_auto"
    bl_label = "Manually Set Themes"

    def execute(self, context):
        set_theme_from_system(context)

        return {'FINISHED'}


class WM_OT_autoswitch_set_theme_light(Operator):
    """Set theme path to use when light"""
    bl_idname = "wm.autoswitch_set_theme_light"
    bl_label = "Set Light Theme to AutoSwitch to"

    menu_idname: StringProperty(
        name='WM_MT_autoswitch_theme_light',
    )

    filepath: StringProperty(
        name='Theme Filepath',
    )

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        addon_prefs.light_theme_path = self.filepath
        WM_MT_autoswitch_theme_light.bl_label = bpy.path.display_name(self.filepath)

        return {'FINISHED'}


class WM_OT_autoswitch_set_theme_dark(Operator):
    """Set theme path to use when dark"""
    bl_idname = "wm.autoswitch_set_theme_dark"
    bl_label = "Set Dark Theme to AutoSwitch to"

    menu_idname: StringProperty(
        name='WM_MT_autoswitch_theme_dark',
    )

    filepath: StringProperty(
        name='Theme Filepath',
    )

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        addon_prefs.dark_theme_path = self.filepath
        WM_MT_autoswitch_theme_dark.bl_label = bpy.path.display_name(self.filepath)

        return {'FINISHED'}


class WM_MT_autoswitch_theme_light(Menu):
    bl_label = "Blender Light"
    bl_description = "Set light theme to auto-switch to"
    preset_subdir = "interface_theme"
    preset_operator = "wm.autoswitch_set_theme_light"
    draw = Menu.draw_preset


class WM_MT_autoswitch_theme_dark(Menu):
    bl_label = "Blender Dark"
    bl_description = "Set dark theme to auto-switch to"
    preset_subdir = "interface_theme"
    preset_operator = "wm.autoswitch_set_theme_dark"
    draw = Menu.draw_preset


classes = (
    WM_AutoThemePreferences,
    WM_MT_autoswitch_theme_light,
    WM_MT_autoswitch_theme_dark,
    WM_OT_autoswitch_set_theme_auto,
    WM_OT_autoswitch_set_theme_light,
    WM_OT_autoswitch_set_theme_dark,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    from bl_pkg import theme_preset_draw
    WM_MT_autoswitch_theme_light.append(theme_preset_draw)
    WM_MT_autoswitch_theme_dark.append(theme_preset_draw)

    bpy.app.handlers.load_post.append(load_post_handler)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    from bl_pkg import theme_preset_draw
    WM_MT_autoswitch_theme_light.remove(theme_preset_draw)
    WM_MT_autoswitch_theme_dark.remove(theme_preset_draw)

    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)


if __name__ == "__main__":
    register()
