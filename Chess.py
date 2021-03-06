from scene import Scene; import taichi as ti; from taichi.math import *
scene = Scene(voxel_edges=0.0, exposure=3)
scene.set_background_color(color=(0.75, 0.75, 0.75))
scene.set_floor(height=-0.05, color=(0.3, 0.3, 0.3))
scene.set_directional_light(direction=(1, 1, 0), direction_noise=0.2, color=(0.5, 0.5, 0.5))
@ti.func
def set_blocks(st, ed, mat, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((st[0], ed[0]), (st[1], ed[1]), (st[2], ed[2]))): scene.set_voxel(v, mat, color)
@ti.func
def checkerboard(pos, k, color):
  blocks = ivec3(k, 1, k)
  for v in ti.grouped(ti.ndrange(
      (k*pos[0], k*pos[0]+ blocks[0]), (pos[1], pos[1] + blocks[1]), (k*pos[2], k*pos[2] + blocks[2]))):
    scene.set_voxel(v, 1, color)
@ti.func
def is_conicoid(origin, v, r, frac=vec3(1, 1, 1)):
  return (v.x-origin[0])**2/frac[0] + (v.y-origin[1])**2/frac[1] + (v.z-origin[2])**2/frac[2] <= r**2
@ti.func
def pawn(origin, radius, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
  (origin[1] - 2*radius[1], origin[1] + 2*radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
    if is_conicoid(origin, v, radius[0], vec3(1, 4, 1)): scene.set_voxel(v, 1, color + color_noise*ti.random())
    if is_conicoid(origin+vec3(0, radius[1]+4, 0), v, 4): scene.set_voxel(v, 1, color + color_noise*ti.random())
@ti.func
def knight(origin, radius, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
      (origin[1] - radius[1], origin[1] + radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
    scene.set_voxel(v, 1, color + color_noise*ti.random())
@ti.func
def bishop(origin, size, color, color_noise=vec3(0.1)):
  for i in ti.static(range(3)):
    radius = ivec3(1); radius[i] = size[i]
    for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
        (origin[1] - radius[1], origin[1] + radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
      scene.set_voxel(v, 1, color + color_noise*ti.random())
@ti.func
def circle(pos, x, z, r): return (x-pos[0])**2 + (z-pos[2])**2 - r**2
@ti.func
def cone(pos, v, r): return (v[0]-pos[0])**2 + (v[2]-pos[2])**2 - (v[1]-pos[1]-4)**2
@ti.func
def rook(origin, radius, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
      (origin[1] - radius[1], origin[1] + radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
    if v.y < origin[1]: scene.set_voxel(v, 1, color + color_noise*ti.random())
    else:
        for v in ti.grouped(ti.ndrange(2, 2)):
          set_blocks(ivec3(origin[0]-4+6*v.x, origin[1], origin[2]-4+6*v.y),
                   ivec3(origin[0]-2+6*v.x, origin[1]+4, origin[2]-2+6*v.y), 1, color)
@ti.func
def queen(origin, radius, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
      (origin[1] - radius[1], origin[1] + radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
    if circle(origin, v.x, v.z, radius[0]) <= 0: scene.set_voxel(v, 1, color + color_noise*ti.random())
@ti.func
def king(origin, radius, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
      (origin[1] - radius[1], origin[1] + radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
    if v.y < origin[1]: scene.set_voxel(v, 1, color + color_noise*ti.random())
    elif cone(origin, v, radius[0]) <= 0: scene.set_voxel(v, 1, color + color_noise*ti.random())
@ti.func
def piece(origin, radius, color, color_noise=vec3(0.1)):
  for v in ti.grouped(ti.ndrange((origin[0] - radius[0], origin[0] + radius[0]),
      (origin[1] - 2*radius[1], origin[1] + 2*radius[1]), (origin[2] - radius[2], origin[2] + radius[2]))):
    if is_conicoid(origin, v, radius[0], vec3(1, 4, 1)): scene.set_voxel(v, 1, color + color_noise*ti.random())

@ti.kernel
def initialize_voxels():
  N = 8; H = 1; scale = 16
  black, white = vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0)
  for i, j in ti.ndrange(N, N):
    if (i + j) % 2: checkerboard(ivec3(i, -2, j), scale, black)
    else: checkerboard(ivec3(i, -2, j), scale, white)
  radius_pawn = ivec3(6, 12, 6); color_noise = vec3(0.1)
  color_me = vec3(ti.hex_to_rgb(0xAF5E24)); color_enemy = vec3(0.1)

  for i in range(16):
    sign, color = -1, color_enemy
    if i < 8: sign, color = 1, color_me
    pawn(ivec3(((i%8) + 0.5)*scale, 1, sign*(64-3*scale/2)), radius_pawn, color, color_noise)
    piece(ivec3(((i%8) + 0.5)*scale, 1, sign*(64-scale/2)), radius_pawn, color, color_noise)

  for i in range(2):
    color = color_enemy if i == 0 else color_me
    knight(ivec3(-64+(1+0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)
    knight(ivec3(64-(1+0.5)*scale, 17, (2*i-1)*(64-scale/2)),ivec3(4), color, color_noise)
    bishop(ivec3(-64+(2+0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)
    bishop(ivec3(64-(2+0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)
    rook(ivec3(-64+(0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)
    rook(ivec3(64-(0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)
    queen(ivec3(-64+(3+0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)
    king(ivec3(-64+(4+0.5)*scale, 17, (2*i-1)*(64-scale/2)), ivec3(4), color, color_noise)

initialize_voxels()
scene.finish()
