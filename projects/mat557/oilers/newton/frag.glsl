#version 330

uniform vec2 u_resolution;
uniform float u_time;

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
        3*mul(mul(z, z), coef3) +
        2*mul(z, coef2) +
        coef1;
}

void main() {
    vec2 z = xyz_coords.xy;
    float iter = 0.0;
    const float maxIter = 100.0;

    // Newton-Raphson iteration
    for(float i = 0.0; i < maxIter; i++) {
        z = z - div(f(z), df(z));
        iter = i;
        if(length(f(z)) < 0.0001) break;
    }

    // Color based on which root it converged to
    float angle = atan(z.y, z.x);
    vec3 color = 0.5 + 0.5 * cos(angle + vec3(0.0, 2.0, 4.0)); // Color wheel
    
    // Darken based on iterations


    float d1 = length(root1 - z);
    float d2 = length(root2 - z);
    float d3 = length(root3 - z);

    if (d1 < d2 && d1 < d3) color = color1;
    if (d2 < d1 && d2 < d3) color = color2;
    if (d3 < d2 && d3 < d1) color = color3;

    if (min(d1,min(d2,d3)) > 1E-3) {
        color = vec3(0.);
    }

    fragColor = vec4(color, 1.0);
    // fragColor = vec4(c, sin(u_time), 1.0);
    // fragColor = vec4(gl_FragCoord.xy, sin(u_time), 1.0);
    // fragColor = vec4(0.0, 1.0, 1.0, 1.0);
    //
    // fragColor = vec4(xyz_coords.xy, sin(u_time),1.0);
}
