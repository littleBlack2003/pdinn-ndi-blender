"""Native 3840 x 2304 transparent final, preserving the approved model.

The provided system Blender has no OpenImageDenoise support. This final therefore
uses up to 512 native path-tracing samples with a stricter adaptive threshold;
no rescaling, AI image replacement or unsupported denoiser is involved.
"""
import bpy, _cycles, os, json, hashlib, time, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
blend_path = os.path.join(R, 'pdinn_jelly.blend')
checkpoint = os.path.join(R, 'checkpoints', 'pdinn_jelly_before_final4k.blend')
if not os.path.exists(checkpoint):
    shutil.copy2(blend_path, checkpoint)
bpy.ops.wm.open_mainfile(filepath=blend_path)
s = bpy.data.scenes['01 • Editable body render']
bpy.context.window.scene = s

def stable(value):
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    try:
        return [stable(v) for v in value]
    except TypeError:
        return str(value)

def hash_scene_content():
    """Includes all object transforms/data, material inputs and studio lighting."""
    objects = sorted(bpy.data.objects, key=lambda o: o.name)
    meshes = {o.data.name: o.data for o in objects if o.type == 'MESH'}
    payload = {
        'objects': [(o.name, o.type, stable(o.matrix_world), o.hide_render,
                     [(x, getattr(o, x)) for x in ['visible_camera', 'visible_transmission']]) for o in objects],
        'meshes': [(n, [stable(v.co) for v in m.vertices], [list(p.vertices) for p in m.polygons]) for n,m in sorted(meshes.items())],
        'curves': [(o.name, o.data.bevel_depth, [[stable(p.co) for p in sp.points] for sp in o.data.splines]) for o in objects if o.type == 'CURVE'],
        'materials': [(m.name, [(n.name, n.bl_idname, [(i.name, stable(i.default_value)) for i in n.inputs if hasattr(i, 'default_value')]) for n in m.node_tree.nodes]) for m in sorted(bpy.data.materials, key=lambda m:m.name) if m.use_nodes],
        'lights': [(o.name, o.data.energy, stable(o.data.color), o.data.type, o.data.size) for o in objects if o.type == 'LIGHT'],
        'camera': (s.camera.name, s.camera.data.type, s.camera.data.ortho_scale, s.camera.data.dof.use_dof),
        'world': [(n.name, [(i.name, stable(i.default_value)) for i in n.inputs if hasattr(i, 'default_value')]) for n in s.world.node_tree.nodes],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

before = hash_scene_content()
assert len(bpy.data.collections['02 • PDINN conceptual motifs'].objects) == 135
assert sum(o.type == 'MESH' for o in bpy.data.collections['03 • NDI segmented chains'].objects) == 141
assert not any(o.type == 'FONT' for o in s.objects)
assert len(bpy.data.scenes) == 1
s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = 512
s.cycles.use_adaptive_sampling = True
s.cycles.adaptive_threshold = 0.01
s.cycles.adaptive_min_samples = 64
s.cycles.use_denoising = bool(_cycles.with_openimagedenoise)
if s.cycles.use_denoising:
    s.cycles.denoiser = 'OPENIMAGEDENOISE'
    s.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    s.cycles.denoising_prefilter = 'ACCURATE'
s.cycles.max_bounces = 16
s.cycles.transmission_bounces = 12
s.cycles.transparent_max_bounces = 16
s.cycles.glossy_bounces = 4
s.cycles.diffuse_bounces = 4
s.cycles.volume_bounces = 0
s.cycles.caustics_reflective = False
s.cycles.caustics_refractive = False
s.cycles.sample_clamp_indirect = 3
s.render.resolution_x = 3840
s.render.resolution_y = 2304
s.render.resolution_percentage = 100
s.render.use_border = False
s.render.use_crop_to_border = False
s.render.filter_size = 1.0
s.render.film_transparent = True
s.cycles.film_transparent_glass = True
s.cycles.film_transparent_roughness = 0.05
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '16'
s.render.image_settings.compression = 35
s.render.filepath = '//renders/PDINN_Jelly_Final_4K_Transparent.png'
s['output_mode'] = 'Native 4K text-free transparent RGBA final'
s['final_render_samples'] = 512
s['final_render_noise_threshold'] = 0.01
s['denoiser_note'] = 'OIDN used only if supported by this Blender build; this build lacks OIDN and uses native high-sample output.'
assert hash_scene_content() == before
report = {
    'revision': 'native-final4k-v11',
    'approved_scene_content_sha256': before,
    'geometry_materials_camera_lights_unchanged': True,
    'resolution': [3840, 2304], 'resolution_percentage': 100,
    'rgba_bit_depth': 16, 'render_engine': 'Cycles CPU',
    'native_render_not_upscale': True, 'maximum_samples': 512,
    'adaptive_threshold': 0.01, 'adaptive_min_samples': 64,
    'denoising': s.cycles.use_denoising,
    'openimagedenoise_compiled_support': bool(_cycles.with_openimagedenoise),
    'total_bounces': 16, 'transmission_bounces': 12, 'transparent_bounces': 16,
    'pdinn_count': 135, 'polymer_core_count': 141, 'chain_count': 8,
    'annotations': 0, 'camera_elevation_deg': 42, 'camera_side_azimuth_deg': 24,
    'pdinn_srgb_hex': '#F0B47C', 'polymer_srgb_hex': '#BE7A9A',
    'film_transparent': True, 'film_transparent_glass': True,
    'output': 'renders/PDINN_Jelly_Final_4K_Transparent.png',
    'previous_48_sample_state': 'checkpoints/pdinn_jelly_before_final4k.blend',
    'status': 'configured',
}
report_path = os.path.join(R, 'final4k_validation.json')
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print('FINAL_RENDER_CONFIG', json.dumps(report), flush=True)
t = time.monotonic()
bpy.ops.render.render(write_still=True)
report['elapsed_render_seconds'] = round(time.monotonic() - t, 2)
report['status'] = 'render_completed'
report['geometry_materials_camera_lights_unchanged'] = hash_scene_content() == before
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)
print('FINAL_RENDER_COMPLETE', json.dumps(report), flush=True)
