struct VSInput {
  float3 point : POSITION;
};

struct VSOutput {
  float4 position : SV_Position;
  float3 xyz_coords : TEXCOORD0;
  float clip0 : SV_ClipDistance0;
  float clip1 : SV_ClipDistance1;
  float clip2 : SV_ClipDistance2;
  float clip3 : SV_ClipDistance3;
};

ConstantBuffer<float> scale_factor;
ConstantBuffer<float3> offset;
ConstantBuffer<float> is_fixed_in_frame;
ConstantBuffer<float4x4> view;
ConstantBuffer<float> focal_distance;
ConstantBuffer<float3> frame_rescale_factors;
ConstantBuffer<float4> clip_plane0;
ConstantBuffer<float4> clip_plane1;
ConstantBuffer<float4> clip_plane2;
ConstantBuffer<float4> clip_plane3;

[shader("vertex")]
VSOutput vs_main(VSInput input) {
  VSOutput vs_out;

  // vs_out.xyz_coords = (input.point - offset) / scale_factor;
  vs_out.xyz_coords = (input.point);

  var result = float4(input.point.xyz, 1.0);
  vs_out.xyz_coords.x = scale_factor;
  // result = lerp(view * result, result, is_fixed_in_frame);
  // result = mul(view, result);

  // result.xyz *= frame_rescale_factors;
  // result.w = 1.0 - result.z;
  // result.z *= -0.1;
  vs_out.position = result;

  if (any(clip_plane0.xyz != float3(0.0, 0.0, 0.0))) {
    vs_out.clip0 = dot(float4(input.point, 1.0), clip_plane0);
  }
  if (any(clip_plane1.xyz != float3(0.0, 0.0, 0.0))) {
    vs_out.clip0 = dot(float4(input.point, 1.0), clip_plane1);
  }
  if (any(clip_plane2.xyz != float3(0.0, 0.0, 0.0))) {
    vs_out.clip2 = dot(float4(input.point, 1.0), clip_plane2);
  }
  if (any(clip_plane3.xyz != float3(0.0, 0.0, 0.0))) {
    vs_out.clip3 = dot(float4(input.point, 1.0), clip_plane3);
  }

  return vs_out;
}

[shader("fragment")]
float4 fs_main(VSOutput input) : SV_Target {
  return float4(abs(input.xyz_coords), 1.0);
  // return float4(1.0, 0.f, 0.f, 1.f);
}
