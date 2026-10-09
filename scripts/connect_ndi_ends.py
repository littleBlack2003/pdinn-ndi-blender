"""Rotate the existing four-ring NDI cores and connect their terminal tips.
Preserves core meshes, object centers, orange layers, gel, camera, and guides.
"""
import bpy,os,sys,re,json,math,hashlib
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,R+'/scripts')
from ndi_connections import make_terminal_connector,terminal_frame
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');body=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=body
BLUE=bpy.data.collections['03 • NDI segmented chains'];ORANGE=bpy.data.collections['02 • PDINN conceptual motifs'];ASSETS=bpy.data.collections['05 • Editable source geometry']
guides=bpy.data.collections.get('07 • Original backbone path guides')
if guides is None:guides=bpy.data.collections.new('07 • Original backbone path guides');body.collection.children.link(guides)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def mesh_hash(o):return digest({'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons]})
orange=next(o for o in ASSETS.objects if o.name.startswith('PDINN source'));core=next(o for o in ASSETS.objects if o.name.startswith('NDI source'))
orange_hash=mesh_hash(orange);core_hash=mesh_hash(core);orange_transforms=digest(sorted([[list(r) for r in o.matrix_world] for o in ORANGE.objects]))
centers_before=digest(sorted([list(o.location) for o in BLUE.objects if o.type=='MESH']))
old_curves=[o for o in BLUE.objects if o.type=='CURVE']
for old in old_curves:
 k=int(re.search(r'\d+',old.name).group())
 if not any(o.get('chain_index')==k for o in guides.objects):
  guide=old.copy();guide.data=old.data.copy();guide.name='NDI original centerline %02d • non-rendering guide'%k;guide['chain_index']=k;guides.objects.link(guide);guide.hide_render=True;guide.hide_viewport=True
 bpy.data.objects.remove(old,do_unlink=True)
groups={k:[] for k in sorted({int(o.name.split()[1]) for o in BLUE.objects if o.type=='MESH'})}
for o in BLUE.objects:
 if o.type=='MESH':
  k=int(o.name.split()[1]);groups[k].append(o)
  if not o.get('terminal_linkage_aligned',False):o.rotation_euler=(o.rotation_euler.to_matrix().to_4x4()@Matrix.Rotation(-math.pi/2,4,'Z')).to_euler()
  o['terminal_linkage_aligned']=True;o['linkage_axis']='Core-local +/-Y, matching the reference upper/lower N-R directions';o['unit_note']='Four-fused-six-ring NDI core; user-requested conceptual terminal linkage. No specific comonomer inferred.'
bpy.context.view_layer.update()
connectors=[];points_all=[];errors=[];wire=bpy.data.materials['NDI • continuous azure backbone']
for k,units in groups.items():
 units.sort(key=lambda o:o.name)
 ob,points,error=make_terminal_connector('NDI chain %02d • terminal-to-terminal connectors'%k,units,BLUE,wire)
 connectors.append(ob);points_all.extend(points);errors.append(error)
# Geometric checks: every core is inside the gel, every connector tip matches
# its core terminal, and no connector centerline traverses the ring interiors.
bpy.context.view_layer.update();gel=bpy.data.collections['01 • Soft transparent jelly'].objects[0];bvh=BVHTree.FromObject(gel,bpy.context.evaluated_depsgraph_get());inv=gel.matrix_world.inverted()
def inside(p,margin=0):
 co=inv@p;hit=bvh.find_nearest(co)
 return hit[0] is not None and (co-hit[0]).dot(hit[1])<=-margin
outside=[]
for units in groups.values():
 for o in units:
  if not all(inside(o.matrix_world@v.co,.003) for v in o.data.vertices):outside.append(o.name)
if outside:raise RuntimeError('Rotated core outside gel: '+str(outside))
connector_outside=[]
for j,points in enumerate(points_all):
 for p in points:
  if not inside(p,.037):connector_outside.append(j);break
if connector_outside:raise RuntimeError('Connector leaves gel: '+str(connector_outside))
assert mesh_hash(orange)==orange_hash and mesh_hash(core)==core_hash
assert digest(sorted([[list(r) for r in o.matrix_world] for o in ORANGE.objects]))==orange_transforms
assert digest(sorted([list(o.location) for o in BLUE.objects if o.type=='MESH']))==centers_before
# Through-center exclusion in every unit's own coordinates; a small terminal
# overlap is intentional for a seamless solid connection.
interior_passes=[]
for k,units in groups.items():
 points=[Vector(p.co[:3]) for sp in connectors[k-1].data.splines for p in sp.points]
 for o in units:
  oi=o.matrix_world.inverted()
  for p in points:
   q=oi@p
   if abs(q.x)<.11 and abs(q.y)<.195 and abs(q.z)<.065:interior_passes.append(o.name);break
assert not interior_passes,interior_passes
core['scientific_caution']='Simplified NDI four-ring core with user-requested conceptual linkage at both terminal N-R directions; exact comonomer and bond chemistry not specified.'
report={'revision':'ndi-terminal-linkage-v6','core_count':sum(len(u) for u in groups.values()),'connected_terminal_tips':sum(len(u)*2 for u in groups.values()),'core_local_attachment_axis':'+Y / -Y','terminal_tip_max_error':max(errors),'through_ring_center_connector_passes':len(interior_passes),'connector_splines':sum(len(o.data.splines) for o in connectors),'all_rotated_cores_inside_gel':True,'all_connectors_inside_gel_with_radius_margin':True,'ndi_core_mesh_hash_unchanged':core_hash,'pdinn_core_mesh_hash_unchanged':orange_hash,'orange_transforms_unchanged':orange_transforms,'repeat_centers_unchanged':centers_before,'original_path_guides_preserved':len(guides.objects),'linkage_scope':'User-requested conceptual connection at upper/lower N-R directions; no comonomer invented','body_resolution':[1200,720],'samples':48}
with open(R+'/ndi_terminal_validation.json','w') as f:json.dump(report,f,indent=2)
for s in bpy.data.scenes:s['ndi_terminal_linkage']='User-requested upper/lower N-R terminal direction connection, not lateral attachment';s.cycles.samples=48;s.render.resolution_x=1200;s.render.resolution_y=720 if s==body else 800
body.render.filepath='//renders/ndi_terminal_body_1200.png';bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('TERMINAL_VALIDATION',json.dumps(report))
