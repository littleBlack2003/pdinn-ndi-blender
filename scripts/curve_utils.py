"""Natural cubic spline for the editable three-dimensional chain guides."""
from mathutils import Vector

def natural_spline(nodes, steps=450):
    v = [Vector(n) for n in nodes]
    n = len(v)
    t = [0]
    for j in range(n - 1):
        t.append(t[-1] + (v[j + 1] - v[j]).length)
    h = [t[j + 1] - t[j] for j in range(n - 1)]
    lo = [0.0] * n
    di = [1.0] * n
    up = [0.0] * n
    rhs = [Vector((0, 0, 0)) for j in range(n)]
    for j in range(1, n - 1):
        lo[j] = h[j - 1]
        di[j] = 2 * (h[j - 1] + h[j])
        up[j] = h[j]
        rhs[j] = 6 * ((v[j + 1] - v[j]) / h[j] - (v[j] - v[j - 1]) / h[j - 1])
    for j in range(1, n):
        f = lo[j] / di[j - 1]
        di[j] -= f * up[j - 1]
        rhs[j] -= f * rhs[j - 1]
    m = [Vector((0, 0, 0)) for j in range(n)]
    m[-1] = rhs[-1] / di[-1]
    for j in range(n - 2, -1, -1):
        m[j] = (rhs[j] - up[j] * m[j + 1]) / di[j]
    points = []
    j = 0
    for k in range(steps):
        x = t[-1] * k / (steps - 1)
        while j < n - 2 and x > t[j + 1]:
            j += 1
        A = (t[j + 1] - x) / h[j]
        B = (x - t[j]) / h[j]
        points.append(A * v[j] + B * v[j + 1] + ((A ** 3 - A) * m[j] + (B ** 3 - B) * m[j + 1]) * h[j] ** 2 / 6)
    return points
