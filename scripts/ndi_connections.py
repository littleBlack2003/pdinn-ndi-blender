"""Conceptual user-requested linkage at the NDI core's two terminal directions.
Core-local +/-Y tips correspond to the upper/lower N-R directions in the
reference. Connectors bridge tips only; no spline passes through a ring center.
"""
import bpy
from mathutils import Vector
TIP=.225
STUB=.012

def terminal_frame(obj):
 m=obj.matrix_world
 return m@Vector((0,-TIP,0)),m@Vector((0,TIP,0)),(m.to_3x3()@Vector((0,1,0))).normalized()

def connector_points(objects,tail=.14):
 frames=[terminal_frame(o) for o in objects];splines=[];tip_checks=[]
 b,t,d=frames[0];splines.append([b-d*tail,b,b+d*STUB]);tip_checks.append((0,1,b))
 for i in range(len(frames)-1):
  _,a,da=frames[i];b,_,db=frames[i+1];h=(b-a).length/3
  c1=a+da*h;c2=b-db*h;points=[a-da*STUB]
  for k in range(17):
   u=k/16;points.append((1-u)**3*a+3*(1-u)**2*u*c1+3*(1-u)*u*u*c2+u**3*b)
  points.append(b+db*STUB);splines.append(points);tip_checks.extend([(len(splines)-1,1,a),(len(splines)-1,len(points)-2,b)])
 b,t,d=frames[-1];splines.append([t-d*STUB,t,t+d*tail]);tip_checks.append((len(splines)-1,1,t))
 return splines,tip_checks

def make_terminal_connector(name,objects,collection,material,tail=.14,radius=.036):
 points,checks=connector_points(objects,tail)
 cu=bpy.data.curves.new(name+' data','CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=3;cu.use_fill_caps=True
 for spline in points:
  sp=cu.splines.new('POLY');sp.points.add(len(spline)-1)
  for p,co in zip(sp.points,spline):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);collection.objects.link(ob);cu.materials.append(material)
 error=max((Vector(cu.splines[s].points[i].co[:3])-v).length for s,i,v in checks)
 ob['terminal_tip_max_error']=error;ob['terminal_tips_connected']=2*len(objects);ob['linkage_note']='User-requested conceptual attachment at the upper/lower N-R directions. Between-core connectors with only .012 local-unit tip overlap, no through-ring-center spline.'
 return ob,points,error
