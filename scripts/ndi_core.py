"""Approved NDI four-fused-six-ring core, traced from the supplied image.
The central two hexagons share a vertical edge; one imide hexagon sits above
and another below. N-R / carbonyl details are not reproduced in this icon.
Any long polymer path is conceptual and does not assert backbone bond sites.
"""
import bpy, math, json
from math import cos,sin,pi,sqrt

def topology(radius=1):
    centers=[(-sqrt(3)*radius/2,0),(sqrt(3)*radius/2,0),(0,1.5*radius),(0,-1.5*radius)]
    vertices=[];faces=[];lookup={};counts={}
    for x,y in centers:
        face=[]
        for k in range(6):
            a=pi/2+k*pi/3;co=(round(x+radius*cos(a),8),round(y+radius*sin(a),8))
            if co not in lookup:lookup[co]=len(vertices);vertices.append(co)
            face.append(lookup[co])
        faces.append(face)
        for i in range(6):
            e=tuple(sorted((face[i],face[(i+1)%6])));counts[e]=counts.get(e,0)+1
    edges=sorted(counts);assert len(vertices)==16 and len(edges)==19 and len(edges)-len(vertices)+1==4
    return vertices,faces,edges,counts

def make_ndi_core(collection,blue,edge,radius=.09):
    xy,faces,edges,edge_counts=topology(radius);nv=len(xy);height=.085
    verts=[(x,y,z) for z in [-height/2,height/2] for x,y in xy]
    polygons=[tuple(reversed(f)) for f in faces]+[tuple(i+nv for i in f) for f in faces]
    for face in faces:
        for i in range(6):
            a,b=face[i],face[(i+1)%6]
            if edge_counts[tuple(sorted((a,b)))]==1:polygons.append((a,b,b+nv,a+nv))
    me=bpy.data.meshes.new('NDI four-ring extruded fused core');me.from_pydata(verts,[],polygons);me.materials.append(blue);me.update()
    ob=bpy.data.objects.new('NDI source • 4 fused six-membered rings',me);collection.objects.link(ob)
    bv=ob.modifiers.new('Soft enamel perimeter bevel','BEVEL');bv.width=.0045;bv.segments=3;bv.limit_method='ANGLE';ob.modifiers.new('Weighted core normals','WEIGHTED_NORMAL')
    parts=[ob]
    # Draw each unique graph edge once, retaining all four six-sided faces.
    for i,(a,b) in enumerate(edges):
        cu=bpy.data.curves.new('NDI unique ring edge %02d'%i,'CURVE');cu.dimensions='3D';cu.bevel_depth=.007;cu.bevel_resolution=3
        sp=cu.splines.new('POLY');sp.points.add(1)
        for pp,j in zip(sp.points,(a,b)):pp.co=(*xy[j],height/2+.003,1)
        q=bpy.data.objects.new('NDI raised blue ring contour %02d'%i,cu);collection.objects.link(q);cu.materials.append(edge);parts.append(q)
    bpy.ops.object.select_all(action='DESELECT')
    for q in parts:q.select_set(True)
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');bpy.ops.object.join();ob=bpy.context.object
    ob.name='NDI source • 4 fused six-membered rings';ob.hide_render=True;ob.location=(0,0,-10)
    ob['ring_count']=4;ob['ring_sizes']='6,6,6,6';ob['core_graph_vertices']=16;ob['core_graph_edges']=19;ob['core_cycle_rank']=4
    ob['ring_layout']='Two central aromatic rings side by side; upper/lower six-membered imide rings, following the user reference.'
    ob['scientific_caution']='Simplified four-ring NDI core. Atom labels, carbonyl oxygens, N-R substituents, bond order and comonomer omitted. Long connector is a conceptual path, not a specified backbone bond.'
    return ob
