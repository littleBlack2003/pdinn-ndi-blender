"""Apply exact user-supplied sRGB colors to the molecular materials.
Blender shader Base Color inputs are scene-linear, so decode sRGB first.
"""
import bpy,os,json
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend')
def linear_hex(value):
 v=[int(value[i:i+2],16)/255 for i in (1,3,5)]
 return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
colors={'#F0B47C':['PDINN • warm amber-orange enamel','PDINN • golden raised ring edges'],'#BE7A9A':['NDI • azure blue enamel','NDI • continuous azure backbone','NDI • raised blue fused-ring contours']}
changed=[]
for hexc,names in colors.items():
 linear=linear_hex(hexc)
 for name in names:
  m=bpy.data.materials[name];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*linear,1);m.diffuse_color=(*linear,1);m['requested_srgb_hex']=hexc;m['color_space_note']='Exact sRGB user color decoded to scene-linear for shader input';changed.append({'material':name,'srgb_hex':hexc,'linear_rgb':linear})
for s in bpy.data.scenes:s['pdinn_requested_srgb_hex']='#F0B47C';s['polymer_requested_srgb_hex']='#BE7A9A';s['palette_note']='Exact Base Colors; physical lighting, reflections and gel transmission alter displayed pixel values.'
assert len(bpy.data.collections['02 • PDINN conceptual motifs'].objects)==135
assert sum(o.type=='MESH' for o in bpy.data.collections['03 • NDI segmented chains'].objects)==141
report={'revision':'density50-requested-palette','pdinn_srgb':'#F0B47C','polymer_srgb':'#BE7A9A','materials':changed,'orange_count':135,'polymer_core_count':141,'chain_count':8,'geometry_unchanged':True,'jelly_and_studio_materials_unchanged':True,'pixel_note':'Rendered values vary with lighting, highlights, shadows and gel transmission.'}
with open(R+'/palette_validation.json','w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/pdinn_jelly.blend');print('PALETTE_APPLIED',json.dumps(report))
