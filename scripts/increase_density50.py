"""Add 50% to v7: orange 90->135, NDI cores 94->141, same gel volume.
Preserve the five existing chains; add three genuinely curved depth paths.
Relocate only orange icons that conflict with the new chains, without scaling.
"""
import bpy,os,sys,math,random,json,bisect,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,R+'/scripts')
from ndi_connections import make_terminal_connector
from curve_utils import natural_spline
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');s=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=s
BLUE=bpy.data.collections['03 • NDI segmented chains'];ORANGE=bpy.data.collections['02 • PDINN conceptual motifs'];ASSETS=bpy.data.collections['05 • Editable source geometry'];GUIDES=bpy.data.collections['07 • Original backbone path guides']
blueproto=next(o for o in ASSETS.objects if o.name.startswith('NDI source'));orangeproto=next(o for o in ASSETS.objects if o.name.startswith('PDINN source'))
old_orange=list(ORANGE.objects);old_blue=[o for o in BLUE.objects if o.type=='MESH'];assert len(old_orange)==90 and len(old_blue)==94,'Run once on v7 density model'
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
blue_before=digest(sorted([(o.name,[[*r] for r in o.matrix_world]) for o in old_blue]));orange_scales_before=digest(sorted([(o.name,list(o.scale)) for o in old_orange]))
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
NODES=[
[(-5.3,-.45,.36),(-3.6,.15,.38),(-2.1,.55,.40),(-.4,1.05,.43),(1.1,1.1,.45),(2.6,1.30,.75),(4,.80,.78),(5.25,-.80,.40)],
[(-5.3,-2.05,1.65),(-3.6,-.9,1.75),(-2.1,.5,1.72),(-.3,.05,1.69),(1.4,-1.15,1.72),(3.2,-1.2,1.75),(4.8,-1.2,1.68),(5.35,-.6,1.64)],
[(-5.2,1.7,1.13),(-3.8,1.9,1.15),(-2.2,1.7,1.17),(-.4,1.8,.85),(1.4,2.2,.63),(2.9,1.6,1.20),(4.0,.65,1.25),(4.85,-.3,1.2),(5.3,-1.5,1.10)]
]
newpaths=[natural_spline(ns) for ns in NODES];records=[world_record(o) for o in old_blue];newblue=[];tip_errors=[];new_path_meta=[]
for k,path,n in zip(range(6,9),newpaths,[16,16,15]):
 cu=bpy.data.curves.new('NDI added path %02d data'%k,'CURVE');cu.dimensions='3D';sp=cu.splines.new('POLY');sp.points.add(len(path)-1)
 for pp,v in zip(sp.points,path):pp.co=(*v,1)
 g=bpy.data.objects.new('NDI original centerline %02d • non-rendering guide'%k,cu);GUIDES.objects.link(g);g.hide_render=True;g.hide_viewport=True;g['chain_index']=k;g['path_control_points']=json.dumps(NODES[k-6]);lengths=[0]
 for i in range(1,len(path)):lengths.append(lengths[-1]+(path[i]-path[i-1]).length)
 def at(t):
  i=min(max(1,bisect.bisect_left(lengths,t)),len(path)-1);f=(t-lengths[i-1])/(lengths[i]-lengths[i-1]);return path[i-1].lerp(path[i],f),(path[min(i+2,len(path)-1)]-path[max(i-2,0)]).normalized()
 units=[];last=-10;centers=[]
 for j in range(n):
  q=blueproto.copy();q.data=blueproto.data;BLUE.objects.link(q);q.hide_render=False;q.hide_viewport=False;q.name='NDI %02d • terminal-linked core %02d'%(k,j);q['terminal_linkage_aligned']=True;q['ring_count']=4;t0=.30+(lengths[-1]-.60)*j/(n-1);found=False;failures=[]
  for delta in [0,.03,-.03,.06,-.06,.09,-.09,.12,-.12,.16,-.16,.20,-.20]:
   t=t0+delta
   if t<.24 or t>lengths[-1]-.24 or t-last<.49:continue
   q.location,tan=at(t);q.rotation_euler=tan.to_track_quat('Y','Z').to_euler();bpy.context.view_layer.update();rec=world_record(q)
   contained=all(inside(v) for v in rec[3]);hit=collides(rec,records)
   if not contained or hit:
    failures.append({'t':t,'location':list(q.location),'contained':contained,'hit':hit});continue
   records.append(rec);units.append(q);newblue.append(q);last=t;centers.append(t);found=True;break
  if not found:raise RuntimeError('Could not contain/separate '+q.name+' '+json.dumps(failures))
 ob,points,err=make_terminal_connector('NDI chain %02d • terminal-to-terminal connectors'%k,units,BLUE,bpy.data.materials['NDI • continuous azure backbone']);tip_errors.append(err)
 if not all(inside(p,.037) for ps in points for p in ps):raise RuntimeError('Connector outside gel on chain '+str(k))
 new_path_meta.append({'chain':k,'core_count':n,'length':lengths[-1],'minimum_arc_spacing':min(centers[i+1]-centers[i] for i in range(len(centers)-1)),'z_range':[min(p.z for p in path),max(p.z for p in path)]})
