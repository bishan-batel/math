#version 330

precision highp float;
precision highp vec2;

const int METHOD_NEWTON = 0;
const int METHOD_HALLEY = 1;
const int METHOD_YOUNG_OILER = 2;
const int METHOD_OILER = 3;

const int COLOR_DOMAIN = 0;
const int COLOR_LIMITING = 1;

const float GOLDEN_RATIO = (1 + sqrt(5.)) / 2.;
const float EPSILON = 1E-3f;

// #define vec2 dvec2
// #define float double

const uint MAX_ITERATIONS = 100u;

const vec3 INFINITY_COLOR = vec3(1.);
const vec3 CYCLE_COLOR = vec3(0.);

uniform vec3 u_color1;
uniform vec3 u_color2;
uniform vec3 u_color3;

uniform vec2 u_root1;
uniform vec2 u_root2;
uniform vec2 u_root3;

uniform vec2 u_z0;

uniform int u_mode;

uniform int u_color_mode;

uniform bool u_do_iteration_coloring;

in vec3 xyz_coords;

out vec4 frag_color;

// ======================
//   Complex Operations
// ======================

// Complex math helper functions
vec2 cmul(vec2 a, vec2 b) {
    return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

vec2 cdiv(vec2 a, vec2 b) {
    return vec2(a.x * b.x + a.y * b.y, a.y * b.x - a.x * b.y) / dot(b, b);
}

vec2 csub(vec2 a, vec2 b) {
    return a - b;
}

vec2 cadd(vec2 a, vec2 b) {
    return a + b;
}

vec2 cpowi(vec2 z, int m) {
    vec2 s = vec2(1., 0.);

    for (int i = 0; i < abs(m); i++) s = cmul(s, z);

    if (m < 0) {
        // z^(-m) = 1 / (z^m)
        s = cdiv(vec2(1., 0.), s);
    }

    return s;
}

vec2 cexp(vec2 z) {
    return exp(z.x) * vec2(cos(z.y), sin(z.y));
}

vec2 cubic_P(vec2 z, vec2 r1, vec2 r2, vec2 r3) {
    return cmul(cmul(z - r1, z - r2), z - r3);
}

vec2 cubic_dP(vec2 z, vec2 r1, vec2 r2, vec2 r3) {
    vec2 t1 = cmul(csub(z, r2), csub(z, r3));
    vec2 t2 = cmul(csub(z, r1), csub(z, r3));
    vec2 t3 = cmul(csub(z, r1), csub(z, r2));

    return t1 + t2 + t3;
}

vec2 cubic_d2P(vec2 z, vec2 r1, vec2 r2, vec2 r3) {
    return -2. * r1 - 2. * r2 - 2. * r3 + 6. * z;
}

vec2 f(vec2 z) {
    return cubic_P(z, u_root1, u_root2, u_root3);
}

// Derivative f'(z) = 3z^2
vec2 df(vec2 z) {
    return cubic_dP(z, u_root1, u_root2, u_root3);
}

vec2 d2f(vec2 z) {
    return cubic_d2P(z, u_root1, u_root2, u_root3);
}

// ======================
//         METHODS
// ======================

vec2 newton(vec2 z) {
    return z - cdiv(f(z), df(z));
}

vec2 deriv_newton(vec2 z) {
    return cdiv(
        cmul(d2f(z), f(z)),
        cmul(df(z), df(z))
    );
}

vec2 halley(vec2 z) {
    return z - cdiv(
            cmul(f(z), df(z)),
            cmul(df(z), df(z)) - 0.5f * cmul(f(z), d2f(z))
        );
}

vec2 young_oiler(vec2 z, inout vec2 zp, inout vec2 zpp) {
    vec2 d = cdiv(f(z) - f(zp), z - zp);
    vec2 d_p = cdiv(f(zp) - f(zpp), zp - zpp);
    vec2 d2 = cdiv(d - d_p, z - zpp);

    vec2 next_z =
        z - cdiv(
                cmul(f(z), d),
                cmul(d, d) - cmul(f(zp), d2)
            );

    zpp = zp;
    zp = z;

    return next_z;
}

vec2 oiler(vec2 z, inout vec2 zp, inout vec2 zpp) {
    vec2 d = cdiv(f(z) - f(zp), z - zp);
    vec2 d_p = cdiv(f(zp) - f(zpp), zp - zpp);
    vec2 d2 = cdiv(d - d_p, z - zpp);

    vec2 next_z = z - cdiv(
                cmul(f(z), d),
                cmul(d, d) - cmul(f(z), d2)
            );

    zpp = zp;
    zp = z;

    return next_z;
}

float min_root_distance(vec2 z, vec2 r1, vec2 r2, vec2 r3) {
    float d1 = length(r1 - z);
    float d2 = length(r2 - z);
    float d3 = length(r3 - z);
    return min(d1, min(d2, d3));
}

vec3 domain_color_complex(vec2 z) {
    return cos(atan(z.y, z.x) + vec3(0.0, 2.0, 4.0)) * (length(z));
}

vec3 limit_color_complex(
    vec2 z,
    uint iterations,
    vec2 r1,
    vec2 r2,
    vec2 r3
) {
    if (any(isnan(z)) || any(isinf(z))) return INFINITY_COLOR;
    if (min_root_distance(z, r1, r2, r3) > EPSILON) return CYCLE_COLOR;

    float d1 = length(r1 - z);
    float d2 = length(r2 - z);
    float d3 = length(r3 - z);

    vec3 color = vec3(0.);

    if (d1 <= min(d2, d3)) color = u_color1;
    else if (d2 <= min(d1, d3)) color = u_color2;
    else if (d3 <= min(d1, d2)) color = u_color3;

    if (u_do_iteration_coloring) {
        color *= -log(0.9f - float(iterations) / float(MAX_ITERATIONS));
    }

    return color;
}

vec2 iterate_method(vec2 initial_z, out uint iterations, int iter_mode) {
    vec2 zpp, zp, z;

    if (iter_mode == METHOD_OILER || iter_mode == METHOD_YOUNG_OILER) {
        zpp = initial_z;
        zp = zpp + vec2(GOLDEN_RATIO, 0.);
        z = zp - cdiv(f(zp), cdiv(f(zp) - f(zpp), zp - zpp));
    } else {
        z = initial_z;
    }

    uint i = 0u;

    for (; i < float(MAX_ITERATIONS); i++) {
        if (iter_mode == METHOD_NEWTON) {
            z = newton(z);
        }
        else if (iter_mode == METHOD_HALLEY) {
            z = halley(z);
        }
        else if (iter_mode == METHOD_YOUNG_OILER) {
            z = young_oiler(z, zp, zpp);
        }
        else if (iter_mode == METHOD_OILER) {
            z = oiler(z, zp, zpp);
        }

        if (min_root_distance(z, u_root1, u_root2, u_root3) < EPSILON) {
            break;
        }
    }

    iterations = i;

    return z;
}

vec3 Parametric_newton(vec2 r1, vec2 r2, vec2 r3) {
    vec2 z0 = (r1 + r2 + r3) / 3.0;
    vec2 z = z0;

    uint i = 0u;
    for (; i < MAX_ITERATIONS; i++) {
        z = z - cdiv(cubic_P(z, r1, r2, r3), cubic_dP(z, r1, r2, r3));
        if (min_root_distance(z, r1, r2, r3) < EPSILON) break;
    }

    return limit_color_complex(z, i, r1, r2, r3);
}

void main() {
    vec2 pixel_z = xyz_coords.xy;

    uint iterations;
    vec2 z = iterate_method(pixel_z, iterations, u_mode);

    vec3 color = vec3(1.);

    if (u_color_mode == COLOR_DOMAIN) {
        color = domain_color_complex(z);
    } else if (u_color_mode == COLOR_LIMITING) {
        color = limit_color_complex(z, iterations, u_root1, u_root2, u_root3);
    }

    // color = Parametric_newton(u_root1, u_root2, pixel_z);

    frag_color = vec4(color, 1.0);
}
