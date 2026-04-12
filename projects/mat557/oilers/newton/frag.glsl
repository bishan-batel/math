#version 330

precision highp float;
precision highp vec2;
precision highp vec3;
precision highp vec4;

const uint METHOD_NEWTON = 0u;
const uint METHOD_HALLEY = 1u;
const uint METHOD_YOUNG_OILER = 2u;
const uint METHOD_OILER = 3u;
const uint METHOD_LATTE = 4u;
const uint METHOD_SECANT = 5u;

const uint COLOR_DOMAIN = 0u;
const uint COLOR_LIMITING = 1u;

const float GOLDEN_RATIO = (1 + sqrt(5.)) / 2.;
uniform float u_epsilon = 1E-5f;

uniform vec2 u_oiler_offset = vec2(GOLDEN_RATIO, 0.);
uniform vec2 u_secant_offset = vec2(0.01, 0.0);

#INSERT finalize_color.glsl

uniform float scale_factor;

uniform float u_julia_highlight = 0.0;

uniform uint u_should_color_cycles = 1u;

uniform uint u_max_iterations = 500u;

uniform vec3 u_color_infinity;
uniform vec3 u_color_cycle;

uniform uint u_should_break_on_convergence = 0u;

uniform vec3 u_color1;
uniform vec3 u_color2;
uniform vec3 u_color3;

uniform vec2 u_root1;
uniform vec2 u_root2;
uniform vec2 u_root3;

uniform vec2 u_z0 = vec2(0.);

uniform uint u_mode = METHOD_NEWTON;

uniform uint u_color_mode = COLOR_LIMITING;

uniform uint u_do_iteration_coloring = 1u;
uniform uint u_parametric = 0u;

in vec3 xyz_coords;

out vec4 frag_color;

// ======================
//    Color Operations
// ======================

vec3 hsv_to_rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 rgb_to_oklch(vec3 rgb) {
    // convert srgb to linear rgb
    vec3 linear_rgb;
    linear_rgb.r = (rgb.r <= 0.04045) ? rgb.r / 12.92 : pow((rgb.r + 0.055) / 1.055, 2.4);
    linear_rgb.g = (rgb.g <= 0.04045) ? rgb.g / 12.92 : pow((rgb.g + 0.055) / 1.055, 2.4);
    linear_rgb.b = (rgb.b <= 0.04045) ? rgb.b / 12.92 : pow((rgb.b + 0.055) / 1.055, 2.4);

    // convert linear rgb to xyz (CIE 1931 XYZ color space) primary color space
    float x = linear_rgb.r * 0.4124 + linear_rgb.g * 0.3576 + linear_rgb.b * 0.1805;
    float y = linear_rgb.r * 0.2126 + linear_rgb.g * 0.7152 + linear_rgb.b * 0.0722;
    float z = linear_rgb.r * 0.0193 + linear_rgb.g * 0.1192 + linear_rgb.b * 0.9505;

    // CIE standard illuminant D65 (color temperature of ~6504K) in the xyz color space
    // For reference: https://en.wikipedia.org/wiki/Standard_illuminant
    float xd65 = 0.95047;
    float yd65 = 1.0;
    float zd65 = 1.08883;

    // normalize xyz color values by the natural daylight factor
    float x_norm = x / xd65;
    float y_norm = y / yd65;
    float z_norm = z / zd65;

    // precompute xyz values for oklab conversion later
    float fx = (x_norm > 0.008856) ? pow(x_norm, 1.0 / 3.0) : (7.787 * x_norm + 16.0 / 116.0);
    float fy = (y_norm > 0.008856) ? pow(y_norm, 1.0 / 3.0) : (7.787 * y_norm + 16.0 / 116.0);
    float fz = (z_norm > 0.008856) ? pow(z_norm, 1.0 / 3.0) : (7.787 * z_norm + 16.0 / 116.0);

    // convert from xyz to oklab
    float l_lab = 116.0 * fy - 16.0;
    float a_lab = 500.0 * (fx - fy);
    float b_lab = 200.0 * (fy - fz);

    // convert from oklab to oklch
    float c = sqrt(a_lab * a_lab + b_lab * b_lab);
    float h = degrees(atan(b_lab, a_lab));
    if (h < 0.0) {
        h += 360.0;
    }

    return vec3(l_lab / 100.0, c / 100.0, h);
}

