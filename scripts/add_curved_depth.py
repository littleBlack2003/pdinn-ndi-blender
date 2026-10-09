"""Editable depth revision: curved 3D chains and four staggered motif layers.
Runs on the saved, clear single-transmission project. Only a 48-sample draft
is rendered by default. No extra chemical bonds or crosslink claims are added.
"""
import bpy, math, random, os, sys, json, argparse
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p=argparse.ArgumentParser();p.add_argument('--skip-render',action='store_true');p.add_argument('--width',type=int,default=1200);p.add_argument('--samples',type=int,default=48)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend')
body=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=body
GEL=bpy.data.collections['01 • Soft transparent jelly'];BLUE=bpy.data.collections['03 • NDI segmented chains'];ORANGE=bpy.data.collections['02 • PDINN conceptual motifs']
# Rounded slab really gains volume; restore its unmodified local geometry first
# when this script is rerun, making the revision idempotent.
gel=GEL.objects[0]
old_factor=float(gel.get('depth_revision_z_factor',1))
for v in gel.data.vertices:v.co.z=v.co.z/old_factor*1.80
gel['depth_revision_z_factor']=1.80;gel.location.z=1.08
# A thicker slab needs a milder art-directed IOR to avoid magnifying the
# frontmost icons into streaks. Keep one camera transmission path.
jelly=bpy.data.materials['Jelly • water-rich soft transmission'];jelly.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.13
# Keep original view direction but center the thicker volume.
for s in bpy.data.scenes:
 if not s.get('depth_revision_camera_centered',False):
  s.camera.location.z+=.40;s['depth_revision_camera_centered']=True
 s.camera.data.dof.use_dof=False;s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.065
 s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.threads_mode='FIXED';s.render.threads=8;s.cycles.use_denoising=False
 s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*(.6 if s==body else 2/3))
# Camera-attached editable labels follow the matching camera translation.
texts=bpy.data.collections.get('06 • Native editable Chinese poster labels')
if texts and not texts.get('depth_revision_centered',False):
 for o in texts.objects:o.location.z+=.40
 texts['depth_revision_centered']=True
# Five paths, including a clear hairpin, broad S, and crossing interlayer bridge.
# The centerline is 3D; repeats orient with its full XYZ tangent.
NODES=[
[(-5.45,-2.4,.43),(-3.8,-2.25,.58),(-2,-2.65,.48),(0,-2.1,.54),(2,-2.15,.4),(3.8,-2.35,.50),(5.45,-2.3,.67)],
[(-5.45,-1.45,1.3),(-3.7,-1.65,1.53),(-2,-.15,1.56),(-.5,-.35,1.18),(1.3,-1.75,.80),(2.6,-1.30,.86),(3.7,.0,1.33),(5.4,.3,1.50)],
[(-5.4,.15,.7),(-4.4,.95,.76),(-2.8,1.35,.90),(-1.2,.85,1.21),(.1,.65,1.57),(1.4,1.1,1.65),(2.1,1.9,1.50),(1.9,2.48,1.27),(.3,2.52,.83),(-1.5,2.05,.47)],
[(-5.45,2.28,1.52),(-3.6,2.58,1.64),(-1.4,2.18,1.47),(.6,1.95,1.24),(2.8,2.58,.92),(4.4,2.32,.71),(5.48,1.8,.75)],
[(-3.8,-.78,.45),(-2.3,-1.65,.6),(-.6,-1.38,.55),(.6,-.30,.67),(2,.28,.60),(3.15,.6,.46),(4.35,1.35,.75),(5.35,.8,1.1)]
]
def natural_spline(nodes,steps=450):
 v=[Vector(n) for n in nodes];n=len(v);t=[0]
 for j in range(n-1):t.append(t[-1]+(v[j+1]-v[j]).length)
 h=[t[j+1]-t[j] for j in range(n-1)]
 lo=[0.0]*n;di=[1.0]*n;up=[0.0]*n;rhs=[Vector((0,0,0)) for j in range(n)]
 for j in range(1,n-1):lo[j]=h[j-1];di[j]=2*(h[j-1]+h[j]);up[j]=h[j];rhs[j]=6*((v[j+1]-v[j])/h[j]-(v[j]-v[j-1])/h[j-1])
 for j in range(1,n):f=lo[j]/di[j-1];di[j]-=f*up[j-1];rhs[j]-=f*rhs[j-1]
 m=[Vector((0,0,0)) for j in range(n)];m[-1]=rhs[-1]/di[-1]
 for j in range(n-2,-1,-1):m[j]=(rhs[j]-up[j]*m[j+1])/di[j]
 points=[];j=0
 for k in range(steps):
  x=t[-1]*k/(steps-1)
  while j<n-2 and x>t[j+1]:j+=1
  A=(t[j+1]-x)/h[j];B=(x-t[j])/h[j]
  points.append(A*v[j]+B*v[j+1]+((A**3-A)*m[j]+(B**3-B)*m[j+1])*h[j]**2/6)
 return points
