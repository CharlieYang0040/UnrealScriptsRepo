// 최종 결과물을 담을 변수를 미리 선언합니다.
float result = 0;

// 입력 변수들을 설정합니다.
float lacunarity = 2.0; // 노이즈의 주파수 배율 (고정값)
float gain = 0.5;       // 노이즈의 진폭 배율 (고정값)

// --- 1. 왜곡(Distortion)을 위한 첫 번째 FBM 계산 ---
{
    float2 p = UVs * Scale + float2(Time * Speed * 0.1, Time * Speed * 0.15);
    float amplitude = 0.5;
    float value = 0.0;

    for (int i = 0; i < Octaves; i++)
    {
        // Perlin Noise 로직을 직접 인라인으로 작성
        float2 pi = floor(p);
        float2 pf = frac(p);
        float2 u = pf * pf * (3.0 - 2.0 * pf);

        // Hash 로직을 직접 인라인으로 작성 (4번)
        float2 h1 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(0.0, 0.0), float2(127.1, 311.7)), dot(pi + float2(0.0, 0.0), float2(269.5, 183.3)))) * 43758.5453);
        float2 h2 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(1.0, 0.0), float2(127.1, 311.7)), dot(pi + float2(1.0, 0.0), float2(269.5, 183.3)))) * 43758.5453);
        float2 h3 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(0.0, 1.0), float2(127.1, 311.7)), dot(pi + float2(0.0, 1.0), float2(269.5, 183.3)))) * 43758.5453);
        float2 h4 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(1.0, 1.0), float2(127.1, 311.7)), dot(pi + float2(1.0, 1.0), float2(269.5, 183.3)))) * 43758.5453);
        
        float noise = lerp(lerp(dot(h1, pf - float2(0.0, 0.0)), dot(h2, pf - float2(1.0, 0.0)), u.x),
                           lerp(dot(h3, pf - float2(0.0, 1.0)), dot(h4, pf - float2(1.0, 1.0)), u.x), u.y);

        value += amplitude * noise;
        p *= lacunarity;
        amplitude *= gain;
    }
    result = value * DistortionAmount; // 첫 번째 계산 결과를 왜곡 값으로 저장
}

// --- 2. 최종 용암 모양을 위한 두 번째 FBM 계산 ---
{
    float2 p = UVs * Scale + float2(Time * Speed * -0.08, Time * Speed * 0.2) + result; // 이전 결과(왜곡값)를 UV에 더함
    float amplitude = 0.5;
    float value = 0.0;

    for (int i = 0; i < Octaves; i++)
    {
        // Perlin Noise 로직을 다시 한번 인라인으로 작성
        float2 pi = floor(p);
        float2 pf = frac(p);
        float2 u = pf * pf * (3.0 - 2.0 * pf);

        // Hash 로직을 다시 한번 인라인으로 작성 (4번)
        float2 h1 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(0.0, 0.0), float2(127.1, 311.7)), dot(pi + float2(0.0, 0.0), float2(269.5, 183.3)))) * 43758.5453);
        float2 h2 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(1.0, 0.0), float2(127.1, 311.7)), dot(pi + float2(1.0, 0.0), float2(269.5, 183.3)))) * 43758.5453);
        float2 h3 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(0.0, 1.0), float2(127.1, 311.7)), dot(pi + float2(0.0, 1.0), float2(269.5, 183.3)))) * 43758.5453);
        float2 h4 = -1.0 + 2.0 * frac(sin(float2(dot(pi + float2(1.0, 1.0), float2(127.1, 311.7)), dot(pi + float2(1.0, 1.0), float2(269.5, 183.3)))) * 43758.5453);
        
        float noise = lerp(lerp(dot(h1, pf - float2(0.0, 0.0)), dot(h2, pf - float2(1.0, 0.0)), u.x),
                           lerp(dot(h3, pf - float2(0.0, 1.0)), dot(h4, pf - float2(1.0, 1.0)), u.x), u.y);

        value += amplitude * noise;
        p *= lacunarity;
        amplitude *= gain;
    }
    result = value; // 최종 계산 결과를 저장
}

// 최종 결과물을 0과 1 사이로 정규화하여 반환
return saturate((result + 1.0) * 0.5);