vec3 oklch_to_rgb(vec3 lch) {
    // scale l and h back to values between 0 and 100 and h to radians from degrees
    float l = lch.x * 100.0;
    float c = lch.y * 100.0;
    float h_rad = radians(lch.z);

    // convert c and h to oklab a and b
    float a_lab = cos(h_rad) * c;
    float b_lab = sin(h_rad) * c;

    // precompute oklab values for xyz conversion later
    float fy = (l + 16.0) / 116.0;
    float fx = a_lab / 500.0 + fy;
    float fz = fy - b_lab / 200.0;
    vec3 f = vec3(fx, fy, fz);
    vec3 f_cubed = pow(f, vec3(3.0));

    // inverse oklab (to xyz) conversion
    vec3 mask_xyz = step(vec3(0.008856), f_cubed);
    vec3 xyz = mask_xyz * f_cubed + (1.0 - mask_xyz) * ((f - vec3(16.0 / 116.0)) / 7.787);
    vec3 d65 = vec3(0.95047, 1.0, 1.08883);
    xyz *= d65;

    // convert from xyz to linear rgb
    float r = xyz.x * 3.2406 + xyz.y * -1.5372 + xyz.z * -0.4986;
    float g = xyz.x * -0.9689 + xyz.y * 1.8758 + xyz.z * 0.0415;
    float b = xyz.x * 0.0557 + xyz.y * -0.2040 + xyz.z * 1.0570;
    vec3 linear_rgb = vec3(r, g, b);

    // gamma correction mask
    vec3 linear_gamma = linear_rgb * 12.92;
    vec3 non_linear_gamma = 1.055 * pow(linear_rgb, vec3(1.0 / 2.4)) - 0.055;

    // linear rgb to srgb
    vec3 mask_rgb = step(linear_rgb, vec3(0.0031308));
    vec3 srgb = mix(non_linear_gamma, linear_gamma, mask_rgb);

    return clamp(srgb, 0.0, 1.0);
}

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

vec2 secant(vec2 z, inout vec2 zp) {
    vec2 d = cdiv(f(z) - f(zp), z - zp);

    vec2 next_z = z - cdiv(f(z), d);

    zp = z;

    return next_z;
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

vec2 latte(vec2 z) {
    return cdiv(cpowi(cpowi(z, 2) + vec2(1., 0.), 2), cmul(4. * z, cpowi(z, 2) - vec2(1., 0.)));
}

float min_root_distance(vec2 z, vec2 r1, vec2 r2, vec2 r3) {
    float d1 = dot(r1 - z, r1 - z);
    float d2 = dot(r2 - z, r2 - z);
    float d3 = dot(r3 - z, r3 - z);
    return sqrt(min(d1, min(d2, d3)));
}

vec3 domain_color_complex(vec2 z) {
    // return (atan(z.y, z.x) + vec3(0.0, 2.0, 4.0)) * (length(z));
    if (any(isinf(z)) || any(isnan(z))) return vec3(1.);

    float r = length(z);
    float theta = atan(z.y, z.x) / 6.28318 + 0.5; // Map [-PI, PI] to [0, 1]

    // theta to degrees
    theta *= 360;

    // Simple hue mapping; 'hsv2rgb' is a standard utility function

    float light = 0.6f / exp(-r * 0.1);
    vec3 color = oklch_to_rgb(vec3(
                clamp(log(1. + r * 0.5), 0., 1.),
                clamp(2.0f - log(r), 0., 1.),
                theta
            ));
    // if (any(isinf(color)) || any(isnan(color))) return vec3(1.);

    // Add grid lines for magnitude (logarithmic scale)
    // color *= 0.8 + 0.2 * sin(log(r) * 10.0);
    // color *= length()
    return color;
}

vec3 limit_color_complex(
    vec2 z,
    float iterations,
    vec2 r1,
    vec2 r2,
    vec2 r3
) {
    if (any(isnan(z)) || any(isinf(z))) return u_color_infinity;

    if (u_should_color_cycles == 1u && min_root_distance(z, r1, r2, r3) > u_epsilon) {
        return u_color_cycle;
    }

    float d1 = length(r1 - z);
    float d2 = length(r2 - z);
    float d3 = length(r3 - z);

    vec3 color = vec3(0.);

    if (d1 <= min(d2, d3)) color = u_color1;
    else if (d2 <= min(d1, d3)) color = u_color2;
    else if (d3 <= min(d1, d2)) color = u_color3;

    // if (u_do_iteration_coloring) {
    // color *= 0.5f - 10.f * log(0.9f - 1.1f * float(iterations) / float(u_max_iterations));

    color = rgb_to_oklch(color);

    if (u_do_iteration_coloring != 0u) {
        // color.x += pow(
        //     1E1f * pow(clamp(max(0., float(iterations)) / 100.f, 0., 1.), 5),
        //     0.5f
        // );
        //

        float saturation_factor = 5.0;
        // iterations /= float(u_max_iterations);
        color.xy *= 1.0 + (0.01 * saturation_factor) * (iterations - 2 * saturation_factor);
    }

    // color.x = clamp(color.x, 0., 1.);
    // color.y = clamp(color.y, 0., 1.);

    color = oklch_to_rgb(color);

    return color;
}

void single_iteration(inout vec2 z, inout vec2 zp, inout vec2 zpp, vec2 r1, vec2 r2, vec2 r3, uint iter_mode) {
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
    } else if (iter_mode == METHOD_LATTE) {
        z = latte(z);
    } else if (iter_mode == METHOD_SECANT) {
        z = secant(z, zp);
    }
}

