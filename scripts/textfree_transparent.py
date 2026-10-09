"""Make the current model annotation-free on a genuine RGBA background.
The preceding labeled project is retained as a checkpoint, not in the active
scenes. Studio lighting/world remain; the floor is invisible to camera and
transmission rays so it cannot become a white background through the gel.
"""
import bpy,os,json,hashlib
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');body=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=body

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def model_hash():
 cols=['01 • Soft transparent jelly','02 • PDINN conceptual motifs','03 • NDI segmented chains','05 • Editable source geometry','07 • Original backbone path guides'];obs=sorted([o for n in cols for o in bpy.data.collections[n].objects],key=lambda o:o.name);meshes={o.data.name:o.data for o in obs if o.type=='MESH'}
 return digest({'objects':[(o.name,o.type,[[*r] for r in o.matrix_world]) for o in obs],'meshes':[(n,[list(v.co) for v in m.vertices],[list(p.vertices) for p in m.polygons]) for n,m in sorted(meshes.items())],'curves':[(o.name,[[list(p.co) for p in sp.points] for sp in o.data.splines]) for o in obs if o.type=='CURVE']})
before=model_hash();camera_before=digest([[*r] for r in body.camera.matrix_world]);lights_before=digest([(o.name,[[*r] for r in o.matrix_world],o.data.energy) for o in bpy.data.objects if o.type=='LIGHT'])
# Old annotated layout is available in checkpoints/pdinn_jelly_before_textfree.blend.
other_cameras=[]
for sc in list(bpy.data.scenes):
 if sc!=body:
  if sc.camera and sc.camera!=body.camera:other_cameras.append(sc.camera)
  bpy.data.scenes.remove(sc)
labels=bpy.data.collections.get('06 • Native editable Chinese poster labels');removed=[]
if labels:
 for o in list(labels.objects):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(labels)
for cam in other_cameras:
 if cam.name in bpy.data.objects:bpy.data.objects.remove(cam,do_unlink=True)
assert not any(o.type=='FONT' for o in body.objects)
assert not any('Legend rendered' in o.name for o in body.objects)
floor=bpy.data.objects['Infinite matte white studio'];floor.visible_camera=False;floor.visible_transmission=False
body.render.film_transparent=True;body.render.image_settings.file_format='PNG';body.render.image_settings.color_mode='RGBA';body.render.image_settings.color_depth='8'
if hasattr(body.cycles,'film_transparent_glass'):body.cycles.film_transparent_glass=True
if hasattr(body.cycles,'film_transparent_roughness'):body.cycles.film_transparent_roughness=.05
body.render.resolution_x=1200;body.render.resolution_y=720;body.render.resolution_percentage=100;body.cycles.samples=48;body.camera.data.dof.use_dof=False
body.render.filepath='//renders/PDINN_Jelly_Clear_Draft.png';body['output_mode']='Text-free RGBA model; no title, ratio, legend or footer';body['transparent_background']=True
assert model_hash()==before and digest([[*r] for r in body.camera.matrix_world])==camera_before
assert digest([(o.name,[[*r] for r in o.matrix_world],o.data.energy) for o in bpy.data.objects if o.type=='LIGHT'])==lights_before
report={'revision':'textfree-transparent-v10','annotation_objects_removed':removed,'active_scene_count':len(bpy.data.scenes),'active_text_objects':sum(o.type=='FONT' for o in body.objects),'active_legend_objects':sum('Legend rendered' in o.name for o in body.objects),'model_geometry_hash_unchanged':before,'camera_matrix_hash_unchanged':camera_before,'lighting_hash_unchanged':lights_before,'floor_visible_camera':floor.visible_camera,'floor_visible_transmission':floor.visible_transmission,'world_and_area_lights_retained':True,'film_transparent':body.render.film_transparent,'film_transparent_glass':getattr(body.cycles,'film_transparent_glass',None),'film_transparent_roughness':getattr(body.cycles,'film_transparent_roughness',None),'image_color_mode':body.render.image_settings.color_mode,'resolution':[1200,720],'samples':48,'pdinn_count':len(bpy.data.collections['02 • PDINN conceptual motifs'].objects),'polymer_core_count':sum(o.type=='MESH' for o in bpy.data.collections['03 • NDI segmented chains'].objects),'camera_elevation_deg':42,'camera_side_azimuth_deg':24,'pdinn_srgb':'#F0B47C','polymer_srgb':'#BE7A9A','archived_labeled_project':'checkpoints/pdinn_jelly_before_textfree.blend'}
with open(R+'/textfree_transparent_validation.json','w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('TEXTFREE_TRANSPARENT_VALIDATION',json.dumps(report));bpy.ops.render.render(write_still=True)
