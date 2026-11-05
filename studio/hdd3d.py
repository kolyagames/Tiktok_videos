"""3D-модель жёсткого диска (процедурная): крышка цветной линейки слетает, внутри вращается пластина.
python3 hdd3d.py OUTDIR R G B [frames] [size] [samples]  -> OUTDIR/f0001.png (прозрачный фон)"""
import bpy, math, os, sys
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
col = tuple(float(x) / 255 for x in sys.argv[2:5]) + (1,)
N = int(sys.argv[5]) if len(sys.argv) > 5 else 96
S = int(sys.argv[6]) if len(sys.argv) > 6 else 360
SM = int(sys.argv[7]) if len(sys.argv) > 7 else 6
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SM; sc.cycles.use_denoising = True
sc.render.resolution_x = S; sc.render.resolution_y = S; sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
def mat(c, rough=0.4, metal=0.0, emit=0):
    m = bpy.data.materials.new('m'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = c; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = c; b.inputs['Emission Strength'].default_value = emit
    return m
def box(sz, loc, m, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = sz; o.data.materials.append(m)
    bv = o.modifiers.new('b', 'BEVEL'); bv.width = bevel; bv.segments = 3; return o
root = bpy.data.objects.new('root', None); sc.collection.objects.link(root)
base = box((1.0, 1.45, 0.16), (0, 0, 0), mat((0.55, 0.57, 0.6, 1), 0.35, 0.9)); base.parent = root
inner = box((0.9, 1.35, 0.1), (0, 0, 0.07), mat((0.08, 0.08, 0.1, 1), 0.6)); inner.parent = root
# пластина
bpy.ops.mesh.primitive_cylinder_add(radius=0.46, depth=0.02, location=(0, -0.1, 0.14), vertices=64); plat = bpy.context.object
plat.data.materials.append(mat((0.85, 0.87, 0.9, 1), 0.08, 1.0)); plat.parent = root
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.04, location=(0, -0.1, 0.15), vertices=32); hub = bpy.context.object; hub.data.materials.append(mat((0.3, 0.3, 0.33, 1), 0.3, 1)); hub.parent = root
# рычаг
pivot = bpy.data.objects.new('piv', None); sc.collection.objects.link(pivot); pivot.location = (0.36, -0.52, 0.15); pivot.parent = root
arm = box((0.62, 0.05, 0.02), (-0.3, 0, 0), mat((0.7, 0.72, 0.75, 1), 0.3, 0.9), 0.005); arm.parent = pivot
tip = box((0.06, 0.08, 0.025), (-0.6, 0, 0), mat((0.15, 0.15, 0.17, 1), 0.5), 0.005); tip.parent = pivot
# крышка цветной линейки (метка, без логотипов)
lid = bpy.data.objects.new('lid', None); sc.collection.objects.link(lid)
lb = box((1.0, 1.45, 0.05), (0, 0, 0), mat(col, 0.3, 0.2), 0.02); lb.parent = lid
lab = box((0.7, 0.45, 0.01), (0, 0.35, 0.03), mat((0.96, 0.96, 0.98, 1), 0.5), 0.003); lab.parent = lid
for k in range(3): box((0.5 - k * 0.1, 0.03, 0.012), (0, 0.45 - k * 0.1, 0.04), mat((0.2, 0.2, 0.25, 1), 0.5), 0.002).parent = lid
def light(kind, loc, e, rot):
    d = bpy.data.lights.new('l', kind); d.energy = e; ob = bpy.data.objects.new('l', d); sc.collection.objects.link(ob); ob.location = loc; ob.rotation_euler = rot
    if kind == 'AREA': d.size = 4
light('AREA', (3, -4, 6), 600, (0.8, 0.2, 0.5)); light('AREA', (-4, -2, 3), 250, (1.1, 0, -1.0))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 40
tg = bpy.data.objects.new('t', None); sc.collection.objects.link(tg); tg.location = (0, 0, 0.3)
c = cam.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
for f in range(N):
    t = f / N                                        # 0..1 один цикл
    enter = ease(t / 0.2)
    root.location = (0, 0, 0.18 * math.sin(t * 2 * math.pi))                       # парит
    root.rotation_euler = (0.25, 0, math.radians(-40 + 80 * t))                     # медленный разворот
    root.scale = [0.4 + 0.6 * enter] * 3
    lift = ease((t - 0.18) / 0.25)
    lid.parent = root; lid.location = (0, 0, 0.14 + 1.0 * lift); lid.rotation_euler = (0.0, 0.5 * lift * math.sin(t * 6), math.radians(25 * lift * math.sin(t * 5)))
    plat.rotation_euler = (0, 0, -t * 2 * math.pi * 18); hub.rotation_euler = plat.rotation_euler
    pivot.rotation_euler = (0, 0, math.radians(18 * math.sin(t * 2 * math.pi * 3)))
    ang = math.radians(35 + 10 * math.sin(t * 2 * math.pi)); cam.location = (4.3 * math.sin(ang), -4.3 * math.cos(ang), 2.6)
    sc.render.filepath = os.path.join(out, 'f%04d.png' % (f + 1)); bpy.ops.render.render(write_still=True)
print('DONE')