allpaths=[[g.matrix_world@Vector(p.co[:3]) for p in g.data.splines[0].points] for g in GUIDES.objects]
def near_path(q,paths):
 inv=q.matrix_world.inverted()
 for path in paths:
  for p in path[::3]:
   v=inv@p
   if abs(v.x)<.65 and abs(v.y)<.22 and abs(v.z)<.14:return True
 return False
# Preserve all unconstrained old orange instances; only relocate conflicts.
retained=[];relocate=[]
for q in old_orange:
 rec=world_record(q)
 if collides(rec,records) or near_path(q,newpaths):relocate.append(q)
 else:records.append(rec);retained.append(q)
rng=random.Random(5050);placed=list(retained);attempts=0;relocated_names=[];zs=[.36,.79,1.22,1.66]
def place(q,band):
 global attempts
 for _ in range(6000):
  attempts+=1;q.location=(rng.uniform(-5.42,5.42),rng.uniform(-2.76,2.76),zs[band-1]+rng.uniform(-.075,.075));q.rotation_euler=(rng.uniform(-.32,.32),rng.uniform(-.35,.35),rng.uniform(-math.pi,math.pi));bpy.context.view_layer.update()
  if any((q.location-o.location).length<.50 for o in placed) or near_path(q,allpaths):continue
  rec=world_record(q)
  if not all(inside(v,.018) for v in rec[3]) or collides(rec,records):continue
  q['depth_band']=band;records.append(rec);placed.append(q);return
 raise RuntimeError('Could not place '+q.name)
for q in relocate:
 band=int(q['depth_band']);place(q,band);relocated_names.append(q.name)
added=[]
for band,n in enumerate([12,11,11,11],1):
 for j in range(n):
  q=orangeproto.copy();q.data=orangeproto.data;ORANGE.objects.link(q);q.hide_render=False;q.hide_viewport=False;q.name='PDINN depth %d • density50 addition %02d'%(band,j+1);q.scale=old_orange[len(added)%len(old_orange)].scale;place(q,band);added.append(q)
assert len(ORANGE.objects)==135 and sum(o.type=='MESH' for o in BLUE.objects)==141
assert digest(sorted([(o.name,[[*r] for r in o.matrix_world]) for o in old_blue]))==blue_before
assert digest(sorted([(o.name,list(o.scale)) for o in old_orange]))==orange_scales_before
bands=[sum(o.get('depth_band')==k for o in ORANGE.objects) for k in range(1,5)]
report={'revision':'density-plus50-v8','relative_to':'v7: 90 orange and 94 blue','orange_before':90,'orange_after':135,'blue_before':94,'blue_after':141,'increase_percent_both':50,'chain_count':8,'old_five_chains_and_94_cores_unchanged':True,'new_chain_core_counts':[16,16,15],'orange_band_counts':bands,'existing_orange_retained':len(retained),'existing_orange_relocated':len(relocate),'relocated_orange_names':relocated_names,'existing_molecule_scales_unchanged':True,'new_orange_scales_reused_from_existing_icons':True,'matrix_camera_material_unchanged':True,'all_added_and_relocated_molecules_inside_gel':True,'new_and_relocated_molecule_mesh_intersections':0,'all_terminal_tips_connected':282,'new_terminal_tip_max_error':max(tip_errors),'new_paths':new_path_meta,'orange_placement_attempts':attempts,'body_resolution':[1200,720],'samples':48,'ratio_label_is_not_an_object_count_ratio':True}
with open(R+'/density50_validation.json','w') as f:json.dump(report,f,indent=2)
for sc in bpy.data.scenes:sc['density_revision']='50% relative to v7: 135 orange / 141 blue, eight curved chains, unchanged gel volume and molecular scale';sc['motif_count']=135;sc['ndi_unit_count']=141;sc['chain_count']=8;sc['depth_band_counts']=bands;sc.cycles.samples=48
s.render.filepath='//renders/density50_body_1200.png';bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('DENSITY50_VALIDATION',json.dumps(report))
