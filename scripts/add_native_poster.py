"""Add a second native Blender scene with packed, editable Chinese typography.
The external compositor remains the recommended precision-print layout.
"""
import bpy, os, math
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend')
for old in list(bpy.data.scenes):
 if old.name.startswith('02 • Native Chinese poster'):bpy.data.scenes.remove(old)
for old in list(bpy.data.collections):
 if old.name.startswith('06 • Native editable Chinese poster labels'):bpy.data.collections.remove(old)
body=bpy.context.scene;body.name='01 • Editable body render'
poster=body.copy();poster.use_fake_user=True;poster.name='02 • Native Chinese poster';poster.render.resolution_x=4096;poster.render.resolution_y=2731
camera=body.camera.copy();camera.data=body.camera.data.copy();poster.collection.objects.link(camera);camera.name='Poster framing camera';camera.data.ortho_scale=15.6;poster.camera=camera
texts=bpy.data.collections.new('06 • Native editable Chinese poster labels');poster.collection.children.link(texts)
mat=bpy.data.materials.new('Poster typography • deep navy emission');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.003,.013,.07,1);em.inputs[1].default_value=1;mat.node_tree.links.new(em.outputs[0],o.inputs[0])
quat=camera.rotation_euler.to_quaternion();right=quat@Vector((1,0,0));up=quat@Vector((0,1,0));forward=quat@Vector((0,0,-1));base=camera.location+forward*8
bold=bpy.data.fonts.load(R+'/assets/PDINNPosterSansSC-Bold.otf');reg=bpy.data.fonts.load(R+'/assets/PDINNPosterSansSC-Regular.otf')
for font in [bold,reg]:font.pack()
def text(name,words,x,y,size,font,width=None):
 cu=bpy.data.curves.new(name,'FONT');cu.body=words;cu.size=size;cu.align_x='CENTER';cu.font=font;cu.space_character=1.03;cu.extrude=0
 ob=bpy.data.objects.new(name,cu);texts.objects.link(ob);ob.location=base+right*x+up*y;ob.rotation_euler=camera.rotation_euler;ob.data.materials.append(mat)
 bpy.context.view_layer.update()
 if width and ob.dimensions.x>width:ob.scale*=width/ob.dimensions.x
 return ob
text('Title • editable Chinese','PDINN / NDI型聚合物共混示意图',0,4.4,.52,bold,14.6)
text('Ratio label • not object counts','PDINN : NDI型聚合物 = 1 : 0.3',0,3.83,.41,bold,13.5)
text('Legend • PDINN','PDINN 小分子',-3.0,-4.05,.36,bold)
text('Legend • NDI','NDI型聚合物',3.2,-4.05,.36,bold)
text('Concept disclaimer','概念示意，非实际化学结构或实测形貌',0,-4.72,.25,reg)
# Add matching image key as packed camera-facing PNG plane; the source 3D geometry is in scene 01.
def icon(name,path,x,y,w,h):
 image=bpy.data.images.load(path);image.pack();m=bpy.data.materials.new(name+' material');m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');tx=n.new('ShaderNodeTexImage');tx.image=image;tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');L=m.node_tree.links;L.new(tx.outputs['Color'],em.inputs[0]);L.new(tx.outputs['Alpha'],mix.inputs[0]);L.new(tr.outputs[0],mix.inputs[1]);L.new(em.outputs[0],mix.inputs[2]);L.new(mix.outputs[0],out.inputs[0])
 me=bpy.data.meshes.new(name+' plane');me.from_pydata([(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)],[],[(0,1,2,3)]);me.uv_layers.new()
 for poly in me.polygons:
  for li,uv in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):me.uv_layers.active.data[li].uv=uv
 ob=bpy.data.objects.new(name,me);texts.objects.link(ob);ob.data.materials.append(m);ob.location=base+right*x+up*y;ob.rotation_euler=camera.rotation_euler
if os.path.exists(R+'/assets/legend_pdinn.png'):icon('Legend rendered orange icon',R+'/assets/legend_pdinn.png',-5,-3.98,1.65,.55)
if os.path.exists(R+'/assets/legend_ndi.png'):icon('Legend rendered blue key',R+'/assets/legend_ndi.png',.62,-3.98,2.2,.73)
poster['typography_note']='Native editable text with packed subset CJK fonts. Poster key PNGs are packed; full 3D source is retained. Precision layout source is compose_poster.py + SVG.'
# Preserve the body scene as default; all assets are packed for portable use.
bpy.context.window.scene=body
for sc in [body,poster]:
 sc.render.filepath='//renders/'+('final_body.png' if sc==body else 'native_poster.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend')
print('Native poster scene, packed fonts, packed key images added.')
