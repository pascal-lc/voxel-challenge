from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(voxel_edges=0.0, exposure=3)
scene.set_background_color(color=(0.75, 0.75, 0.75))
scene.set_floor(height=-0.125, color=(0.3, 0.6, 0.5))
scene.set_directional_light(direction=(1, 1, 1), direction_noise=0.2, color=(0.8, 0.7, 0.6))

@ti.func
def set_blocks(st, ed, mat, color, color_noise=vec3(0.1), sign=1, axis=0):
	for v in ti.grouped(ti.ndrange((st[0], ed[0]), (st[1], ed[1]), (st[2], ed[2]))):
		scene.set_voxel(ivec3(v.x, axis + sign*v.y, v.z),
		                mat, color + color_noise*ti.random())

@ti.kernel
def initialize_voxels():
	origin = ivec3(0, -8, 0)
	pos0 = ivec3(-32, -8, -32)  # 地基
	ChinaRed = vec3(0.80, 0, 0)
	MarbleWhite = vec3(0.9)
	GrassGreen = vec3(0.0, 0.7, 0.0)
	color_noise = ivec3(0)
	# 立柱
	for i, j in ti.ndrange(2, 2):
		st = pos0 + ivec3(i*48, 0, j*48)
		ed = st + ivec3(16, 68, 16)
		set_blocks(st, ed, 1, ChinaRed, color_noise)
	for i, j, k in ti.ndrange(2, 2, 2):
		set_blocks(ivec3(-30+48*j+8*i, -8, -32+48*k), ivec3(-26+48*j+8*i, 60, -16+48*k), 1, MarbleWhite, color_noise)
		set_blocks(ivec3(-32+48*j, -8, -30+48*k+8*i), ivec3(-16+48*j, 60, -26+48*k+8*i), 1, MarbleWhite, color_noise)
	# 底座
	for i in range(8):
		color1 = vec3(0.9 - i*0.1) * vec3(0.7, 0.7, 0.7)
		set_blocks(ivec3(-64, -8+i, -64), ivec3(64, -8+i+1, 64), 1, color1, color_noise)
	# 绿化
	set_blocks(ivec3(-60, -1, -60), ivec3(60, 0, 60), 1, GrassGreen)
	# 台阶
	pos2 = origin + ivec3(32-4, 0, -16)
	for i in range(9):
		st = pos2 + ivec3(4*i, 0, 0)
		ed = st + ivec3(4, i, 32)
		set_blocks(st, ed, 0, ChinaRed, color_noise, -1, -8)
	# 穹顶
	pos1 = pos0 + ivec3(0, 32+4, 0)
	for i in range(32-4):
		st = pos1 + ivec3(-int(i), int(i), -int(i))
		ed = ivec3(-st[0], st[1]+1, -st[2])
		set_blocks(st, ed, 1, MarbleWhite)

	# 斗拱
	for i in range(2):
		st0 = ivec3(-32+48*i, 54, -64); ed0 = st0 + ivec3(2, 2, 128)
		st1 = ivec3(-18+48*i, 54, -64); ed1 = st1 + ivec3(2, 2, 128)
		st2 = ivec3(-64, 54, -32+48*i); ed2 = st2 + ivec3(128, 2, 2)
		st3 = ivec3(-64, 54, -18+48*i); ed3 = st3 + ivec3(128, 2, 2)
		set_blocks(st0, ed0, 1, ChinaRed, color_noise); set_blocks(st1, ed1, 1, ChinaRed, color_noise)
		set_blocks(st2, ed2, 1, ChinaRed, color_noise); set_blocks(st3, ed3, 1, ChinaRed, color_noise)

	n = 5
	for i in range(16):
		# x 轴方向
		st = ivec3(-32, 24, -32) + ivec3(-2*i, 2*i, -2*i)
		ed = ivec3(-st[0], st[1]+2, st[2]+2)
		if i % 2:
			set_blocks(st, ed, 1, ChinaRed, color_noise)
			# 对称，关于 x-O-y 平面，x、y坐标不变，z坐标取反，并微调z坐标
			set_blocks(st*ivec3(1, 1, -1) + ivec3(0, 0, -2), ed *
			           ivec3(1, 1, -1) + ivec3(0, 0, 2), 1, ChinaRed, color_noise)
			dx = ed[0]/n
			for k in range(n):
				st[2] += k*dx
				ed = ivec3(-st[0], st[1]+2, st[2]+2)
				set_blocks(st, ed, 1, ChinaRed, color_noise)
		# z 轴方向
		st2 = ivec3(-32, 24, -32) + ivec3(-2*i, 2*i, -2*i)
		ed2 = ivec3(st2[0]+2, st2[1]+2, -st2[2])
		if not i % 2:
			set_blocks(st2, ed2, 1, ChinaRed, color_noise)
			# 对称，关于 z-O-y 平面，z、y坐标不变，x坐标取反，并微调x坐标
			set_blocks(st2*ivec3(-1, 1, 1) + ivec3(-2, 0, 0), ed2 *
			           ivec3(-1, 1, 1) + ivec3(2, 0, 0), 1, ChinaRed, color_noise)
			dx = ed2[2]/n
			for k in range(n):
				st2[0] += k*dx
				ed2 = ivec3(st2[0]+2, st2[1]+2, -st2[2])
				set_blocks(st2, ed2, 1, ChinaRed, color_noise)
	# 大天窗
	set_blocks(ivec3(-16, 24, -16), ivec3(16, 56, 16), 0, ChinaRed)

initialize_voxels()
scene.finish()
