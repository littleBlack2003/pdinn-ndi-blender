"""Seven-ring PDINN/PDI visual core traced from the supplied reference.
Five central six-membered rings plus two six-membered terminal imide rings.
The reference's terminal imides are SIX-membered; do not replace with pentagons.
This graphic retains ring fusion and N-side-chain attachment direction but omits
atom labels, bond orders and full side-chain chemistry. It is still conceptual.
"""
import bpy, math
from math import cos,sin,pi,sqrt

def make_pdinn_core(collection,orange,edge):
    parts=[];r=.108;h=.044
    centers=[(-3*r,0),(-1.5*r,sqrt(3)*r/2),(-1.5*r,-sqrt(3)*r/2),(0,0),(1.5*r,sqrt(3)*r/2),(1.5*r,-sqrt(3)*r/2),(3*r,0)]
    def curve(name,pts,radius,cyclic=False):
        cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
        for p,co in zip(sp.points,pts):p.co=(*co,1)
        sp.use_cyclic_u=cyclic;ob=bpy.data.objects.new(name,cu);collection.objects.link(ob);ob.data.materials.append(edge);parts.append(ob);return ob
    for j,(x,y) in enumerate(centers):
        coords=[(x+r*cos(k*pi/3),y+r*sin(k*pi/3),z) for z in [-h/2,h/2] for k in range(6)]
        fs=[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(k,(k+1)%6,(k+1)%6+6,k+6) for k in range(6)]
        me=bpy.data.meshes.new('PDINN ring %d • six-membered'%(j+1));me.from_pydata(coords,[],fs);me.materials.append(orange);ob=bpy.data.objects.new('PDINN terminal imide' if j in [0,6] else 'PDINN perylene central ring',me);collection.objects.link(ob);bv=ob.modifiers.new('Soft ring bevel','BEVEL');bv.width=.008;bv.segments=3;ob.modifiers.new('Weighted ring normals','WEIGHTED_NORMAL');parts.append(ob)
        curve('PDINN ring %d • raised contour'%(j+1),[(x+r*cos(k*pi/3),y+r*sin(k*pi/3),h/2+.004) for k in range(6)],.010,True)
    # Both terminal N sites are the extreme left/right vertices after rotating
    # the reference 30 degrees clockwise; tails connect continuously there.
    for sign in [-1,1]:
        pts=[]
        for i in range(33):
            t=i/32;pts.append((sign*(4*r+.29*t),sign*(.042*sin(t*pi*2)-.012*t),.004+.018*sin(t*pi)))
        curve('PDINN • N-side-chain conceptual tail',pts,.023)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();proto=bpy.context.object;proto.name='PDINN source • 7 fused six-membered rings';proto.location=(0,0,-8);proto.hide_render=True
    proto['ring_count']=7;proto['central_ring_count']=5;proto['terminal_imide_ring_count']=2;proto['ring_sizes']='6,6,6,6,6,6,6';proto['scientific_caution']='Ring fusion traced from the user image. Atoms, bond order, carbonyl oxygens and full side-chain chemistry omitted: conceptual graphic, not a complete structural formula.'
    return proto
