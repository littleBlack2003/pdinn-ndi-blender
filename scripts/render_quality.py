"""Render the saved editable scene without rebuilding it."""
import bpy,os,sys,argparse
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p=argparse.ArgumentParser();p.add_argument('--width',type=int,default=1200);p.add_argument('--samples',type=int,default=48);p.add_argument('--output',default='PDINN_Jelly_Clear_Draft.png');p.add_argument('--poster',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=R+'/pdinn_jelly.blend')
s=bpy.data.scenes.get('02 • Native Chinese poster' if a.poster else '01 • Editable body render') or bpy.context.scene;bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.065;s.cycles.adaptive_min_samples=min(16,a.samples)
s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False;s.cycles.sample_clamp_indirect=3;s.cycles.volume_bounces=0
s.camera.data.dof.use_dof=False;s.render.filter_size=1.0;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*(2/3 if a.poster else .6));s.render.resolution_percentage=100
s.render.filepath=os.path.join(R,'renders',a.output);bpy.ops.render.render(write_still=True)
print('Draft render saved:',s.render.filepath)
