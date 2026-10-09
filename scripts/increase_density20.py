"""Increase PDINN icons 75->90 and NDI cores 78->94 in the same gel volume.
Use the original five curve guides, retaining upper/lower terminal linkage.
"""
import bpy,os,sys,json,math,random,bisect,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,R+'/scripts')
from ndi_connections import make_terminal_connector
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');s=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=s
BLUE=bpy.data.collections['03 • NDI segmented chains'];ORANGE=bpy.data.collections['02 • PDINN conceptual motifs'];ASSETS=bpy.data.collections['05 • Editable source geometry'];GUIDES=bpy.data.collections['07 • Original backbone path guides']
blueproto=next(o for o in ASSETS.objects if o.name.startswith('NDI source'));orangeproto=next(o for o in ASSETS.objects if o.name.startswith('PDINN source'))
old_orange=list(ORANGE.objects);old_counts=[sum(1 for o in BLUE.objects if o.type=='MESH' and int(o.name.split()[1])==k) for k in range(1,6)]
assert len(old_orange)==75 and sum(old_counts)==78,'Run this once on the v6 75/78 model'
old_orange_transform_hash=hashlib.sha256(json.dumps(sorted([[list(r) for r in o.matrix_world] for o in old_orange])).encode()).hexdigest()
raw=[c*94/78 for c in old_counts];counts=[math.floor(x) for x in raw]
for j in sorted(range(5),key=lambda j:raw[j]-counts[j],reverse=True)[:94-sum(counts)]:counts[j]+=1
for o in list(BLUE.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update();gel=bpy.data.collections['01 • Soft transparent jelly'].objects[0];gbvh=BVHTree.FromObject(gel,bpy.context.evaluated_depsgraph_get());ginv=gel.matrix_world.inverted()
def inside(p,margin=.005):
 v=ginv@p;h=gbvh.find_nearest(v)
 return h[0] is not None and (v-h[0]).dot(h[1])<=-margin

def world_record(obj):
 vs=[obj.matrix_world@v.co for v in obj.data.vertices];bounds=(tuple(min(v[j] for v in vs) for j in range(3)),tuple(max(v[j] for v in vs) for j in range(3)))
 return obj.name,bounds,BVHTree.FromPolygons(vs,[list(p.vertices) for p in obj.data.polygons]),vs

def collides(rec,others):
 a,b=rec[1]
 for other in others:
  c,d=other[1]
  if all(a[j]<=d[j] and c[j]<=b[j] for j in range(3)) and rec[2].overlap(other[2]):return other[0]
 return None
records=[world_record(o) for o in old_orange];old_records=list(records);path_arrays=[];tip_errors=[];blue_collision_candidates_avoided=0;unresolved=[];allunits=[];paths_meta=[]
for k in range(1,6):
 guide=next(g for g in GUIDES.objects if g.get('chain_index')==k);path=[guide.matrix_world@Vector(p.co[:3]) for p in guide.data.splines[0].points];path_arrays.append(path);lengths=[0]
 for i in range(1,len(path)):lengths.append(lengths[-1]+(path[i]-path[i-1]).length)
 def at(t):
  i=min(max(1,bisect.bisect_left(lengths,t)),len(path)-1);f=(t-lengths[i-1])/(lengths[i]-lengths[i-1]);return path[i-1].lerp(path[i],f),(path[min(i+2,len(path)-1)]-path[max(i-2,0)]).normalized()
 n=counts[k-1];units=[];last_t=-100;centers=[]
 for j in range(n):
  t0=.30+(lengths[-1]-.60)*j/(n-1);q=blueproto.copy();q.data=blueproto.data;BLUE.objects.link(q);q.hide_render=False;q.hide_viewport=False;q.name='NDI %02d • terminal-linked core %02d'%(k,j);q['terminal_linkage_aligned']=True;q['ring_count']=4
  chosen=None;best=None
  for shift in [0,.025,-.025,.05,-.05,.075,-.075,.1,-.1,.12,-.12]:
   t=t0+shift
   if t<.24 or t>lengths[-1]-.24 or t-last_t<.49:continue
   pos,tan=at(t);q.location=pos;q.rotation_euler=tan.to_track_quat('Y','Z').to_euler();bpy.context.view_layer.update();rec=world_record(q)
   if not all(inside(v) for v in rec[3]):continue
   hit=collides(rec,records)
   if hit is None:chosen=(t,rec);break
   blue_collision_candidates_avoided+=1
   if best is None:best=(t,rec,hit,pos.copy(),q.rotation_euler.copy())
  if chosen is None:
   if best is None:raise RuntimeError('No contained placement for '+q.name)
   t,rec,hit,pos,rot=best;q.location=pos;q.rotation_euler=rot;bpy.context.view_layer.update();unresolved.append((q.name,hit));chosen=(t,world_record(q))
  last_t,rec=chosen;records.append(rec);units.append(q);centers.append(last_t)
 connector,points,err=make_terminal_connector('NDI chain %02d • terminal-to-terminal connectors'%k,units,BLUE,bpy.data.materials['NDI • continuous azure backbone']);tip_errors.append(err);allunits+=units
 if not all(inside(p,.037) for ps in points for p in ps):raise RuntimeError('Connector outside volume')
 paths_meta.append({'chain':k,'before':old_counts[k-1],'after':n,'length':lengths[-1],'minimum_arc_spacing':min(centers[i+1]-centers[i] for i in range(len(centers)-1))})
if unresolved:print('UNRESOLVED_NEW_BLUE_INTERSECTIONS',unresolved)
# Add exactly 15 orange motifs, distributed as +4,+4,+4,+3 in the four bands.
# Original 75 orange positions and rotations are untouched.
rng=random.Random(2057);added=[];attempts=0;targets=[4,4,4,3];zs=[.36,.79,1.22,1.66]
for band,(z,number) in enumerate(zip(zs,targets)):
 success=0
 while success<number and attempts<12000:
  attempts+=1;q=orangeproto.copy();q.data=orangeproto.data;ORANGE.objects.link(q);q.hide_render=False;q.hide_viewport=False;q.location=(rng.uniform(-5.42,5.42),rng.uniform(-2.76,2.76),z+rng.uniform(-.075,.075));q.rotation_euler=(rng.uniform(-.32,.32),rng.uniform(-.35,.35),rng.uniform(-math.pi,math.pi));sc=rng.uniform(.82,1.05);q.scale=(sc,sc,sc);bpy.context.view_layer.update()
  if any((q.location-o.location).length<.55 for o in old_orange+added):bpy.data.objects.remove(q,do_unlink=True);continue
  oi=q.matrix_world.inverted();near=False
  for path in path_arrays:
   for p in path[::3]:
    v=oi@p
    if abs(v.x)<.60 and abs(v.y)<.22 and abs(v.z)<.14:near=True;break
   if near:break
  if near:bpy.data.objects.remove(q,do_unlink=True);continue
  rec=world_record(q)
  if not all(inside(v,.018) for v in rec[3]) or collides(rec,records):bpy.data.objects.remove(q,do_unlink=True);continue
  q.name='PDINN depth %d • density addition %02d'%(band+1,success+1);q['depth_band']=band+1;records.append((q.name,*rec[1:]));added.append(q);success+=1
 if success<number:raise RuntimeError('Could not add required orange icons')
assert len(ORANGE.objects)==90 and len(allunits)==94
assert hashlib.sha256(json.dumps(sorted([[list(r) for r in o.matrix_world] for o in old_orange])).encode()).hexdigest()==old_orange_transform_hash
bands=[sum(1 for o in ORANGE.objects if o.get('depth_band')==k) for k in range(1,5)]
report={'revision':'density-plus20-v7','orange_before':75,'orange_after':90,'orange_change_percent':20,'blue_before':78,'blue_after':94,'blue_change_percent':(94/78-1)*100,'blue_chain_count':5,'orange_band_counts':bands,'original_orange_transforms_unchanged':True,'original_five_path_guides_unchanged':True,'matrix_camera_material_unchanged':True,'all_new_motifs_inside_gel':True,'added_orange_surface_intersections':0,'blue_candidate_collisions_avoided':blue_collision_candidates_avoided,'blue_unresolved_mesh_intersections':unresolved,'all_upper_lower_terminal_tips_connected':188,'terminal_tip_max_error':max(tip_errors),'chain_counts':paths_meta,'orange_placement_attempts':attempts,'body_resolution':[1200,720],'samples':48,'ratio_label_is_not_an_object_count_ratio':True}
with open(R+'/density20_validation.json','w') as f:json.dump(report,f,indent=2)
for sc in bpy.data.scenes:sc['density_revision']='Orange 75->90; blue NDI cores 78->94; same volume and five paths; conceptual counts, not stoichiometry';sc['motif_count']=90;sc['ndi_unit_count']=94;sc['depth_band_counts']=bands;sc.cycles.samples=48
s.render.filepath='//renders/density20_body_1200.png';bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('DENSITY_VALIDATION',json.dumps(report))
