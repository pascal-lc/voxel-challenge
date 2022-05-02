from scene import Scene
import taichi as ti
from taichi.math import *
# 玻璃美酒夜光杯

scene = Scene(voxel_edges=0.0, exposure=3)
scene.set_directional_light((1, 1, 1), 0.2, (0.8, 0.8, 0.8))
scene.set_background_color((0.3, 0.5, 0.5))
scene.set_floor(-1.0, (0.6, 0.6, 0.6))

@ti.func
def ellipse(pos, x, y, z, r):
	return (x-pos[0])**2 + (y-pos[1])**2 + (z-pos[2])**2/2 - 3

@ti.func
def wineglass(x, y, z):
	return x**2 + y**2 - (ti.log(z+3.2))**2 - 0.02

@ti.kernel
def initialize_voxels():
	N = 64; color = vec3(0, 0.3, 0.3); color_noise = vec3(0.1)
	for i, j, k in ti.ndrange((-N, N), (-N, N), (-N, N)):
		x, y, z = float(i) / (N/3), float(j) / (N/3), float(k) / (N/3)
		if wineglass(x, y, z) <= 0 and ellipse(vec3(0, 0, 3.0), x, y, z, 1) >= 0:
			scene.set_voxel(vec3(i, k, j), 1, color + ti.random()*color_noise)


initialize_voxels()

scene.finish()
