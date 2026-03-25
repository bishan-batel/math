#version 330
precision highp float;
precision highp vec2;

const int MAX_COEFS = 4;
const int METHOD_NEWTON = 0;
const int METHOD_HALLEY = 1;
const int METHOD_YOUNG_OILER  = 2;
const int METHOD_OILER  = 3;

const int COLOR_DOMAIN = 0;
const int COLOR_LIMITING = 1;

const float GOLDEN_RATIO = (1 + sqrt(5.)) / 2.;
const float EPSILON = 1E-5f;

const int MAX_ITERATIONS = 100;

const vec3 INFINITY_COLOR = vec3(1.); 
const vec3 CYCLE_COLOR = vec3(0.); 

uniform int coeff_count;
uniform vec3 color1;
uniform vec3 color2;
uniform vec3 color3;

uniform vec2 coef0;
uniform vec2 coef1;
uniform vec2 coef2;
uniform vec2 coef3;
uniform vec2 root1;
uniform vec2 root2;
uniform vec2 root3;

uniform vec2 z0;

uniform int mode;

uniform int color_mode;

in vec3 xyz_coords;

out vec4 frag_color;

vec2 root_midpoint() { return (root1 + root2 + root3) / 3.; }

// ======================
//   Complex Operations
// ======================

// Complex math helper functions
vec2 mul(vec2 a, vec2 b) { return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }

vec2 div(vec2 a, vec2 b) { return vec2(a.x * b.x + a.y * b.y, a.y * b.x - a.x * b.y) / dot(b, b); }

vec2 c_exp(vec2 z) { return exp(z.x) * vec2(cos(z.y), sin(z.y)): }

vec2 f(vec2 z) {
    return 
        mul(mul(z, mul(z,z)), coef3) +
        mul(mul(z, z), coef2) +
        mul(z, coef1) +
        coef0;
}

// Derivative f'(z) = 3z^2
vec2 df(vec2 z) {
    return 
        3.*mul(mul(z, z), coef3) +
        2.*mul(z, coef2) +
        coef1;
}

vec2 d2f(vec2 z) {
    return 
        3.*2.*mul(z, coef3) +
        2.*coef2;
}

// ======================
//         METHODS 
// ======================

vec2 newton(vec2 z) {
    return z - div(f(z), df(z));
}

vec2 deriv_newton(vec2 z) {
    return div( 
        mul(d2f(z), f(z)),
        mul(df(z), df(z))
    );
}

vec2 halley(vec2 z) {
    return z - div(
        mul(f(z), df(z)),
        mul(df(z), df(z)) - 0.5f*mul(f(z), d2f(z))
    );
}

vec2 young_oiler(vec2 z, inout vec2 zp, inout vec2 zpp) {
    vec2 d = div(f(z)-f(zp), z - zp);
    vec2 d_p = div(f(zp)-f(zpp), zp - zpp);
    vec2 d2 = div(d - d_p, z - zpp);

    vec2 next_z = z - div(
        mul(f(z), d),
        mul(d, d) - mul(f(zp), d2)
    );

    zpp = zp;
    zp = z;

    return next_z;
}

vec2 oiler(vec2 z, inout vec2 zp, inout vec2 zpp) {
    vec2 d = div(f(z)-f(zp), z - zp);
    vec2 d_p = div(f(zp)-f(zpp), zp - zpp);
    vec2 d2 = div(d - d_p, z - zpp);

    vec2 next_z = z - div(
        mul(f(z), d),
        mul(d, d) - mul(f(z), d2)
    );

    zpp = zp;
    zp = z;

    return next_z;
}

float min_root_distance(vec2 z) {
    float d1 = length(root1 - z);
    float d2 = length(root2 - z);
    float d3 = length(root3 - z);
    return min(d1, min(d2, d3));
}

vec3 domain_color_complex(vec2 z) {
    // return 0.5 + 0.5 * cos(atan(z.y, z.x) + vec3(0.0, 2.0, 4.0)) * length(z);
    return cos(atan(z.y, z.x) + vec3(0.0, 2.0, 4.0)) * (length(z));
}

vec3 limit_color_complex(vec2 z) {
    if (any(isnan(z)) || any(isinf(z))) return INFINITY_COLOR;
    if (min_root_distance(z) > EPSILON) return CYCLE_COLOR;

    float d1 = length(root1 - z);
    float d2 = length(root2 - z);
    float d3 = length(root3 - z);

    if      (d1 <= min(d2,d3)) return color1;
    else if (d2 <= min(d1,d3)) return color2;
    else if (d3 <= min(d1,d2)) return color3;

    return vec3(0.);
}

void main() {
    vec2 pixel_z = xyz_coords.xy;

    vec2 zpp, zp, z;

    if (mode == METHOD_OILER || mode == METHOD_YOUNG_OILER) {
        zpp = pixel_z;
        zp = zpp + vec2(GOLDEN_RATIO, 0.);
        // zp = z0;
        z = zp - div(f(zp), div(f(zp)-f(zpp),zp - zpp));
    } else {
        z = pixel_z;
    }

    vec2 c = z;

    float iter = 0.0;

    for(; iter < int(MAX_ITERATIONS); iter++) {
        if (mode == METHOD_NEWTON)           z = newton(z);
        else if (mode == METHOD_HALLEY)      z = halley(z);
        else if (mode == METHOD_YOUNG_OILER) z = young_oiler(z, zp, zpp);
        else if (mode == METHOD_OILER)       z = oiler(z, zp, zpp);


        if (min_root_distance(z) < EPSILON) break;
    }

    vec3 color = vec3(1.);

    if (color_mode == COLOR_DOMAIN) {
        color = domain_color_complex(z);
    } else if (color_mode == COLOR_LIMITING) {
        color = limit_color_complex(z);
    }

    frag_color = vec4(color, 1.0);
}