void iteration_setup(vec2 initial_z, inout vec2 z, inout vec2 zp, inout vec2 zpp, uint iter_mode) {
    if (iter_mode == METHOD_OILER || iter_mode == METHOD_YOUNG_OILER) {
        zpp = initial_z;
        zp = zpp + u_oiler_offset;
        z = zp - cdiv(f(zp), cdiv(f(zp) - f(zpp), zp - zpp));
    } else if (iter_mode == METHOD_SECANT) {
        zp = initial_z;
        z = zp + u_secant_offset;
    } else
    {
        z = initial_z;
    }
}
vec2 iterate_method(vec2 initial_z, out uint i, uint iter_mode, out float fiters) {
    vec2 zpp, zp, z;

    iteration_setup(initial_z, z, zp, zpp, iter_mode);

    float curr_len;

    for (i = 0u; i < u_max_iterations; i++) {
        vec2 previous_z = z;

        single_iteration(z, zp, zpp, u_root1, u_root2, u_root3, iter_mode);

        fiters = float(i);
        curr_len = length(previous_z - z);

        if (u_should_break_on_convergence == 0u) {
            if (curr_len < u_epsilon) {
                break;
            }
        }
        else {
            if (min_root_distance(z, u_root1, u_root2, u_root3) < u_epsilon) {
                break;
            }
        }
    }

    float e = abs(min_root_distance(z, u_root1, u_root2, u_root3));

    if (u_should_break_on_convergence == 0u) {
        fiters -= log(curr_len) / log(u_epsilon);
    }

    return z;
}

vec3 Parametric_newton(vec2 r1, vec2 r2, vec2 r3) {
    vec2 z0 = (r1 + r2 + r3) / 3.0;
    vec2 z = z0;

    uint i = 0u;
    for (; i < u_max_iterations; i++) {
        z = z - cdiv(cubic_P(z, r1, r2, r3), cubic_dP(z, r1, r2, r3));
        if (min_root_distance(z, r1, r2, r3) < u_epsilon) break;
    }

    if (u_color_mode == COLOR_DOMAIN) {
        return domain_color_complex(z);
    } else if (u_color_mode == COLOR_LIMITING) {
        return limit_color_complex(z, i, r1, r2, r3);
    } else {
        return vec3(0.);
    }
}

void main() {
    vec2 pixel_z = xyz_coords.xy;

    vec3 color = vec3(1.);

    if (u_parametric == 0u) {
        uint iterations;
        float f_iters;

        vec2 z = iterate_method(pixel_z, iterations, u_mode, f_iters);

        if (u_color_mode == COLOR_DOMAIN) {
            color = domain_color_complex(z);
        } else if (u_color_mode == COLOR_LIMITING) {
            color = limit_color_complex(z, f_iters, u_root1, u_root2, u_root3);
        }
    } else if (u_parametric == 1u) {
        uint iterations;
        color = Parametric_newton(pixel_z, u_root2, u_root3);
    }

    // julia boundry highlights
    if (u_julia_highlight > 0.0) {
        float radius = u_julia_highlight;

        const uint NUM_SAMPLES = 4u;
        vec2[NUM_SAMPLES] z = vec2[NUM_SAMPLES](
                pixel_z + vec2(radius, 0.0),
                pixel_z + vec2(-radius, 0.0),
                pixel_z + vec2(0.0, radius),
                pixel_z + vec2(0.0, -radius)
            ), zp, zpp;

        for (uint i = 0u; i < NUM_SAMPLES; i++) {
            iteration_setup(z[i], z[i], zp[i], zpp[i], u_mode);
        }

        float max_dist = 0.0;

        for (uint i = 0u; i < NUM_SAMPLES; i++) {
            for (uint j = 0u; j < u_max_iterations; j++) {
                single_iteration(z[i], zp[i], zpp[i], u_root1, u_root2, u_root3, u_mode);
            }
        }

        for (uint i = 0u; i < NUM_SAMPLES; i++) {
            max_dist = max(max_dist, distance(z[i], z[(i + 1u) % NUM_SAMPLES]));
        }

        color *= 1.0 * smoothstep(0., 0.1, max_dist);
    }

    frag_color = finalize_color(vec4(color, 1.), xyz_coords, vec3(0.0, 0.0, 1.0));
}
