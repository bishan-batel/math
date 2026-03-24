#version 330
precision highp float;

#define MAX_COEFS 4

uniform vec2 u_resolution;
uniform float u_time;

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

uniform vec2 coefs[MAX_COEFS];

in vec3 xyz_coords;

out vec4 fragColor;

// Complex math helper functions
vec2 mul(vec2 a, vec2 b) {
    return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

vec2 div(vec2 a, vec2 b) {
    return vec2(a.x * b.x + a.y * b.y, a.y * b.x - a.x * b.y) / dot(b, b);
}

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

vec2 newton(vec2 z) {
    return z - div(f(z), df(z));
}

vec2 halley(vec2 z) {
    return z - div(
        mul(f(z), df(z)),
        mul(df(z), df(z)) - 0.5f*mul(f(z), d2f(z))
    );
}

vec2 oiler(vec2 z, inout vec2 zp, inout vec2 zpp) {
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

const float GOLDEN_RATIO = (1 + sqrt(5.)) / 2.;

void main() {
    // vec2 z = xyz_coords.xy;
    // vec2 zp = z - vec2(1., 0.);
    // vec2 zpp = zp - vec2(1., 0.);


    vec2 zpp, zp, z;

    if (mode == 2) {
        zpp = xyz_coords.xy;
        zp = zpp + vec2(GOLDEN_RATIO, 0.);
        z = zp - div(f(zp), div(f(zp)-f(zpp),zp - zpp));
    } else {
        z = xyz_coords.xy;
    }

    vec2 c = z;

    float iter = 0.0;
    const float maxIter = 100.0;


    vec2 mandelbrot = vec2(0.);

    // Newton-Raphson iteration
    for(; iter < maxIter; iter++) {
        mandelbrot = mul(mandelbrot, mandelbrot) + c;
        if (mode == 0) {
            z = newton(z);
            // z = mul(z,z) + z0;
        } else if (mode == 1) {
            z = halley(z);
        } else if (mode == 2) {
            z = oiler(z, zp, zpp);
        }

        if(length(f(z)) < 1E-5) break;
    }

    // z = xyz_coords.xy;
    vec3 color = 0.5 + 0.5 * cos(atan(z.y, z.x) + vec3(0.0, 2.0, 4.0)); // Color wheel
    // color = vec3(1.);
    
    float d1 = length(root1 - z);
    float d2 = length(root2 - z);
    float d3 = length(root3 - z);

    if (min(d1,min(d2,d3)) > 1E-4 || any(isnan(z))) color = vec3(0.); else 
        if (d1 <= min(d2,d3)) color = color1;
    else if (d2 <= min(d1,d3)) color = color2;
    else if (d3 <= min(d1,d2)) color = color3;


    // if (length(z) < 2.f) {
        // color = vec3(0.);
    // } else {
        // color = color1;
    // }

    // if (length(mandelbrot) < 2.f) {
    //     color = color1;
    // } else {
    //     color = color2;
    // }

    // color *= iter / maxIter;
    // color *= 0.0;

    fragColor = vec4(color, 1.0);
    // fragColor = vec4(c, sin(u_time), 1.0);
    // fragColor = vec4(gl_FragCoord.xy, sin(u_time), 1.0);
    // fragColor = vec4(0.0, 1.0, 1.0, 1.0);
    //
    // fragColor = vec4(xyz_coords.xy, sin(u_time),1.0);
}
