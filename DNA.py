from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(voxel_edges=0.0, exposure=3)
scene.set_background_color(color=(0.75, 0.75, 0.75))
scene.set_floor(height=-1.0, color=(0.3, 0.3, 0.3))
scene.set_directional_light(direction=(1, 1, 0), direction_noise=0.2, color=(0.8, 0.7, 0.6))

pi = 3.1415926

@ti.func
def set_blocks(st, ed, mat, color, color_noise=vec3(0.1)):
	for v in ti.grouped(ti.ndrange((st[0], ed[0]), (st[1], ed[1]), (st[2], ed[2]))):
		scene.set_voxel(v, mat, color + color_noise*ti.random())

@ti.func
def helix_surf(R, r, color, color_noise=vec3(0.1), rotation=1, phi=0):
	N = 512
	scale = 2
	du, dv = 4*pi/N, 2*pi/N
	for i in range(100):
		for i, j in ti.ndrange(N, N):
			u, v = du*i, dv*j
			w = R + r*ti.cos(v)
			x = w * ti.cos(rotation*u+phi)
			y = w * ti.sin(rotation*u+phi)
			z = r*ti.sin(v)+u*4
			scene.set_voxel(vec3(x, z, y)*scale + vec3(0, -48, 0), 1, color+color_noise*ti.random())

@ti.func
def helix_curve(R, color, rotation=1, phi=0, color_noise=vec3(0.1)):
	N = 512
	scale = 2
	dt = 4*pi/N
	for i in range(N):
		t = dt*i
		x = R*ti.cos(rotation*t+phi)
		y = R*ti.sin(rotation*t+phi)
		z = t*4
		scene.set_voxel(vec3(x, z, y)*scale + vec3(0, -48, 0), 1, color+color_noise*ti.random())

@ti.kernel
def initialize_voxels():
	R, r = 8, 1.0
	cg = vec3(1.0, 0.85, 0.0)
	cb = vec3(0.1, 0.4, 0.6)
	color_noise = vec3(0.1)
	color_curve = vec3(0.2, 0.6, 0.2)
	cw, ccw = 1, -1
	phi = pi/2
	helix_surf(R, r, cb, color_noise, ccw, 0)
	helix_surf(R, r, cg, color_noise, ccw, phi)
	helix_curve(R, color_curve, ccw, 0)
	helix_curve(R, color_curve, ccw, phi)
	set_blocks(ivec3(-32, -64, -32), ivec3(32, -48, 32), 1, vec3(0.2, 0.1, 0.1))

initialize_voxels()
scene.finish()
