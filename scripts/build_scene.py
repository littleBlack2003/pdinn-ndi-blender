"""Procedural conceptual PDINN/NDI blend, Blender 4.3+. No chemical accuracy implied."""
import bpy, math, random, os, sys, argparse, json
from mathutils import Vector, Quaternion
from math import sin, cos, pi
P=argparse.ArgumentParser(); P.add_argument('--mode',default='preview',choices=['grey','preview','final']); P.add_argument('--width',type=int,default=1200); P.add_argument('--samples',type=int,default=48); P.add_argument('--out',default=None); P.add_argument('--blend-output',default=None); P.add_argument('--skip-render',action='store_true')
a=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); random.seed(41)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials,bpy.data.curves,bpy.data.meshes):
    for d in list(datablocks):
        if d.users==0: datablocks.remove(d)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=a.samples; scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED'; scene.render.threads=8
scene.cycles.max_bounces=10; scene.cycles.transmission_bounces=8; scene.cycles.transparent_max_bounces=8; scene.cycles.volume_bounces=0
scene.cycles.use_light_tree=True
scene.cycles.caustics_reflective=False; scene.cycles.caustics_refractive=False
scene.cycles.sample_clamp_indirect=3.0
scene.render.resolution_x=a.width; scene.render.resolution_y=round(a.width*.60); scene.render.resolution_percentage=100
scene.render.filter_size=1.0
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.render.film_transparent=False
scene.world.color=(.8,.8,.8); scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=-1.0
# Well-organized collections remain editable.
def coll(name):
 c=bpy.data.collections.new(name); scene.collection.children.link(c); return c
GEL=coll('01 • Soft transparent jelly'); ORANGE=coll('02 • PDINN conceptual motifs'); BLUE=coll('03 • NDI segmented chains'); STUDIO=coll('04 • Studio'); ASSETS=coll('05 • Editable source geometry')
def assign(obj,col):
 for c in list(obj.users_collection): c.objects.unlink(obj)
 col.objects.link(obj)
