from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(voxel_edges=0.0, exposure=3)
scene.set_background_color(color=(0.3, 0.3, 0.3))
scene.set_floor(height=-1.0, color=(0.3, 0.3, 0.3))
scene.set_directional_light(direction=(1, 1, 0), direction_noise=0.2, color=(0.8, 0.7, 0.6))

pi = 3.1415926

@ti.func
def set_lines_xz(st, ed, mat, color, color_noise=vec3(0.1)):
	for v in ti.grouped(ti.ndrange((st[0], ed[0]), (st[1], ed[1]), (st[2], ed[2]))):
		if ed[0] - st[0]:
			k = (ed[2]-st[2])/(ed[0]-st[0])
			z = k*(v.x - st[0])+st[2]
			z = z+1 if z > 0 and z > int(z) else z-1 if z < 0 and z < int(z) else z
			scene.set_voxel(ivec3(v.x, v.y, z), mat, color + color_noise*ti.random())

@ti.func
def hydrogen_bond(st, ed, mat, color, color_noise=vec3(0.1)):
	for v in ti.grouped(ti.ndrange((st[0], ed[0]), (st[1], ed[1]), (st[2], ed[2]))):
		if abs((st[2]-ed[2])*v[0] + (ed[0]-st[0])*v[2] + st[0]*ed[2] - ed[0]*st[2]) - 8*ti.random() < 4:
			scene.set_voxel(v, mat, color + color_noise*ti.random())

@ti.func
def helix(R, r, color, color_noise=vec3(0.1), phi=0):
	N = 512; scale = 2
	du, dv = 4*pi/N, 2*pi/N
	for i in range(100):
		for i, j in ti.ndrange(N, N):
			u, v = du*i, dv*j
			w = R + r*ti.cos(v)
			x = (w * ti.cos(u+phi)) * scale
			y = (w * ti.sin(u+phi)) * scale
			z = (r*ti.sin(v)+u*4) * scale
			scene.set_voxel(ivec3(x, z-48, y), 1, color+color_noise*ti.random())

@ti.func
def helixline(R, color, color_noise=vec3(0.1), phi=pi):
	N = 512; dt = 4*pi/N; scale = 2
	for i in range(N):
		t = dt*i
		x2 = (R*ti.cos(t)) * scale
		y2 = (R*ti.sin(t)) * scale
		z2 = (t*4) * scale
		scene.set_voxel(ivec3(x2, z2-48, y2), 1, color+color_noise*ti.random())
		x3 = (R*ti.cos(t + phi)) * scale
		y3 = (R*ti.sin(t + phi)) * scale
		z3 = (t*4) * scale
		scene.set_voxel(ivec3(x3, z3-48, y3), 1, color+color_noise*ti.random())

		hydrogen_bond(ivec3(x2, z2-48, y2), ivec3(-x2, z2-48+2, -y2), 1, color)
		hydrogen_bond(ivec3(x3, z3-48, y3), ivec3(-x3, z3-48+2, -y3), 1, color)


@ti.kernel
def initialize_voxels():
	R, r = 8, 0.8
	cw = vec3(0.6, 0.4, 0.1); cc = vec3(0.1, 0.4, 0.6); color_noise = vec3(0.3)
	color_key = vec3(0.2, 0.6, 0.2)
	helix(R, r, cc, color_noise, 0)
	helix(R, r, cw, color_noise, pi)
	helixline(R, color_key)
	set_lines_xz(ivec3(-16, -48, -1), ivec3(16, -48+2, 1), 1, color_key)

initialize_voxels()
scene.finish()
