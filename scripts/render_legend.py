import bpy, os, math, sys
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'pdinn_jelly.blend'))
s=bpy.context.scene;s.cycles.samples=32;s.cycles.use_denoising=False;s.render.film_transparent=True;s.render.resolution_x=900;s.render.resolution_y=300;s.render.resolution_percentage=100
for ob in bpy.data.objects:
 if ob.type not in ['LIGHT','CAMERA']:ob.hide_render=True
proto=next(o for o in bpy.data.objects if o.name.startswith('PDINN source •'));proto.hide_render=False;proto.location=(0,0,.18);proto.rotation_euler=(0,0,0)
cam=s.camera;cam.location=(0,-1,3.7);cam.rotation_euler=(Vector((0,0,.18))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.85
s.render.filepath=os.path.join(R,'assets','legend_pdinn.png');bpy.ops.render.render(write_still=True)
proto.hide_render=True
mat=bpy.data.materials.get('NDI • azure blue enamel');wiremat=bpy.data.materials.get('NDI • continuous azure backbone')
sys.path.insert(0,R+'/scripts');from ndi_connections import make_terminal_connector
ndiproto=next((o for o in bpy.data.objects if o.name.startswith('NDI source')),None)
if ndiproto is None:
 sys.path.insert(0,R+'/scripts');from ndi_core import make_ndi_core
 edge=bpy.data.materials.get('NDI • raised blue fused-ring contours') or mat
 ndiproto=make_ndi_core(s.collection,mat,edge)
units=[]
for i in range(5):
 x=-1.22+i*.61;y=.075*math.sin((x+1.55)/3.1*math.pi*3);dy=.075*math.pi*3/3.1*math.cos((x+1.55)/3.1*math.pi*3)
 q=ndiproto.copy();q.data=ndiproto.data;s.collection.objects.link(q);q.hide_render=False;q.location=(x,y,.18);q.rotation_euler=Vector((1,dy,0)).to_track_quat('Y','Z').to_euler();units.append(q)
bpy.context.view_layer.update();legendwire,_,err=make_terminal_connector('Legend upper-lower linked NDI chain',units,s.collection,wiremat,tail=.13);assert err<1e-6
cam.data.ortho_scale=3.6;s.render.filepath=os.path.join(R,'assets','legend_ndi.png');bpy.ops.render.render(write_still=True)
print('Legend assets rendered.')