paths=[natural_spline(n) for n in NODES]
for ob in list(BLUE.objects):bpy.data.objects.remove(ob,do_unlink=True)
def put_in(ob,col):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 col.objects.link(ob)
for k,path in enumerate(paths):
 cu=bpy.data.curves.new('NDI %02d • continuous XYZ centerline'%(k+1),'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=.040;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(path)-1)
 for pp,v in zip(sp.points,path):pp.co=(*v,1)
 ob=bpy.data.objects.new('NDI chain %02d • curved interlayer backbone'%(k+1),cu);BLUE.objects.link(ob);cu.materials.append(bpy.data.materials['NDI • continuous azure backbone'])
 ob['path_control_points']=json.dumps(NODES[k]);ob['meaning']='A continuous conceptual polymer chain. Projected crossings are spatial entanglement, not newly asserted covalent crosslinks.'
 lengths=[0]
 for i in range(1,len(path)):lengths.append(lengths[-1]+(path[i]-path[i-1]).length)
 t=.16;ii=1;num=0
 while t<lengths[-1]-.16:
  while lengths[ii]<t:ii+=1
  f=(t-lengths[ii-1])/(lengths[ii]-lengths[ii-1]);pos=path[ii-1].lerp(path[ii],f);tan=(path[min(ii+2,len(path)-1)]-path[max(ii-2,0)]).normalized()
  bpy.ops.mesh.primitive_cube_add(size=1,location=pos);q=bpy.context.object;put_in(q,BLUE);q.name='NDI %02d • XYZ tangent repeat %02d'%(k+1,num);q.dimensions=(.49,.255,.135);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);q.rotation_euler=tan.to_track_quat('X','Z').to_euler();q.data.materials.append(bpy.data.materials['NDI • azure blue enamel']);bv=q.modifiers.new('Soft rounded rectangular segment','BEVEL');bv.width=.058;bv.segments=4;q.modifiers.new('Smooth weighted normals','WEIGHTED_NORMAL');num+=1;t+=.75
# Fill four real Z bands with irregular orientation; preserve 75 approved icons.
# Placement accepts only complete motif meshes inside the gel.
bpy.context.view_layer.update();depsgraph=bpy.context.evaluated_depsgraph_get();gel_bvh=BVHTree.FromObject(gel,depsgraph);gel_inv=gel.matrix_world.inverted()
def inside_gel(point,margin=.018):
 co=gel_inv@point;hit=gel_bvh.find_nearest(co)
 return hit[0] is not None and (co-hit[0]).dot(hit[1])<=-margin
