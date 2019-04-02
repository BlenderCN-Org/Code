import bpy
import bmesh

import numpy
import sys
sys.path.append('/d/bandrieu/GitHub/Code/Python')
import lib_blender_edit as lbe
import lib_blender_util as lbu
from mathutils import Vector
import random



scene = bpy.context.scene
lbu.clear_scene(meshes=True, lamps=True, cameras=False)

## add mesh
"""
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3)
obj = bpy.data.objects["Icosphere"]
"""

"""
bpy.ops.mesh.primitive_monkey_add()
obj = bpy.data.objects["Suzanne"]
bpy.ops.object.modifier_add(type='SUBSURF')
obj.modifiers['Subsurf'].levels = 4
bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Subsurf')
"""

"""
bpy.ops.mesh.primitive_cylinder_add(vertices=8,
                                    radius=1.0,
                                    depth=2.0,
                                    end_fill_type='TRIFAN')
obj = bpy.data.objects["Cylinder"]
bpy.ops.object.modifier_add(type='SUBSURF')
obj.modifiers['Subsurf'].levels = 4
bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Subsurf')
"""

"""
bpy.ops.import_scene.obj(filepath='/d/bandrieu/GitHub/FFTsurf/test/demo_EoS_brep/mesh_eos/mesh_eos_optim.obj',
                         axis_forward='Y', axis_up='Z')
obj = bpy.data.objects['mesh_eos_optim']
"""

pth = '/d/bandrieu/GitHub/FFTsurf/cases/jouke/output/'
xyz = numpy.loadtxt(pth + 'pos_060.dat')
tri = numpy.loadtxt(pth + 'connect_01.dat')-1
verts = [[x for x in p] for p in xyz]
faces = [[int(v) for v in t] for t in tri]

obj = lbu.pydata_to_mesh(verts,
                         faces,
                         name='mesh')


bpy.ops.object.select_all(action='DESELECT')
scene.objects.active = obj
obj.select = True

msh = obj.data



############################################

args = sys.argv
if len(args) < 4:
    length_max = 30.0
else:
    length_max = float(args[3])

if len(args) < 5:
    deviation = 0.0
else:
    deviation = float(args[4])

"""
geodesic = []

# switch to edit mode
bpy.ops.object.mode_set(mode='EDIT')

# Get a BMesh representation
bmsh = bmesh.from_edit_mesh(msh)

# random first point

face = bmsh.faces[0]#random.randint(0,len(bmsh.faces))]
x = [v.co for v in face.verts]
u = numpy.ones(len(x))#numpy.random.rand(len(x))
uv = u/numpy.sum(u)

xyz = Vector([0,0,0])
for i in range(len(x)):
    xyz = xyz + x[i]*uv[i]

# initial direction
#direction = Vector(2*numpy.random.rand(3) - 1).normalized()
direction = Vector([1,1,1]).normalized()

geodesic.append(lbe.IntersectionPoint(faces=[face], uvs=uv, xyz=xyz))
length = 0.0
delta_length = 0.0
while length < length_max:
    #print("face #",face.index, ", length=",length,"/",length_max)
    print("length=",length,"/",length_max,", delta =", delta_length)
    normal = face.normal
    # project displacement onto local tangent plane
    direction_t = (direction - direction.project(normal)).normalized()
    displacement = (length_max - length)*direction_t
    #
    nv = len(face.verts)
    leaves_face = False
    for i in range(nv):
        print("    ",i+1,"/",nv)
        vi = face.verts[i]
        vj = face.verts[(i+1)%nv]
        # plane generated by edge ij and face normal
        planeorig = 0.5*(vi.co + vj.co)
        vecij = vj.co - vi.co
        vecijsqr = vecij.dot(vecij)
        # normal of that plane, pointing towards the face's exterior
        planenormal = normal.cross(vecij)
        planenormal.normalize()
        # check if displacement crosses the plane
        if planenormal.dot(xyz - planeorig + displacement) > 0 and planenormal.dot(displacement) > 1.e-7:
            print("        crosses edge wall :", planenormal.dot(xyz - planeorig + displacement), planenormal.dot(displacement))
            # get intersection point between displacement and plane
            fracdisp = planenormal.dot(planeorig - xyz)/planenormal.dot(displacement)
            print("        fracdisp =",fracdisp)
            targetpoint = xyz + fracdisp*displacement
            # project that point onto edge ij
            fracvij = vecij.dot(targetpoint - vi.co)/vecijsqr
            print("        fracvij =",fracvij)
            if fracvij < 0 or fracvij > 1:
                print("            projection outside edge range")
            else:
                leaves_face = True
                edge = face.edges[i]
                found_other_face = False
                for otherface in edge.link_faces:
                    if otherface != face:
                        xyzprev = xyz.copy()
                        xyz = vi.co + fracvij*vecij
                        delta_length = (xyz - xyzprev).length
                        length += delta_length
                        direction = xyzprev - xyz + displacement
                        geodesic.append(lbe.IntersectionPoint(faces=[face, otherface], uvs=[], xyz=xyz))
                        face = otherface
                        found_other_face = True
                        break
                if not found_other_face:
                    print("found no other face, edge is boundary?", edge.is_boundary)
                    leaves_face = False
                    break
    if not leaves_face:
        print("does not leave face")
        break

# select all faces crossed by the geodesic
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_mode(type="FACE")
for g in geodesic:
    for f in g.faces:
        f.select = True
    
# leave edit mode
bpy.ops.object.mode_set(mode='OBJECT')
bmsh.free()

"""

# random first point
iface = random.randint(1,len(obj.data.polygons))
baryco = numpy.random.rand(len(obj.data.polygons[iface].vertices))
startdirection = Vector(2*numpy.random.rand(3) - 1)

geodesic = lbe.trace_geodesic(iface,
                              baryco,
                              startdirection,
                              length_max,
                              deviation)


XYZ = [p.xyz for p in geodesic]
ifaces = [[f for f in p.faces] for p in geodesic]

obj = lbu.pydata_to_polyline(XYZ,
                       name='geodesic',
                       thickness=obj.dimensions.length*1e-3,
                       resolution_u=24,
                       bevel_resolution=4,
                       fill_mode='FULL')
mat = bpy.data.materials.new("mat_geodesic")
mat.diffuse_color = [1,1,0]
mat.diffuse_intensity = 1
mat.emit = 1
mat.use_shadeless = True
obj.data.materials.append(mat)