def mat(name,color,rough=.25,metal=.0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
orange=mat('PDINN • warm amber-orange enamel',(.80,.13,.001),.26,.12)
edge=mat('PDINN • golden raised ring edges',(.95,.26,.004),.22,.17)
blue=mat('NDI • azure blue enamel',(.006,.10,.34),.22,.22)
bluewire=mat('NDI • continuous azure backbone',(.009,.12,.38),.26,.13)
white=mat('White matte background',(1,1,1),.7)
grey=mat('Clay composition check',(.52,.56,.62),.55)
jelly=bpy.data.materials.new('Jelly • water-rich soft transmission'); jelly.use_nodes=True
n=jelly.node_tree.nodes; l=jelly.node_tree.links; p=n.get('Principled BSDF')
p.inputs['Base Color'].default_value=(.975,.991,1,1);p.inputs['Roughness'].default_value=.020;p.inputs['IOR'].default_value=1.335;p.inputs['Transmission Weight'].default_value=1;p.inputs['Coat Weight'].default_value=.10;p.inputs['Coat Roughness'].default_value=.025
# Low-frequency, tiny normal variation gives wet soft undulation, not frosted glass.
tex=n.new('ShaderNodeTexNoise');tex.name='Subtle wet surface irregularity';tex.inputs['Scale'].default_value=1.5;tex.inputs['Detail'].default_value=1.5;tex.inputs['Roughness'].default_value=.45
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.025;bump.inputs['Distance'].default_value=.010;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
vol=n.new('ShaderNodeVolumeScatter');vol.inputs['Color'].default_value=(.83,.94,1,1);vol.inputs['Density'].default_value=.0001;vol.inputs['Anisotropy'].default_value=.2;l.new(vol.outputs['Volume'],n.get('Material Output').inputs['Volume'])
clear=n.new('ShaderNodeBsdfTransparent');clear.inputs[0].default_value=(1,1,1,1)
mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.55;l.new(p.outputs['BSDF'],mix.inputs[1]);l.new(clear.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
# Art-directed clear shadows improve internal visibility and suppress refractive caustic noise.
out=n.get('Material Output');lp=n.new('ShaderNodeLightPath');lp.name='Illustration clear shadows';shadowmix=n.new('ShaderNodeMixShader');l.new(lp.outputs['Is Shadow Ray'],shadowmix.inputs[0]);l.new(p.outputs['BSDF'],shadowmix.inputs[1]);l.new(clear.outputs[0],shadowmix.inputs[2]);l.new(shadowmix.outputs[0],out.inputs['Surface'])
# Optional scatter node retained for editing, disconnected in the clarity-first render.
for link in list(out.inputs['Volume'].links):l.remove(link)
# Rounded-box surface sampled per face, welded at seams; micro shape undulation is actual geometry.
verts=[];faces=[];idx={};dims=(6.15,3.30,.51);rad=.47;steps=(64,40,10)
def vtx(p):
 key=tuple(round(v,6) for v in p)
 if key in idx:return idx[key]
 q=Vector([max(-dims[k]+rad,min(dims[k]-rad,p[k])) for k in range(3)]);d=Vector(p)-q
 if d.length>0:q+=d.normalized()*rad
 x,y,z=q;fade=.45+.55*abs(z)/dims[2]
 q.x+=.026*sin(y*.96+z*2.1)*sin(x*.7+.2)
 q.y+=.026*sin(x*.87+z*3.5)
 q.z+=.055*sin(x*.68+.5)*sin(y*1.03+.35)*fade+.018*cos(x*1.5-y*.8)
 i=len(verts);verts.append(tuple(q));idx[key]=i;return i
for axis in range(3):
 other=[i for i in range(3) if i!=axis];u,v=other;nu,nv=steps[u],steps[v]
 for sign in [-1,1]:
  rows=[]
  for j in range(nv+1):
   row=[]
   for i in range(nu+1):
    p=[0,0,0];p[axis]=sign*dims[axis];p[u]=-dims[u]+2*dims[u]*i/nu;p[v]=-dims[v]+2*dims[v]*j/nv;row.append(vtx(p))
   rows.append(row)
  for j in range(nv):
   for i in range(nu):
    f=[rows[j][i],rows[j][i+1],rows[j+1][i+1],rows[j+1][i]]
    # Consistent exterior normals.
    if (Vector(verts[f[1]])-Vector(verts[f[0]])).cross(Vector(verts[f[2]])-Vector(verts[f[0]]))[axis]*sign<0:f.reverse()
    faces.append(f)
mesh=bpy.data.meshes.new('Rounded wet gel mesh • parametric');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Jelly matrix • soft organic rounded slab',mesh);GEL.objects.link(ob);ob.location.z=.61;ob.data.materials.append(grey if a.mode=='grey' else jelly)
for p0 in mesh.polygons:p0.use_smooth=True
sub=ob.modifiers.new('Gentle surface smoothing','SUBSURF');sub.levels=1;sub.render_levels=1
ob['design_note']='Soft conceptual polymer matrix; no bubbles; undulation 0.02–0.05 scene units; refractive index 1.335 for visual softness, not measured material data.'
# Shared motif asset: seven filled fused hexagonal tiles with raised golden contour.
def curve_obj(name,pts,radius,material,col,cyclic=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 sp.use_cyclic_u=cyclic;ob=bpy.data.objects.new(name,cu);col.objects.link(ob);ob.data.materials.append(material);return ob
# Reference-derived seven-ring core; all instances share this editable mesh.
sys.path.insert(0,os.path.join(ROOT,'scripts'))
from pdinn_core import make_pdinn_core
proto=make_pdinn_core(ASSETS,orange,edge)
# Continuous blue chains sampled along analytic smooth paths; evenly spaced blocks by arc length.
chainpaths=[]
for k in range(5):
 y0=-2.6+k*1.25;phase=.68*k
 path=[]
 for i in range(301):
  x=-5.68+11.36*i/300;y=y0+.32*sin(x*.85+phase)+.10*sin(x*1.73-phase);z=.70+.035*sin(x*.88+phase)+.035*(k%2)
  path.append(Vector((x,y,z)))
 chainpaths.append(path)
 wire=curve_obj('NDI chain %02d • continuous curved connector'%(k+1),path,.040,grey if a.mode=='grey' else bluewire,BLUE)
 # actual rounded boxes at roughly constant arc-length increments
 lengths=[0]
 for i in range(1,len(path)):lengths.append(lengths[-1]+(path[i]-path[i-1]).length)
 t=.10;no=0
 while t<lengths[-1]-.12:
  ii=next(i for i,d in enumerate(lengths) if d>=t);fac=(t-lengths[ii-1])/(lengths[ii]-lengths[ii-1]);pos=path[ii-1].lerp(path[ii],fac);tan=(path[min(ii+2,len(path)-1)]-path[max(ii-2,0)]).normalized()
  bpy.ops.mesh.primitive_cube_add(size=1,location=pos);q=bpy.context.object;assign(q,BLUE);q.name='NDI %02d • rounded repeat %02d'%(k+1,no);q.dimensions=(.49,.255,.135);q.rotation_euler=(0,0,math.atan2(tan.y,tan.x));bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);q.data.materials.append(grey if a.mode=='grey' else blue);bv=q.modifiers.new('Soft rounded rectangular segment','BEVEL');bv.width=.058;bv.segments=4;q.modifiers.new('Smooth weighted normals','WEIGHTED_NORMAL');no+=1;t+=.78
# Orange placements avoid blue backbone in XY, with two depth layers and milder rear density.
places=[];attempts=0
while len(places)<51 and attempts<20000:
 attempts+=1;x=random.uniform(-5.52,5.52);y=random.uniform(-2.83,2.83);ang=random.uniform(-.85,.85) if random.random()<.65 else random.uniform(-pi,pi);sc=random.uniform(.92,1.15)
 if any((x-p[0])**2+(y-p[1])**2<.75**2 for p in places):continue
 if min((Vector((x,y,0))-Vector((p.x,p.y,0))).length for path in chainpaths for p in path[::5])<.37:continue
 places.append((x,y,ang,sc))
for k,(x,y,ang,sc) in enumerate(places):
 q=proto.copy();q.data=proto.data;ORANGE.objects.link(q);q.hide_render=False;q.name='PDINN upper • %03d'%(k+1);q.location=(x,y,.69+random.uniform(-.07,.085));q.rotation_euler=(random.uniform(-.12,.12),random.uniform(-.15,.15),ang);q.scale=(sc,sc,sc)
 if a.mode=='grey':q.data=q.data.copy();q.data.materials.clear();q.data.materials.append(grey)
for k in range(24):
 x=random.uniform(-5.6,5.6);y=random.uniform(-2.9,2.9);q=proto.copy();q.data=proto.data;ORANGE.objects.link(q);q.hide_render=False;q.name='PDINN lower depth • %03d'%(k+1);q.location=(x,y,.37);q.rotation_euler=(random.uniform(-.35,.35),random.uniform(-.35,.35),random.uniform(-pi,pi));sc=random.uniform(.7,.90);q.scale=(sc,sc,sc)
 if a.mode=='grey':q.data=q.data.copy();q.data.materials.clear();q.data.materials.append(grey)
# Contain complete icons, including flexible tails, inside the rounded matrix.
for ob in ORANGE.objects:
 ang=ob.rotation_euler.z;sc=ob.scale.x;ex=(.73*abs(cos(ang))+.21*abs(sin(ang)))*sc;ey=(.73*abs(sin(ang))+.21*abs(cos(ang)))*sc
 ob.location.x=max(-5.88+ex,min(5.88-ex,ob.location.x));ob.location.y=max(-3.04+ey,min(3.04-ey,ob.location.y))
# White cyclorama with soft contact shadow.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.015));ground=bpy.context.object;assign(ground,STUDIO);ground.name='Infinite matte white studio';ground.data.materials.append(white)
def light(name,loc,power,size,shape='DISK',size_y=None):
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);STUDIO.objects.link(o);o.location=loc;d.energy=power;d.shape=shape;d.size=size
 if size_y:d.size_y=size_y
 o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler();return o
light('Key • broad softbox upper left',(-4,-1,9),1300,7,'DISK')
light('Edge strip • gel gloss',(-2,6,6),900,8,'RECTANGLE',1.0)
light('Front fill • soft clear interior',(3,-7,5),550,7,'DISK')
light('Right narrow reflection',(8,1,4),650,5,'RECTANGLE',1.0)
camd=bpy.data.cameras.new('Scientific isometric camera');cam=bpy.data.objects.new('Scientific isometric camera',camd);STUDIO.objects.link(cam);cam.location=(1.75,-10.6,15.2);target=Vector((0,0,.52));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=14.4;camd.lens=65;camd.dof.use_dof=False;camd.dof.aperture_fstop=11;scene.camera=cam;camd.clip_end=500
scene['project_description']='PDINN / NDI型聚合物共混示意图 | Soft jelly-style conceptual matrix'
scene['ratio_label']='PDINN : NDI型聚合物 = 1 : 0.3'
scene['scientific_disclaimer']='概念示意，非实际化学结构或实测形貌。配比未指定质量或摩尔基准；图标数不代表配比。'
scene['pdinn_ring_count']=7;scene['ring_topology']='5 central six-membered rings + 2 terminal six-membered imide rings';scene['random_seed']=41;scene['upper_motif_count']=len(places);scene['lower_motif_count']=24;scene['chain_count']=5
# Save before render so each stage is recoverable.
blend=a.blend_output or os.path.join(ROOT,'pdinn_jelly.blend' if a.mode!='grey' else 'checkpoints/composition_grey.blend');bpy.ops.wm.save_as_mainfile(filepath=blend)
scene.render.filepath=a.out or os.path.join(ROOT,'renders',a.mode+'_body.png')
if not a.skip_render:bpy.ops.render.render(write_still=True)
print('SUCCESS',json.dumps({'blend':blend,'render':scene.render.filepath,'motifs_upper':len(places),'mode':a.mode}))