proto=next(o for o in bpy.data.collections['05 • Editable source geometry'].objects if o.name.startswith('PDINN source'))
source_mesh=proto.data
for ob in list(ORANGE.objects):bpy.data.objects.remove(ob,do_unlink=True)
rng=random.Random(4109);placed=[];zs=(.36,.79,1.22,1.66);counts=(18,19,19,19);depth_counts=[];attempt_count=0
for band,(z,count) in enumerate(zip(zs,counts)):
 accepted=0
 while accepted<count and attempt_count<35000:
  attempt_count+=1
  q=proto.copy();q.data=source_mesh;q.hide_render=False;q.hide_viewport=False;ORANGE.objects.link(q)
  q.location=(rng.uniform(-5.42,5.42),rng.uniform(-2.76,2.76),z+rng.uniform(-.075,.075))
  q.rotation_euler=(rng.uniform(-.32,.32),rng.uniform(-.35,.35),rng.uniform(-math.pi,math.pi));sc=rng.uniform(.82,1.05);q.scale=(sc,sc,sc);bpy.context.view_layer.update()
  # Keep enough spacing in each depth band, while deliberately allowing layers
  # to overlap in projection rather than lining all icons into a single sheet.
  if any((Vector((q.location.x-p.x,q.location.y-p.y,(q.location.z-p.z)*1.15))).length<.73 for p in placed):bpy.data.objects.remove(q,do_unlink=True);continue
  inv=q.matrix_world.inverted();near_chain=False
  for path in paths:
   for p0 in path[::3]:
    v=inv@p0
    if abs(v.x)<.58 and abs(v.y)<.22 and abs(v.z)<.14:near_chain=True;break
   if near_chain:break
  if near_chain:bpy.data.objects.remove(q,do_unlink=True);continue
  world_verts=[q.matrix_world@v.co for v in source_mesh.vertices]
  if not all(inside_gel(v) for v in world_verts):bpy.data.objects.remove(q,do_unlink=True);continue
  q.name='PDINN depth %d • %03d'%(band+1,accepted+1);q['depth_band']=band+1;placed.append(q.location.copy());accepted+=1
 depth_counts.append(accepted)
 if accepted<count:raise RuntimeError('Could not contain required motifs in depth band '+str(band+1))
# Confirm blue connectors and repeat bounding vertices remain contained.
bpy.context.view_layer.update()
blue_outside=[]
for ob in BLUE.objects:
 points=[ob.matrix_world@v.co for v in ob.data.vertices] if ob.type=='MESH' else [Vector(p.co[:3]) for p in ob.data.splines[0].points]
 if not all(inside_gel(v,.003) for v in points):blue_outside.append(ob.name)
if blue_outside:raise RuntimeError('Blue geometry outside the gel: '+str(blue_outside))
minimum_pair=min(min((p-q).length for p in paths[i][::3] for q in paths[j][::3]) for i in range(5) for j in range(i))
if minimum_pair<.20:raise RuntimeError('Two chain centerlines too close: '+str(minimum_pair))
for s in bpy.data.scenes:
 s['depth_revision']='Four staggered molecular depth bands, five continuous 3D polymer paths including a hairpin and broad S, and 1.8× gel thickness. Conceptual physical interpenetration, no new covalent bonds.';s['depth_band_counts']=depth_counts;s['chain_count']=5;s['motif_count']=75;s['preview_only']=True;s['render_quality_note']='Limited draft only, 1200 px body / 48 samples. No high-resolution final render performed for this revision.'
body.render.filepath=R+'/renders/curved_depth_body_1200.png'
report={'revision':'curved-depth-draft-v4','depth_bands':zs,'depth_counts':depth_counts,'orange_count':len(ORANGE.objects),'chain_count':5,'gel_z_factor':1.80,'gel_z_bounds':[min((gel.matrix_world@v.co).z for v in gel.data.vertices),max((gel.matrix_world@v.co).z for v in gel.data.vertices)],'orange_center_z_range':[min(p.z for p in placed),max(p.z for p in placed)],'blue_centerline_z_ranges':[[min(p.z for p in ps),max(p.z for p in ps)] for ps in paths],'minimum_chain_centerline_separation':minimum_pair,'all_motif_vertices_inside_gel':True,'all_blue_geometry_inside_gel':True,'blue_blocks_follow_xyz_tangent':True,'new_covalent_bonds_added':False,'dof':False,'render_resolution':[a.width,round(a.width*.6)],'samples':a.samples,'placement_attempts':attempt_count,'seven_ring_source_unchanged':True}
with open(R+'/curved_depth_validation.json','w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend')
print('DEPTH_VALIDATION',json.dumps(report))
if not a.skip_render:bpy.ops.render.render(write_still=True)
