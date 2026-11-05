"""3D-сцена: блоки падают и собирают портал, камера облетает и влетает внутрь.
python3 portal3d.py OUTDIR [W H FPS SAMPLES]  -> OUTDIR/f0001.png ... + OUTDIR/events.json
"""
import bpy, math, json, os, sys, random

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
W = int(sys.argv[2]) if len(sys.argv) > 2 else 540
H = int(sys.argv[3]) if len(sys.argv) > 3 else 960
FPS = int(sys.argv[4]) if len(sys.argv) > 4 else 30
SAMPLES = int(sys.argv[5]) if len(sys.argv) > 5 else 24
DUR = 7.0
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.fps = FPS
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [v.identifier for v in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Standard'

sc.view_settings.exposure = -1.3
def mat(name, col, rough=0.5, emit=0.0, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col; b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = col; b.inputs['Emission Strength'].default_value = emit
    return m

# мир: тёмный градиент
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.03, 0.02, 0.03, 1); bg.inputs[1].default_value = 0.15

# пол
bpy.ops.mesh.primitive_plane_add(size=80, location=(1.5, 0, -0.5))
floor = bpy.context.object; floor.data.materials.append(mat('floor', (0.07, 0.07, 0.08, 1), rough=0.7))

# блоки рамки
cells = [(x, 0) for x in range(4)] + [(x, z) for z in (1, 2, 3) for x in (0, 3)] + [(x, 4) for x in range(4)]
random.seed(4)
mats = [mat('o1', (0.16, 0.16, 0.18, 1), 0.85), mat('o2', (0.11, 0.11, 0.13, 1), 0.9), mat('o3', (0.18, 0.16, 0.14, 1), 0.85)]
cubes = []; events = []
T0, STEP = 0.5, 0.15
for i, (x, z) in enumerate(cells):
    bpy.ops.mesh.primitive_cube_add(size=0.96)
    c = bpy.context.object; c.data.materials.append(random.choice(mats))
    bv = c.modifiers.new('b', 'BEVEL'); bv.width = 0.05; bv.segments = 3
    t_land = T0 + i * STEP; cubes.append((c, x, z, t_land)); events.append(t_land)

# портал
bpy.ops.mesh.primitive_plane_add(size=1)
pl = bpy.context.object; pl.rotation_euler = (math.pi / 2, 0, 0); pl.location = (1.5, 0, 2)
pm = bpy.data.materials.new('portal'); pm.use_nodes = True; nt = pm.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
tc = nt.nodes.new('ShaderNodeTexCoord'); no = nt.nodes.new('ShaderNodeTexNoise'); no.noise_dimensions = '4D'
no.inputs['Scale'].default_value = 5; no.inputs['Detail'].default_value = 4
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.7, 0.12, 0.0, 1); ramp.color_ramp.elements[1].color = (1.0, 0.75, 0.25, 1)
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 0
o = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tc.outputs['Object'], no.inputs['Vector']); nt.links.new(no.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs[0], o.inputs[0])
pl.data.materials.append(pm)
T_PORTAL = T0 + len(cells) * STEP + 0.25   # ~2.9 c
events.append(T_PORTAL)

# свет
def light(kind, loc, energy, color=(1, 1, 1), rot=None, size=None):
    d = bpy.data.lights.new('l', kind); d.energy = energy; d.color = color
    if size: d.size = size
    ob = bpy.data.objects.new('l', d); sc.collection.objects.link(ob); ob.location = loc
    if rot: ob.rotation_euler = rot
    return ob
light('AREA', (-4, -6, 8), 160, (0.5, 0.65, 1), (0.8, 0, -0.5), 6)
light('AREA', (7, -5, 3), 120, (0.4, 0.6, 1), (1.2, 0, 0.9), 5)
pl_light = light('POINT', (1.5, -1.5, 2), 0, (1.0, 0.5, 0.15))
torches = []
for tx in (-1.6, 4.6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(tx, -0.8, 0.5)); st = bpy.context.object; st.scale = (0.18, 0.18, 1.8); st.data.materials.append(mat('wood', (0.12, 0.07, 0.03, 1), 0.9))
    bpy.ops.mesh.primitive_cube_add(size=0.34, location=(tx, -0.8, 1.55)); fl = bpy.context.object; fl.data.materials.append(mat('fire', (1.0, 0.45, 0.05, 1), 0.5, emit=12))
    torches.append((fl, light('POINT', (tx, -1.0, 1.7), 150, (1.0, 0.5, 0.15))))

# камера
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 34
tgt = bpy.data.objects.new('t', None); sc.collection.objects.link(tgt)
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'

def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)

def shake(t):
    s = 0
    for e in events[:-1]:
        d = t - e
        if 0 <= d < 0.35: s += 0.05 * math.exp(-d * 9) * math.sin(d * 70)
    return s

N = int(DUR * FPS)
for f in range(N):
    t = f / FPS
    # блоки
    for c, x, z, tl in cubes:
        drop = 0.38
        if t < tl - drop: c.hide_render = True; continue
        c.hide_render = False
        u = (t - (tl - drop)) / drop
        if u < 1:
            h = 14 * (1 - u * u)  # ускоряется вниз
            c.location = (x, 0, z + h); c.scale = (1, 1, 1); c.rotation_euler = (0.6 * (1 - u), 0.4 * (1 - u), 0)
        else:
            d = t - tl
            bounce = 0.12 * math.exp(-d * 9) * abs(math.sin(d * 22))
            sq = 1 - 0.25 * math.exp(-d * 14)
            c.location = (x, 0, z + bounce); c.rotation_euler = (0, 0, 0); c.scale = (1 + (1 - sq) * 0.5, 1 + (1 - sq) * 0.5, sq)
    # портал
    up = ease((t - T_PORTAL) / 0.6)
    pl.scale = (2.0 * up, 3.0 * up, 1)
    em.inputs['Strength'].default_value = 1.2 * up
    no.inputs['W'].default_value = t * 1.5
    pl_light.data.energy = 450 * up
    for fl, tl_ in torches: tl_.data.energy = 60 + 18 * math.sin(t * 17 + fl.location.x) + 10 * math.sin(t * 41)
    pl.hide_render = up <= 0
    # камера
    if t < T_PORTAL:
        k = t / T_PORTAL
        ang = math.radians(-35 + 55 * ease(k)); r = 12 - 2 * k; hgt = 2.2 + 2.0 * math.sin(k * math.pi)
        cam.location = (1.5 + r * math.sin(ang), -r * math.cos(ang), hgt)
        tgt.location = (1.5, 0, 1.2 + 0.8 * k)
    else:
        k = ease((t - T_PORTAL) / (DUR - T_PORTAL - 0.3))
        ang = math.radians(20 * (1 - k)); r = 10 + (-10.2) * k
        cam.location = (1.5 + r * math.sin(ang), -r * math.cos(ang), 4.2 - 2.2 * k)
        tgt.location = (1.5, 3 * k, 2.0)
    cam.location.x += shake(t) * 3; cam.location.z += shake(t) * 2
    sc.render.filepath = os.path.join(out, 'f%04d.png' % (f + 1))
    bpy.ops.render.render(write_still=True)
    if f % 10 == 0: print('frame', f, '/', N, flush=True)
json.dump({'events': events, 'portal': T_PORTAL, 'dur': DUR, 'fps': FPS}, open(os.path.join(out, 'events.json'), 'w'))
print('DONE')
