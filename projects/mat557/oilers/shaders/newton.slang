static constexpr int MAX_COEFS = 4;
static constexpr int METHOD_NEWTON = 0;
static constexpr int METHOD_HALLEY = 1;
static constexpr int METHOD_YOUNG_OILER = 2;
static constexpr int METHOD_OILER = 3;

static constexpr int COLOR_DOMAIN = 0;
static constexpr int COLOR_LIMITING = 1;

static constexpr float GOLDEN_RATIO = (1 + sqrt(5.)) / 2.;
static constexpr float EPSILON = 1E-5f;

// #define float2 dfloat2
// #define float double

static constexpr uint MAX_ITERATIONS = 100u;

static constexpr float3 INFINITY_COLOR = float3(1.);
static constexpr float3 CYCLE_COLOR = float3(0.);

uniform int coeff_count;
uniform float3 color1;
uniform float3 color2;
uniform float3 color3;

uniform float2 coef0;
uniform float2 coef1;
uniform float2 coef2;
uniform float2 coef3;
uniform float2 root1;
uniform float2 root2;
uniform float2 root3;

uniform float2 z0;

uniform int mode;

uniform int color_mode;

in float3 xyz_coords;

float2 root_midpoint() { return (root1 + root2 + root3) / 3.; }

// ======================
//   Complex Operations
// ======================

// Complex math helper functions
float2 mul(float2 a, float2 b) {
  return float2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

float2 div(float2 a, float2 b) {
  return float2(a.x * b.x + a.y * b.y, a.y * b.x - a.x * b.y) / dot(b, b);
}

float2 c_exp(float2 z) { return exp(z.x) * float2(cos(z.y), sin(z.y)); }

float2 f(float2 z) {
  return mul(mul(z, mul(z, z)), coef3) + mul(mul(z, z), coef2) + mul(z, coef1) +
         coef0;
}

// Derivative f'(z) = 3z^2
float2 df(float2 z) {
  return 3. * mul(mul(z, z), coef3) + 2. * mul(z, coef2) + coef1;
}

float2 d2f(float2 z) { return 3. * 2. * mul(z, coef3) + 2. * coef2; }

// ======================
//         METHODS
// ======================

float2 newton(float2 z) { return z - div(f(z), df(z)); }

float2 deriv_newton(float2 z) {
  return div(mul(d2f(z), f(z)), mul(df(z), df(z)));
}

float2 halley(float2 z) {
  return z -
         div(mul(f(z), df(z)), mul(df(z), df(z)) - 0.5f * mul(f(z), d2f(z)));
}

float2 young_oiler(float2 z, inout float2 zp, inout float2 zpp) {
  float2 d = div(f(z) - f(zp), z - zp);
  float2 d_p = div(f(zp) - f(zpp), zp - zpp);
  float2 d2 = div(d - d_p, z - zpp);

  float2 next_z = z - div(mul(f(z), d), mul(d, d) - mul(f(zp), d2));

  zpp = zp;
  zp = z;

  return next_z;
}

float2 oiler(float2 z, inout float2 zp, inout float2 zpp) {
  float2 d = div(f(z) - f(zp), z - zp);
  float2 d_p = div(f(zp) - f(zpp), zp - zpp);
  float2 d2 = div(d - d_p, z - zpp);

  float2 next_z = z - div(mul(f(z), d), mul(d, d) - mul(f(z), d2));

  zpp = zp;
  zp = z;

  return next_z;
}

float min_root_distance(float2 z) {
  float d1 = length(root1 - z);
  float d2 = length(root2 - z);
  float d3 = length(root3 - z);
  return min(d1, min(d2, d3));
}

float3 domain_color_complex(float2 z) {
  // return 0.5 + 0.5 * cos(atan(z.y, z.x) + float3(0.0, 2.0, 4.0)) * length(z);
  return cos(atan(z.y / z.x) + float3(0.0, 2.0, 4.0)) * (length(z));
}

float3 limit_color_complex(float2 z) {
  if (any(isnan(z)) || any(isinf(z)))
    return INFINITY_COLOR;
  if (min_root_distance(z) > EPSILON)
    return CYCLE_COLOR;

  float d1 = length(root1 - z);
  float d2 = length(root2 - z);
  float d3 = length(root3 - z);

  if (d1 <= min(d2, d3))
    return color1;
  else if (d2 <= min(d1, d3))
    return color2;
  else if (d3 <= min(d1, d2))
    return color3;

  return float3(0.);
}

[shader("fragment")]
float4 fragmentMain() : SV_Target {
  float2 pixel_z = xyz_coords.xy;

  float2 zpp, zp, z;

  if (mode == METHOD_OILER || mode == METHOD_YOUNG_OILER) {
    zpp = pixel_z;
    zp = zpp + float2(GOLDEN_RATIO, 0.);
    // zp = z0;
    z = zp - div(f(zp), div(f(zp) - f(zpp), zp - zpp));
  } else {
    z = pixel_z;
  }

  float2 c = z;

  for (uint i = 0u; i < float(MAX_ITERATIONS); i++) {
    if (mode == METHOD_NEWTON)
      z = newton(z);
    else if (mode == METHOD_HALLEY)
      z = halley(z);
    else if (mode == METHOD_YOUNG_OILER)
      z = young_oiler(z, zp, zpp);
    else if (mode == METHOD_OILER)
      z = oiler(z, zp, zpp);
    if (min_root_distance(z) < EPSILON)
      break;
  }

  float3 color = float3(1.);

  if (color_mode == COLOR_DOMAIN) {
    color = domain_color_complex(z);
  } else if (color_mode == COLOR_LIMITING) {
    color = limit_color_complex(z);
  }

  return float4(color, 1.0);
}

