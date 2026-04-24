#version 330

precision highp float;

// Math Constants
const float GOLDEN_RATIO = (1 + sqrt(5.)) / 2.;

// What counts as 'close-enough' / minimum number we really care about
uniform float u_epsilon = 1E-3f;

// number of iterations before quitting
uniform uint u_max_iterations = 500u;

// enums for what method to use
const uint METHOD_NEWTON = 0u;
const uint METHOD_HALLEY = 1u;
const uint METHOD_YOUNG_OILER = 2u;
const uint METHOD_OILER = 3u;
const uint METHOD_LATTE = 4u;
const uint METHOD_SECANT = 5u;

// enums for how to color limit behaviors
const uint COLOR_DOMAIN = 0u;
const uint COLOR_LIMITING = 1u;

uniform uint u_mode = METHOD_NEWTON;

uniform uint u_color_mode = COLOR_LIMITING;

uniform vec2 u_oiler_offset = vec2(GOLDEN_RATIO, 0.);

uniform vec2 u_secant_offset = vec2(0.01, 0.0);

uniform float scale_factor = 1.0;

uniform float u_julia_highlight = 0.0;

// whether or not iteration's should stop when we converge to a root, if this is off then this will instead stop when the step size is too small
uniform uint u_should_break_on_convergence = 0u;

// Constants for polynomial control
const uint MAX_ROOTS = 12u;
const uint MAX_COEFS = MAX_ROOTS + 1u;

// degree of polynomial, basically the number of roots
uniform uint u_degree = 3u;

// Different roots for the polynomial
uniform vec2 u_root1 = vec2(0., 0.);
uniform vec2 u_root2 = vec2(0., 0.);
uniform vec2 u_root3 = vec2(0., 0.);
uniform vec2 u_root4 = vec2(0., 0.);
uniform vec2 u_root5 = vec2(0., 0.);
uniform vec2 u_root6 = vec2(0., 0.);
uniform vec2 u_root7 = vec2(0., 0.);
uniform vec2 u_root8 = vec2(0., 0.);
uniform vec2 u_root9 = vec2(0., 0.);
uniform vec2 u_root10 = vec2(0., 0.);
uniform vec2 u_root11 = vec2(0., 0.);
uniform vec2 u_root12 = vec2(0., 0.);

// Color of said roots
uniform vec4 u_color1 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color2 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color3 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color4 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color5 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color6 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color7 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color8 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color9 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color10 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color11 = vec4(vec3(1., 0., 0.), 1.);
uniform vec4 u_color12 = vec4(vec3(1., 0., 0.), 1.);

uniform uint u_should_color_cycles = 1u;

// color for when seed blows up to infinity
uniform vec4 u_color_infinity = vec4(1.);

// color for when seed falls in cycle, only used if u_should_color_cycles is 1
uniform vec4 u_color_cycle = vec4(0., 0., 0., 1.);

uniform vec2 u_z0 = vec2(0.);

// whether or not to vary the brighness of a pixel based on hwo fast it converges
uniform uint u_do_iteration_coloring = 1u;

// whether or not to color in parameter-space mode
uniform uint u_parametric = 0u;

// control for the relaxed newton's method, N(z) = z - u_relaxed_newtons * P(z)/P'(z)
uniform float u_relaxed_newtons = 1.0f;

// global opacity
uniform float u_opacity = 1.0;

// Fragment Shader Inputs and Outputs
in vec3 xyz_coords;
uniform vec3 u_plane_offset = vec3(0.);

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

vec4 index_to_color(uint index) {
    vec4 u_colors[MAX_ROOTS] = vec4[](
            u_color1,
            u_color2,
            u_color3,
            u_color4,
            u_color5,
            u_color6,
            u_color7,
            u_color8,
            u_color9,
            u_color10,
            u_color11,
            u_color12
        );

    return u_colors[index];
}

// ======================
//   Complex Operations
// ======================

