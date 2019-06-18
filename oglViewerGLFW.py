import math

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
from OpenGL.arrays import vbo

WIDTH = 500
HEIGHT = 500

BG_BLACK = (0.0, 0.0, 0.0, 0.0)
BG_WHITE = (1.0, 1.0, 1.0, 0.0)
BG_RED = (1.0, 0.0, 0.0, 0.0)
BG_BLUE = (0.0, 0.0, 1.0, 0.0)
BG_YELLOW = (1.0, 1.0, 0.0, 0.0)

M_BLACK = (0.0, 0.0, 0.0)
M_WHITE = (1.0, 1.0, 1.0)
M_RED = (1.0, 0.0, 0.0)
M_BLUE = (0.0, 0.0, 1.0)
M_YELLOW = (1.0, 1.0, 0.0)
color = M_RED

ANGLE = 10

my_vbo = vbo.VBO(np.array([0, 0, 0]))
center = []
scale_factor = 1.0
data = []

ortho_proj = True
persp_proj = False

fov = 90.0
near = 0.1
far = 100.0

zoom = 0
zooming = False

mouse_x = 0
mouse_y = 0

rotate_b = False
rotate_x = 0.0
rotate_y = 0.0

translating = False
new_x_pos = 0.0
new_y_pos = 0.0

smallChars = True

actOri = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
start_p = [0, 0, 0]
angle = 0
axis = np.array([0, 0, 1])

shadows = False


def init_opengl():
    glClearColor(*BG_WHITE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.5, 1.5, -1.5, 1.5, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)


def create_obj_from_file():
    global my_vbo, center, scale_factor, data

    vertices = []
    normals = []
    faces = []

    file = open(sys.argv[1])

    for lines in file:
        # check if not empty
        if lines.split():
            ltype = lines.split()[0]
            if ltype == 'v':
                vertices.append(list(map(float, lines.split()[1:])))
            if ltype == 'vn':
                normals.append(list(map(float, lines.split()[1:])))
            if ltype == 'f':
                first = lines.split()[1:]
                for face in first:
                    faces.append(list(map(float, face.split('//'))))

    for face in faces:
        # if no vt is available fill up with 0 at list position 1
        if len(face) == 2:
            face.insert(1, 0.0)
        # if no vt and no vn is available fill up with 0 at list position 1 and 2
        if len(face) == 1:
            face.insert(1, 0.0)
            face.insert(2, 0.0)

    min_x = vertices[0][0]
    max_x = vertices[0][0]
    min_y = vertices[0][1]
    max_y = vertices[0][1]
    min_z = vertices[0][2]
    max_z = vertices[0][2]

    for line in vertices:
        x, y, z = line[0], line[1], line[2]
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
        if z < min_z:
            min_z = z
        if z > max_z:
            max_z = z

    x = min_x + ((max_x - min_x) / 2)
    y = min_y + ((max_y - min_y) / 2)
    z = min_z + ((max_z - min_z) / 2)

    center.append(x)
    center.append(y)
    center.append(z)

    max_x = max([abs(x[0]) for x in vertices])
    max_y = max([abs(x[1]) for x in vertices])

    if max_x > max_y:
        scale_factor = max_x
    else:
        scale_factor = max_y

    for vertex in faces:
        vn = int(vertex[0]) - 1
        nn = int(vertex[2]) - 1
        if 0 <= nn < len(normals):
            data.append(vertices[vn] + normals[nn])
        else:
            normals = [x - y for x, y in zip(vertices[vn], [x, y, z])]
            l = math.sqrt(normals[0] ** 2 + normals[1] ** 2 + normals[2] ** 2)
            normals = [x / l for x in normals]
            data.append(vertices[vn] + normals)

    my_vbo = vbo.VBO(np.array(data, 'f'))


def display():
    glMatrixMode(GL_MODELVIEW)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # glLoadIdentity()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

    light = np.array([0.0, 100000.0, -0.1, 0.0])
    glLightfv(GL_LIGHT0, GL_POSITION, light)
    p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / light[1], 0, 0, 1.0, 0, 0, 0, 0, 0]

    my_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glVertexPointer(3, GL_FLOAT, 24, my_vbo)
    glNormalPointer(GL_FLOAT, 24, my_vbo + 12)

    if shadows:
        # Schatten ab hier
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(light[0], light[1], light[2])

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glMultMatrixf(p)
        glColor3fv(M_BLACK)

        glTranslatef(-light[0], -light[1], -light[2])
        glDrawArrays(GL_TRIANGLES, 0, len(data))

        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        # Schatten bis hier

    glLoadIdentity()
    if new_x_pos is not None:
        glTranslate(new_x_pos, -new_y_pos, 0.0)

    glMultMatrixf(actOri * rotate(angle, axis))

    glColor3fv(color)
    glScale(scale_factor, scale_factor, scale_factor)
    glTranslate(-center[0], -center[1], -center[2])
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glDrawArrays(GL_TRIANGLES, 0, len(data))

    my_vbo.unbind()

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glfw.swap_buffers(window)


def resize_viewport(win, width, height):
    global HEIGHT, WIDTH, zoom
    WIDTH = width
    HEIGHT = height

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # set Viewport
    glViewport(0, 0, int(width), int(height))

    aspect = float(width) / height
    aspectHeight = float(height) / width

    # Ortho Projection
    if ortho_proj:
        if width <= height:
            glOrtho(-1.5, 1.5, (-1.5) * aspectHeight,
                    1.5 * aspectHeight, -100.0, 100.0)
        else:
            glOrtho((-1.5) * aspect, (1.5) * aspect, -1.5, 1.5,
                    -100.0, 100.0)

    # Perspective Projection
    if persp_proj:
        if width <= height:
            gluPerspective(fov * aspectHeight, aspect, near, far)
        else:
            gluPerspective(fov * aspect, aspect, near, far)
        gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)

    glMatrixMode(GL_MODELVIEW)


