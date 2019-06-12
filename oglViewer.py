import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
from OpenGL.arrays import vbo

WIDTH = 500
HEIGHT = 500

BLACK = (0.0, 0.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0, 0.0)
RED = (1.0, 0.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0, 0.0)
YELLOW = (1.0, 1.0, 0.0, 0.0)

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

mouse_x = None
mouse_y = None

rotate = False
rotate_x = 0.0
rotate_y = 0.0

translating = False
new_x_pos = 0.0
new_y_pos = 0.0


def init_opengl():
    glClearColor(*BLACK)
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
    glLoadIdentity()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

    my_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glVertexPointer(3, GL_FLOAT, 24, my_vbo)
    glNormalPointer(GL_FLOAT, 24, my_vbo + 12)

    if new_x_pos is not None:
        glTranslate(new_x_pos, -new_y_pos, 0.0)

    glRotate(rotate_y, 1, 0, 0)
    glRotate(rotate_x, 0, 1, 0)

    glScale(scale_factor, scale_factor, scale_factor)
    glTranslate(-center[0], -center[1], -center[2])
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glDrawArrays(GL_TRIANGLES, 0, len(data))

    my_vbo.unbind()
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glutSwapBuffers()


def resize_viewport(width, height):
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
        if width == height:
            glOrtho(-1.5 - zoom, 1.5 + zoom, -1.5 - zoom, 1.5 + zoom, -10.0, 10.0)
        elif width <= height:
            glOrtho(-1.5 - zoom, 1.5 + zoom, (-1.5 - zoom) * aspectHeight,
                    (1.5 + zoom) * aspectHeight, -1.0, 1.0)
        else:
            glOrtho((-1.5 - zoom) * aspect, (1.5 + zoom) * aspect, -1.5 - zoom, 1.5 + zoom,
                    -10.0, 10.0)

    # Perspective Projection
    if persp_proj:
        if width <= height:
            gluPerspective(fov * aspectHeight, aspect, near, far)
        else:
            gluPerspective(fov, aspect, near, far)
        gluLookAt(0, 0, 3 + zoom, 0, 0, 0, 0, 1, 0)

    glMatrixMode(GL_MODELVIEW)


def key_pressed(key, x, y):
    global persp_proj, ortho_proj

    key = key.decode("utf-8")

    if key == '\x1b':
        sys.exit()

    if key == 's':
        glClearColor(*BLACK)

    if key == 'w':
        glClearColor(*WHITE)

    if key == 'r':
        glClearColor(*RED)

    if key == 'b':
        glClearColor(*BLUE)

    if key == 'g':
        glClearColor(*YELLOW)

    if key == 'S':
        glColor(*BLACK)

    if key == 'W':
        glColor(*WHITE)

    if key == 'R':
        glColor(*RED)

    if key == 'B':
        glColor(*BLUE)

    if key == 'G':
        glColor(*YELLOW)

    if key == 'o':
        if persp_proj:
            ortho_proj = True
            persp_proj = False
            resize_viewport(WIDTH, HEIGHT)

    # Activate Perspective-Projection
    if key == 'p':
        if ortho_proj:
            ortho_proj = False
            persp_proj = True
            resize_viewport(WIDTH, HEIGHT)

    if key == 'h':
        pass

    glutPostRedisplay()


def mouse_pressed(button, state, x, y):
    global zooming, mouse_x, mouse_y, rotate, translating

    if button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            zooming = True
            mouse_x = x
            mouse_y = y
        if state == GLUT_UP:
            zooming = False
            mouse_x = None
            mouse_y = None

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            rotate = True
            mouse_x = x
            mouse_y = y
        if state == GLUT_UP:
            rotate = False
            mouse_x = None
            mouse_y = None

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            translating = True
            mouse_x = x
            mouse_y = y
        if state == GLUT_UP:
            translating = False
            mouse_x = None
            mouse_y = None

    glutPostRedisplay()


def mouse_moved(x, y):
    global mouse_x, mouse_y, zooming, zoom, rotate_x, rotate_y, translating, new_x_pos, new_y_pos

    x_diff = abs(x) - abs(mouse_x)
    y_diff = abs(y) - abs(mouse_y)

    if zooming:
        scale = float(HEIGHT) / ANGLE
        zoom += (y_diff / scale)
        resize_viewport(HEIGHT, WIDTH)

    if rotate:
        rotate_x += x_diff
        rotate_y += y_diff

    if translating:
        scale = float(WIDTH) / 2.0
        new_x_pos += x_diff / scale
        new_y_pos += y_diff / scale

    mouse_x = x
    mouse_y = y


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("OpenGL obj Viewer")

    glutDisplayFunc(display)
    glutReshapeFunc(resize_viewport)
    glutKeyboardFunc(key_pressed)
    glutMouseFunc(mouse_pressed)
    glutMotionFunc(mouse_moved)

    create_obj_from_file()

    init_opengl()

    glutMainLoop()


# call main
if __name__ == '__main__':
    main()
