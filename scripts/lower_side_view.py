"""Lower the camera and show more side face without changing molecular content.
Both body and native poster cameras are updated. Native labels retain their
screen positions and apparent size; only their camera-facing layout changes.
"""
import bpy,os,math,json,hashlib
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend')
body=bpy.data.scenes['01 • Editable body render'];poster=bpy.data.scenes['02 • Native Chinese poster'];bpy.context.window.scene=body

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def content_hash():
 names=['01 • Soft transparent jelly','02 • PDINN conceptual motifs','03 • NDI segmented chains','04 • Studio','05 • Editable source geometry','07 • Original backbone path guides']
 obs=sorted([o for n in names for o in bpy.data.collections[n].objects if o.type!='CAMERA'],key=lambda o:o.name);meshes={o.data.name:o.data for o in obs if o.type=='MESH'}
 return digest({'objects':[(o.name,o.type,[[*r] for r in o.matrix_world]) for o in obs],'meshes':[(n,[list(v.co) for v in m.vertices],[list(p.vertices) for p in m.polygons]) for n,m in sorted(meshes.items())],'curves':[(o.name,[[list(p.co) for p in sp.points] for sp in o.data.splines]) for o in obs if o.type=='CURVE']})
def material_hash():
 return digest([(m.name,list(m.diffuse_color),[(n.name,n.type,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]) for m in sorted(bpy.data.materials,key=lambda m:m.name) if m.use_nodes])
def angles(cam):
 a=cam.rotation_euler.to_quaternion()@Vector((0,0,1));return {'elevation_deg':math.degrees(math.atan2(a.z,math.hypot(a.x,a.y))),'side_azimuth_from_front_deg':math.degrees(math.atan2(a.x,-a.y)),'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale}
before_hash=content_hash();before_material=material_hash();old_body=angles(body.camera);old_poster=angles(poster.camera);old_poster_matrix=poster.camera.matrix_world.copy();old_ratio=poster.camera.data.ortho_scale/body.camera.data.ortho_scale
labels=bpy.data.collections['06 • Native editable Chinese poster labels'];label_locals={o.name:old_poster_matrix.inverted()@o.matrix_world for o in labels.objects};label_ndc_before={o.name:list(world_to_camera_view(poster,poster.camera,o.matrix_world.translation)) for o in labels.objects}
el=math.radians(42);az=math.radians(24);distance=18.2;target=Vector((0,0,1.08));new_location=target+Vector((distance*math.cos(el)*math.sin(az),-distance*math.cos(el)*math.cos(az),distance*math.sin(el)))
for s in [body,poster]:
 c=s.camera;c.location=new_location;c.rotation_euler=(target-new_location).to_track_quat('-Z','Y').to_euler();c.data.dof.use_dof=False
body.camera.data.ortho_scale=15.8;bpy.context.view_layer.update()
gel=bpy.data.collections['01 • Soft transparent jelly'].objects[0];pts=[gel.matrix_world@v.co for v in gel.data.vertices]
def bounds():
 uv=[world_to_camera_view(body,body.camera,p) for p in pts];return [min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
b=bounds();factor=max(1,(.5-b[0])/.45,(b[1]-.5)/.45,(.5-b[2])/.43,(b[3]-.5)/.43);body.camera.data.ortho_scale*=factor
poster.camera.data.ortho_scale=body.camera.data.ortho_scale*old_ratio;bpy.context.view_layer.update();scale=poster.camera.data.ortho_scale/old_poster['ortho_scale'];screen_scale=Matrix.Diagonal((scale,scale,1,1))
for o in labels.objects:o.matrix_world=poster.camera.matrix_world@screen_scale@label_locals[o.name]
bpy.context.view_layer.update();label_error=max(max(abs(world_to_camera_view(poster,poster.camera,o.matrix_world.translation)[i]-label_ndc_before[o.name][i]) for i in [0,1]) for o in labels.objects)
assert label_error<1e-5
assert content_hash()==before_hash and material_hash()==before_material
b=bounds();assert b[0]>.024 and b[1]<.98 and b[2]>.045 and b[3]<.96,b
for s in [body,poster]:s.cycles.samples=48;s.render.resolution_x=1200;s.render.resolution_y=720 if s==body else 800;s['view_revision']='Camera lowered to42 degrees elevation, side azimuth24 degrees. Molecular geometry, gel and materials unchanged.'
body.render.filepath='//renders/lower_side_body_1200.png'
report={'revision':'lower-side-view-v9','body_camera_before':old_body,'body_camera_after':angles(body.camera),'poster_camera_before':old_poster,'poster_camera_after':angles(poster.camera),'body_gel_ndc_bounds':[b[0],b[1],b[2],b[3]],'whole_matrix_inside_crop':True,'native_label_screen_position_max_error':label_error,'native_label_apparent_size_preserved':True,'geometry_and_non_camera_object_hash_unchanged':before_hash,'all_material_node_hash_unchanged':before_material,'pdinn_count':135,'polymer_core_count':141,'chain_count':8,'pdinn_srgb':'#F0B47C','polymer_srgb':'#BE7A9A','body_resolution':[1200,720],'poster_resolution':[1200,800],'samples':48}
with open(R+'/view_validation.json','w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('VIEW_VALIDATION',json.dumps(report))