// Complex math helper functions
vec2 cmul(in vec2 a, in vec2 b) {
    return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

vec2 cdiv(in vec2 a, in vec2 b) {
    return vec2(a.x * b.x + a.y * b.y, a.y * b.x - a.x * b.y) / dot(b, b);
}

vec2 csub(in vec2 a, in vec2 b) {
    return a - b;
}

vec2 cadd(in vec2 a, in vec2 b) {
    return a + b;
}

vec2 cpowi(in vec2 z, in int m) {
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

struct Polynomial {
    vec2 coefs[MAX_COEFS];
    vec2 roots[MAX_ROOTS];
    uint degree;
};

void Polynomial_gen_coefs_from_roots(inout Polynomial polynomial) {
    for (uint i = 0u; i < MAX_COEFS; i++) polynomial.coefs[i] = vec2(0.0);
    polynomial.coefs[0] = vec2(1.0, 0.0); // Start with P(z) = 1

    for (uint i = 0u; i < polynomial.degree; i++) {
        vec2 root = polynomial.roots[i];

        // multiply the curr polynomial by (z - root)
        // temp = coefs * -root + coefs_shifted * 1
        vec2 next_coefs[MAX_COEFS];

        for (uint j = 0u; j < MAX_COEFS; j++) next_coefs[j] = vec2(0.0);

        for (uint j = 0u; j <= i; j++) {
            // new coeff = prev coeff * -root + prev_coeff_shifted
            next_coefs[j] += cmul(polynomial.coefs[j], -root);
            next_coefs[j + 1u] += polynomial.coefs[j];
        }
        polynomial.coefs = next_coefs;
    }
}

// populates the uniform roots into the root array
void populate_uniform_roots(out vec2 roots[MAX_ROOTS], out uint degree) {
    roots = vec2[](
            u_root1,
            u_root2,
            u_root3,
            u_root4,
            u_root5,
            u_root6,
            u_root7,
            u_root8,
            u_root9,
            u_root10,
            u_root11,
            u_root12
        );
    degree = u_degree;
}

// populates a given root array, num of roots, and coefs with the roots & coefficients of the polynomial described via the uniforms u_root[1:10], with this polynomial being of degree u_degree
void populate_uniform_poylnomial(inout Polynomial polynomial) {
    populate_uniform_roots(polynomial.roots, polynomial.degree);
    Polynomial_gen_coefs_from_roots(polynomial);
}

/// Evaluate given polynomial at z
vec2 Polynomial_eval(in Polynomial polynomial, in vec2 z) {
    vec2 result = vec2(0.0);

    for (int i = int(polynomial.degree); i >= 0; i--) {
        result = cmul(result, z) + polynomial.coefs[i];
    }

    return result;
}

/// evaluate first derivative P'(z)
vec2 Polynomial_eval_deriv1(in Polynomial polynomial, in vec2 z) {
    vec2 result = vec2(0.0);
    for (int i = int(polynomial.degree); i >= 1; i--) {
        // P'(z) = Sum(i * a_i * z^(i-1))
        vec2 term = polynomial.coefs[i] * float(i);
        result = cmul(result, z) + term;
    }
    return result;
}

/// Evaluate second derivative P''(z)
vec2 Polynomial_eval_deriv2(in Polynomial polynomial, in vec2 z) {
    vec2 result = vec2(0.0);
    for (int i = int(polynomial.degree); i >= 2; i--) {
        vec2 term = polynomial.coefs[i] * float(i * (i - 1));
        result = cmul(result, z) + term;
    }
    return result;
}

// ======================
//         METHODS
// ======================

vec2 newton(
    in Polynomial polynomial,
    in vec2 z
) {
    return z - u_relaxed_newtons * cdiv(Polynomial_eval(polynomial, z), Polynomial_eval_deriv1(polynomial, z));
}

vec2 halley(in Polynomial polynomial, vec2 z) {
    vec2 fz = Polynomial_eval(polynomial, z);
    vec2 dfz = Polynomial_eval_deriv1(polynomial, z);
    vec2 d2fz = Polynomial_eval_deriv2(polynomial, z);

    return z - cdiv(
            cmul(fz, dfz),
            cmul(dfz, dfz) - 0.5f * cmul(fz, d2fz)
        );
}

vec2 secant(in Polynomial polynomial, vec2 z, inout vec2 zp) {
    vec2 fz = Polynomial_eval(polynomial, z);
    vec2 fzp = Polynomial_eval(polynomial, zp);

    vec2 d = cdiv(fz - fzp, z - zp);

    vec2 next_z = z - cdiv(fz, d);

    zp = z;

    return next_z;
}

vec2 young_oiler(in Polynomial polynomial, vec2 z, inout vec2 zp, inout vec2 zpp) {
    vec2 fz = Polynomial_eval(polynomial, z);
    vec2 fzp = Polynomial_eval(polynomial, zp);
    vec2 fzpp = Polynomial_eval(polynomial, zpp);

    vec2 d = cdiv(fz - fzp, z - zp);
    vec2 d_p = cdiv(fzp - fzpp, zp - zpp);
    vec2 d2 = cdiv(d - d_p, z - zpp);

    vec2 next_z =
        z - cdiv(
                cmul(fz, d),
                cmul(d, d) - cmul(fzp, d2)
            );

    zpp = zp;
    zp = z;

    return next_z;
}

vec2 oiler(in Polynomial polynomial, in vec2 z, inout vec2 zp, inout vec2 zpp) {
    vec2 fz = Polynomial_eval(polynomial, z);
    vec2 fzp = Polynomial_eval(polynomial, zp);
    vec2 fzpp = Polynomial_eval(polynomial, zpp);

    vec2 d = cdiv(fz - fzp, z - zp);
    vec2 d_p = cdiv(fzp - fzpp, zp - zpp);
    vec2 d2 = cdiv(d - d_p, z - zpp);

    vec2 next_z = z - cdiv(
                cmul(fz, d),
                cmul(d, d) - cmul(fz, d2)
            );

    zpp = zp;
    zp = z;

    return next_z;
}

vec2 latte(vec2 z) {
    return cdiv(cpowi(cpowi(z, 2) + vec2(1., 0.), 2), cmul(4. * z, cpowi(z, 2) - vec2(1., 0.)));
}

bool close_enough_to_root(in Polynomial polynomial, in vec2 z, float epsilon) {
    for (uint i = 0u; i < polynomial.degree; i++) {
        if (dot(z - polynomial.roots[i], z - polynomial.roots[i]) < epsilon * epsilon) return true;
    }

    return false;
}

bool close_enough_to_root(in Polynomial polynomial, in vec2 z) {
    return close_enough_to_root(polynomial, z, u_epsilon);
}

float min_root_distance(in Polynomial polynomial, in vec2 z, out uint min_index) {
    min_index = 0u;

    if (polynomial.degree == 0u) {
        return 1E99;
    }

    float min_dist = dot(polynomial.roots[0] - z, polynomial.roots[0] - z);

    for (uint i = 1u; i < polynomial.degree; i++) {
        float dist_to_root = dot(polynomial.roots[i] - z, polynomial.roots[i] - z);

        if (dist_to_root < min_dist) {
            min_dist = dist_to_root;
            min_index = i;
        }
    }

    return sqrt(min_dist);
}

vec4 domain_color_complex(vec2 z) {
    // return (atan(z.y, z.x) + vec3(0.0, 2.0, 4.0)) * (length(z));
    if (any(isinf(z)) || any(isnan(z))) return vec4(1.);

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
    return vec4(color, 1.);
}

vec4 limit_color_complex(
    vec2 z,
    float iterations,
    Polynomial polynomial
) {
    if (any(isnan(z)) || any(isinf(z))) return u_color_infinity;

    uint min_root_index;

    float min_dist = min_root_distance(polynomial, z, min_root_index);

    if (u_should_color_cycles == 1u && min_dist > u_epsilon) {
        return u_color_cycle;
    }

    vec4 color = index_to_color(min_root_index);

    // if (u_do_iteration_coloring) {
    // color *= 0.5f - 10.f * log(0.9f - 1.1f * float(iterations) / float(u_max_iterations));

    color.rgb = rgb_to_oklch(color.rgb);

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

    color.rgb = oklch_to_rgb(color.rgb);

    return color;
}

void iteration_setup(in Polynomial polynomial, vec2 initial_z, inout vec2 z, inout vec2 zp, inout vec2 zpp, uint iter_mode) {
    if (iter_mode == METHOD_OILER || iter_mode == METHOD_YOUNG_OILER) {
        zpp = initial_z;
        zp = zpp + u_oiler_offset;

        // secant method
        vec2 fzp = Polynomial_eval(polynomial, zp);
        vec2 fzpp = Polynomial_eval(polynomial, zpp);
        z = zp - cdiv(fzp, cdiv(fzp - fzpp, zp - zpp));
    } else if (iter_mode == METHOD_SECANT) {
        zp = initial_z;
        z = zp + u_secant_offset;
    } else
    {
        z = initial_z;
    }
}

void single_iteration(in Polynomial polynomial, inout vec2 z, inout vec2 zp, inout vec2 zpp, uint iter_mode) {
    if (iter_mode == METHOD_NEWTON) {
        z = newton(polynomial, z);
    }
    else if (iter_mode == METHOD_HALLEY) {
        z = halley(polynomial, z);
    }
    else if (iter_mode == METHOD_YOUNG_OILER) {
        z = young_oiler(polynomial, z, zp, zpp);
    }
    else if (iter_mode == METHOD_OILER) {
        z = oiler(polynomial, z, zp, zpp);
    } else if (iter_mode == METHOD_LATTE) {
        z = latte(z);
    } else if (iter_mode == METHOD_SECANT) {
        z = secant(polynomial, z, zp);
    }
}

vec2 iterate_method(in Polynomial polynomial, vec2 initial_z, out uint i, uint iter_mode, out float float_iters) {
    vec2 zpp, zp, z;

    iteration_setup(polynomial, initial_z, z, zp, zpp, iter_mode);

    float curr_len;

    for (i = 0u; i < u_max_iterations; i++) {
        vec2 previous_z = z;

        single_iteration(polynomial, z, zp, zpp, iter_mode);

        float_iters = float(i);
        curr_len = length(previous_z - z);

        if (u_should_break_on_convergence == 0u) {
            if (curr_len < u_epsilon) {
                break;
            }
        }
        else {
            if (close_enough_to_root(polynomial, z)) {
                break;
            }
        }
    }

    if (u_should_break_on_convergence == 0u) {
        float_iters -= log(curr_len) / log(u_epsilon);
    }

    return z;
}

void fragment_parameter_space(out vec4 color, in vec2 pixel_z) {
    uint iterations;
    float f_iters;

    Polynomial polynomial;
    populate_uniform_roots(polynomial.roots, polynomial.degree);

    // overwrite first root
    polynomial.roots[0] = pixel_z;

    Polynomial_gen_coefs_from_roots(polynomial);

    // get center of all roots
    vec2 z0 = vec2(0.f);
    for (uint i = 0u; i < polynomial.degree; i++) {
        z0 += polynomial.roots[i];
    }
    z0 /= float(polynomial.degree);

    vec2 z = iterate_method(polynomial, z0, iterations, u_mode, f_iters);

    if (u_color_mode == COLOR_DOMAIN) {
        color = domain_color_complex(z);
    } else if (u_color_mode == COLOR_LIMITING) {
        color = limit_color_complex(z, f_iters, polynomial);
    } else {
        color = vec4(1., 0., 0.1, 1.);
    }
}

void fragment_seedspace(out vec4 color, in vec2 pixel_z) {
    uint iterations;
    float f_iters;

    Polynomial polynomial;
    populate_uniform_poylnomial(polynomial);

    vec2 z = iterate_method(polynomial, pixel_z, iterations, u_mode, f_iters);

    if (u_color_mode == COLOR_DOMAIN) {
        color = domain_color_complex(z);
    } else if (u_color_mode == COLOR_LIMITING) {
        color = limit_color_complex(z, f_iters, polynomial);
    }

    // julia boundry highlights
    if (u_julia_highlight > 0.0) {
        float radius = u_julia_highlight;

        const uint NUM_SAMPLES = 4u;
        vec2[NUM_SAMPLES] zs = vec2[NUM_SAMPLES](
                pixel_z + vec2(radius, 0.0),
                pixel_z + vec2(-radius, 0.0),
                pixel_z + vec2(0.0, radius),
                pixel_z + vec2(0.0, -radius)
            ), zp, zpp;

        for (uint i = 0u; i < NUM_SAMPLES; i++) {
            iteration_setup(polynomial, zs[i], zs[i], zp[i], zpp[i], u_mode);
        }

        float max_dist = 0.0;

        for (uint j = 0u; j < 20u; j++) {
            for (uint i = 0u; i < NUM_SAMPLES; i++) {
                single_iteration(polynomial, zs[i], zp[i], zpp[i], u_mode);
            }
        }

        for (uint i = 0u; i < NUM_SAMPLES; i++) {
            max_dist = max(max_dist, distance(zs[i], zs[(i + 1u) % NUM_SAMPLES]));
            max_dist = max(max_dist, distance(z, zs[i]));
        }

        color *= 1.0 * smoothstep(0., 0.1, max_dist);
    }
}

vec4 fragment(in vec2 pixel_z) {
    vec4 color = vec4(1.);

    if (u_parametric == 0u) {
        fragment_seedspace(color, pixel_z);
    } else if (u_parametric == 1u) {
        fragment_parameter_space(color, pixel_z);
    }

    return color;
}

#INSERT finalize_color.glsl

void main() {
    vec4 color = fragment((xyz_coords + u_plane_offset).xy);
    frag_color = finalize_color(vec4(color.rgb, color.a * u_opacity), xyz_coords, vec3(0.0, 0.0, 1.0));
}