def key_pressed(win, key, scancode, action, mods):
    global persp_proj, ortho_proj, smallChars, shadows, WIDTH, HEIGHT

    if action == glfw.PRESS:
        if smallChars:
            if key == glfw.KEY_S:
                glClearColor(*BG_BLACK)

            if key == glfw.KEY_W:
                glClearColor(*BG_WHITE)

            if key == glfw.KEY_R:
                glClearColor(*BG_RED)

            if key == glfw.KEY_B:
                glClearColor(*BG_BLUE)

            if key == glfw.KEY_G:
                glClearColor(*BG_YELLOW)

        else:

            if key == glfw.KEY_W:
                glColor(*M_WHITE)

            if key == glfw.KEY_R:
                glColor(*M_RED)

            if key == glfw.KEY_B:
                glColor(*M_BLUE)

            if key == glfw.KEY_G:
                glColor(*M_YELLOW)

            if key == glfw.KEY_S:
                glColor(*M_BLACK)

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        if key == glfw.KEY_O:
            if persp_proj:
                ortho_proj = True
                persp_proj = False
                resize_viewport(win, WIDTH, HEIGHT)

        if key == glfw.KEY_P:
            if ortho_proj:
                ortho_proj = False
                persp_proj = True
                resize_viewport(win, WIDTH, HEIGHT)

        if key == glfw.KEY_H:
            shadows = not shadows

    if key == glfw.KEY_LEFT_SHIFT:
        smallChars = not smallChars


def mouse_pressed(win, button, action, mods):
    global zooming, rotate_b, translating, actOri, angle, axis, start_p, zoom, mouse_x, mouse_y

    print("Pressing mouse: ", button)

    if button == glfw.MOUSE_BUTTON_MIDDLE:
        if glfw.get_mouse_button(win, button) == glfw.PRESS:
            zooming = True
            start_p = [mouse_x, mouse_y, 0]
            zoom = start_p[1]
        if glfw.get_mouse_button(win, button) == glfw.RELEASE:
            zooming = False

    if button == glfw.MOUSE_BUTTON_LEFT:
        r = min(WIDTH, HEIGHT) / 2.0
        if glfw.get_mouse_button(win, button) == glfw.PRESS:
            rotate_b = True
            start_p = projectOnSphere(mouse_x, mouse_y, r)
        if glfw.get_mouse_button(win, button) == glfw.RELEASE:
            rotate_b = False
            actOri = actOri * rotate(angle, axis)
            angle = 0

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if glfw.get_mouse_button(win, button) == glfw.PRESS:
            translating = True
            start_p = [mouse_x, mouse_y, 0]
        if glfw.get_mouse_button(win, button) == glfw.RELEASE:
            translating = False


# Vorlesung
def projectOnSphere(x, y, r):
    x, y = x - WIDTH / 2.0, HEIGHT / 2.0 - y
    a = min(r * r, x ** 2 + y ** 2)
    z = math.sqrt(r * r - a)
    l = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    return x / l, y / l, z / l


# Vorlesung
def rotate(angle, axis):
    c, mc = math.cos(angle), 1 - math.cos(angle)
    s = math.sin(angle)
    l = math.sqrt(np.dot(np.array(axis), np.array(axis)))
    x, y, z = np.array(axis) / l
    r = np.matrix(
        [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
         [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
         [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
         [0, 0, 0, 1]])
    return r.transpose()


def mouse_moved(win, x, y):
    global start_p, zooming, zoom, translating, new_x_pos, new_y_pos, zoom, scale_factor, angle, axis, mouse_x, mouse_y

    mouse_x = x
    mouse_y = y

    # Vorlesung
    if rotate_b:
        r = min(WIDTH, HEIGHT) / 2.0
        moveP = projectOnSphere(x, y, r)
        dot = np.dot(start_p, moveP)
        angle = math.acos(dot)
        axis = np.cross(start_p, moveP)

    if zooming:
        if zoom > y and scale_factor > 0:
            scale_factor += abs(float(float((y - start_p[1])) / HEIGHT))

        if zoom <= y and scale_factor > 0:
            scale_factor -= abs(float(float((y - start_p[1])) / HEIGHT))

        if scale_factor <= 0.0015:
            scale_factor = 0.002

        glScale(scale_factor, scale_factor, scale_factor)
        zoom = y

    if translating:
        new_x_pos = new_x_pos + float(float((x - start_p[0])) / WIDTH)
        new_y_pos = new_y_pos + float(float((y - start_p[1])) / HEIGHT)
        start_p = [x, y, 0]


def run():
    # initializer timer
    glfw.set_time(0.0)
    t = 0.0
    while not glfw.window_should_close(window):
        # update every x seconds
        currT = glfw.get_time()
        if currT - t > 1.0 / frame_rate:
            # update time
            t = currT
            # clear
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            display()

            # Poll for and process events
            glfw.poll_events()
    # end
    glfw.terminate()


def main():
    global window, frame_rate
    cwd = os.getcwd()

    if not glfw.init():
        return

    os.chdir(cwd)

    glfw.window_hint(glfw.DEPTH_BITS, 32)
    frame_rate = 144
    window = glfw.create_window(WIDTH, HEIGHT, "2D Graphics", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_mouse_button_callback(window, mouse_pressed)
    glfw.set_key_callback(window, key_pressed)
    glfw.set_window_size_callback(window, resize_viewport)
    glfw.set_cursor_pos_callback(window, mouse_moved)

    create_obj_from_file()

    init_opengl()

    run()


# call main
if __name__ == '__main__':
    main()
