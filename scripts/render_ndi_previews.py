"""Limited terminal-linkage close-up, matching legend, and whole-scene draft."""
import bpy,os,sys,math
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,R+'/scripts')
from ndi_connections import make_terminal_connector
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');s=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=s;body_output=s.render.filepath
for ob in bpy.data.objects:
 if ob.type not in ['LIGHT','CAMERA']:ob.hide_render=True
# Refresh the PDINN legend from the same newly colored source mesh.
orange=next(o for o in bpy.data.objects if o.name.startswith('PDINN source'));orange.hide_render=False;orange.location=(0,0,.18);orange.rotation_euler=(0,0,0)
s.cycles.samples=32;s.cycles.adaptive_min_samples=8;s.render.film_transparent=True;s.render.resolution_x=900;s.render.resolution_y=300;s.render.resolution_percentage=100
cam=s.camera;cam.location=(0,-1,3.7);cam.rotation_euler=(Vector((0,0,.18))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.85
s.render.filepath=R+'/assets/legend_pdinn.png';bpy.ops.render.render(write_still=True);orange.hide_render=True
proto=next(o for o in bpy.data.objects if o.name.startswith('NDI source'));proto.hide_render=False;proto.location=(0,0,.18);proto.rotation_euler=(0,0,0);bpy.context.view_layer.update()
wiremat=bpy.data.materials['NDI • continuous azure backbone'];unitwire,_,err=make_terminal_connector('Unit view • upper and lower N-R terminal connectors',[proto],s.collection,wiremat,tail=.17)
assert err<1e-6
s.cycles.samples=32;s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.06;s.render.film_transparent=True;s.render.resolution_x=760;s.render.resolution_y=640;s.render.resolution_percentage=100
cam=s.camera;cam.location=(0,-.45,3.7);cam.rotation_euler=(Vector((0,0,.18))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.15
s.render.filepath=R+'/renders/NDI_Four_Ring_Core_Raw.png';bpy.ops.render.render(write_still=True)
proto.hide_render=True;unitwire.hide_render=True;s.render.resolution_x=900;s.render.resolution_y=300
units=[]
for i in range(5):
 x=-1.22+i*.61;y=.075*math.sin((x+1.55)/3.1*math.pi*3);dy=.075*math.pi*3/3.1*math.cos((x+1.55)/3.1*math.pi*3)
 q=proto.copy();q.data=proto.data;s.collection.objects.link(q);q.hide_render=False;q.location=(x,y,.18);q.rotation_euler=Vector((1,dy,0)).to_track_quat('Y','Z').to_euler();units.append(q)
bpy.context.view_layer.update();legendwire,_,err=make_terminal_connector('Legend • terminal-linked NDI chain',units,s.collection,wiremat,tail=.13);assert err<1e-6
cam.location=(0,-1,3.7);cam.rotation_euler=(Vector((0,0,.18))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.6
s.render.filepath=R+'/assets/legend_ndi.png';bpy.ops.render.render(write_still=True)
# Reload the editable project, replace only its packed blue legend, then make
# one low-sample whole-scene draft. No high-quality render is launched.
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');s=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=s
for image in bpy.data.images:
 if 'legend_ndi' in image.name or 'legend_pdinn' in image.name:
  if image.packed_file:image.unpack(method='REMOVE')
  image.filepath=R+'/assets/'+('legend_ndi.png' if 'legend_ndi' in image.name else 'legend_pdinn.png');image.reload();image.pack()
s.render.filepath=body_output;s.cycles.samples=48;s.render.resolution_x=1200;s.render.resolution_y=720;s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');bpy.ops.render.render(write_still=True)
