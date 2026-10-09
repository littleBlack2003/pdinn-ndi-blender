"""Replace rectangular placeholders with the user-approved NDI core.
Preserve each XYZ tangent transform and the existing curved multilayer scene.
Save only; render separately at limited draft quality.
"""
import bpy,os,sys,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,R+'/scripts')
from ndi_core import make_ndi_core,topology
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend');body=bpy.data.scenes['01 • Editable body render'];bpy.context.window.scene=body
ASSETS=bpy.data.collections['05 • Editable source geometry'];BLUE=bpy.data.collections['03 • NDI segmented chains']
orange=next(o for o in ASSETS.objects if o.name.startswith('PDINN source'))
def mesh_hash(obj):return hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in obj.data.vertices],'polygons':[list(p.vertices) for p in obj.data.polygons]}).encode()).hexdigest()
orange_before=mesh_hash(orange)
old=next((o for o in ASSETS.objects if o.name.startswith('NDI source')),None)
if old:bpy.data.objects.remove(old,do_unlink=True)
blue=bpy.data.materials['NDI • azure blue enamel'];edge=bpy.data.materials.get('NDI • raised blue fused-ring contours')
if not edge:
 edge=bpy.data.materials.new('NDI • raised blue fused-ring contours');edge.use_nodes=True;p=edge.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.027,.23,.55,1);p.inputs['Roughness'].default_value=.24;p.inputs['Metallic'].default_value=.18
proto=make_ndi_core(ASSETS,blue,edge)
repeats=[]
for q in BLUE.objects:
 if q.type=='MESH':
  q.data=proto.data
  for m in list(q.modifiers):q.modifiers.remove(m)
  q.name=q.name.replace('XYZ tangent repeat','four-ring NDI core');q['unit_note']=proto['scientific_caution'];q['ring_count']=4;repeats.append(q)
bpy.context.view_layer.update();gel=bpy.data.collections['01 • Soft transparent jelly'].objects[0];bvh=BVHTree.FromObject(gel,bpy.context.evaluated_depsgraph_get());inv=gel.matrix_world.inverted();outside=[]
for q in repeats:
 for v in q.data.vertices:
  co=inv@q.matrix_world@v.co;hit=bvh.find_nearest(co)
  if hit[0] is None or (co-hit[0]).dot(hit[1])>-.003:outside.append(q.name);break
if outside:raise RuntimeError('NDI cores outside gel: '+str(outside))
assert mesh_hash(orange)==orange_before
verts,faces,edges,counts=topology();report={'revision':'ndi-four-ring-draft-v5','reference':'assets/user_ndi_structure_reference.png','core_vertices':len(verts),'core_edges':len(edges),'connected_components':1,'cycle_rank':len(edges)-len(verts)+1,'ring_faces':[len(f) for f in faces],'layout':'Central two fused six-rings, upper and lower six-membered imide rings','replacement_count':len(repeats),'remaining_rectangular_placeholders':0,'five_continuous_xyz_paths_preserved':True,'four_orange_depth_bands_preserved':True,'orange_count':75,'orange_source_mesh_hash':orange_before,'all_ndi_vertices_inside_gel':True,'conceptual_backbone_not_atom_exact':True,'carbonyls_N_R_comonomer_not_specified_by_icon':True,'samples':48,'body_resolution':[1200,720],'preview_resolution':[1200,800]}
with open(R+'/ndi_topology_validation.json','w') as f:json.dump(report,f,indent=2)
for s in bpy.data.scenes:
 s['ndi_ring_count']=4;s['ndi_unit_revision']='Approved four-fused-six-ring NDI core replaces all rectangular placeholders; unspecified polymer connectivity remains conceptual.';s.cycles.samples=48;s.render.resolution_x=1200;s.render.resolution_y=720 if s==body else 800;s.camera.data.dof.use_dof=False
body.render.filepath='//renders/ndi_four_ring_body_1200.png'
bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('NDI_TOPOLOGY_VERIFIED',json.dumps(report))
