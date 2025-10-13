// 입력 파라미터 준비
float2 p = UVs * Scale;
p.y += Time * 0.1;

// 중간 계산 결과를 담을 변수 선언
float2 q = float2(0,0);
float result = 0;

// Simplex Noise용 상수
const float K1 = 0.366025404; // (sqrt(3)-1)/2
const float K2 = 0.211324865; // (3-sqrt(3))/6

// --- FBM #1 : 왜곡용 q.x 계산 ---
{
    float2 fbm_p = p + float2(0.0, 0.0);
    float value = 0.0;
    float amplitude = 0.5;

    for (int i = 0; i < Octaves; i++)
    {
        // Noise 로직 인라인
        float2 noise_i = floor(fbm_p + (fbm_p.x + fbm_p.y) * K1);
        float2 noise_a = fbm_p - noise_i + (noise_i.x + noise_i.y) * K2;
        float2 noise_o = (noise_a.x > noise_a.y) ? float2(1.0, 0.0) : float2(0.0, 1.0);
        float2 noise_b = noise_a - noise_o + K2;
        float2 noise_c = noise_a - 1.0 + 2.0 * K2;

        float3 h = max(0.5 - float3(dot(noise_a, noise_a), dot(noise_b, noise_b), dot(noise_c, noise_c)), 0.0);
        
        // Hash 로직 인라인
        float2 hash_a = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + 0.0, float2(127.1, 311.7)), dot(noise_i + 0.0, float2(269.5, 183.3)))) * 43758.5453123);
        float2 hash_b = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + noise_o, float2(127.1, 311.7)), dot(noise_i + noise_o, float2(269.5, 183.3)))) * 43758.5453123);
        float2 hash_c = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + 1.0, float2(127.1, 311.7)), dot(noise_i + 1.0, float2(269.5, 183.3)))) * 43758.5453123);

        float3 n = h * h * h * h * float3(dot(noise_a, hash_a), dot(noise_b, hash_b), dot(noise_c, hash_c));
        float noise_val = dot(n, float3(70.0, 70.0, 70.0));
        
        value += amplitude * noise_val;
        fbm_p *= Lacunarity;
        amplitude *= Gain;
    }
    q.x = value;
}

// --- FBM #2 : 왜곡용 q.y 계산 ---
{
    float2 fbm_p = p + float2(5.2, 1.3);
    float value = 0.0;
    float amplitude = 0.5;

    for (int i = 0; i < Octaves; i++)
    {
        // Noise 로직 인라인
        float2 noise_i = floor(fbm_p + (fbm_p.x + fbm_p.y) * K1);
        float2 noise_a = fbm_p - noise_i + (noise_i.x + noise_i.y) * K2;
        float2 noise_o = (noise_a.x > noise_a.y) ? float2(1.0, 0.0) : float2(0.0, 1.0);
        float2 noise_b = noise_a - noise_o + K2;
        float2 noise_c = noise_a - 1.0 + 2.0 * K2;

        float3 h = max(0.5 - float3(dot(noise_a, noise_a), dot(noise_b, noise_b), dot(noise_c, noise_c)), 0.0);
        
        // Hash 로직 인라인
        float2 hash_a = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + 0.0, float2(127.1, 311.7)), dot(noise_i + 0.0, float2(269.5, 183.3)))) * 43758.5453123);
        float2 hash_b = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + noise_o, float2(127.1, 311.7)), dot(noise_i + noise_o, float2(269.5, 183.3)))) * 43758.5453123);
        float2 hash_c = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + 1.0, float2(127.1, 311.7)), dot(noise_i + 1.0, float2(269.5, 183.3)))) * 43758.5453123);

        float3 n = h * h * h * h * float3(dot(noise_a, hash_a), dot(noise_b, hash_b), dot(noise_c, hash_c));
        float noise_val = dot(n, float3(70.0, 70.0, 70.0));
        
        value += amplitude * noise_val;
        fbm_p *= Lacunarity;
        amplitude *= Gain;
    }
    q.y = value;
}

// --- FBM #3 : 최종 결과물 계산 ---
{
    float2 r = p + WarpStrength * q;
    float2 fbm_p = r;
    float value = 0.0;
    float amplitude = 0.5;

    for (int i = 0; i < Octaves; i++)
    {
        // Noise 로직 인라인
        float2 noise_i = floor(fbm_p + (fbm_p.x + fbm_p.y) * K1);
        float2 noise_a = fbm_p - noise_i + (noise_i.x + noise_i.y) * K2;
        float2 noise_o = (noise_a.x > noise_a.y) ? float2(1.0, 0.0) : float2(0.0, 1.0);
        float2 noise_b = noise_a - noise_o + K2;
        float2 noise_c = noise_a - 1.0 + 2.0 * K2;

        float3 h = max(0.5 - float3(dot(noise_a, noise_a), dot(noise_b, noise_b), dot(noise_c, noise_c)), 0.0);
        
        // Hash 로직 인라인
        float2 hash_a = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + 0.0, float2(127.1, 311.7)), dot(noise_i + 0.0, float2(269.5, 183.3)))) * 43758.5453123);
        float2 hash_b = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + noise_o, float2(127.1, 311.7)), dot(noise_i + noise_o, float2(269.5, 183.3)))) * 43758.5453123);
        float2 hash_c = -1.0 + 2.0 * frac(sin(float2(dot(noise_i + 1.0, float2(127.1, 311.7)), dot(noise_i + 1.0, float2(269.5, 183.3)))) * 43758.5453123);

        float3 n = h * h * h * h * float3(dot(noise_a, hash_a), dot(noise_b, hash_b), dot(noise_c, hash_c));
        float noise_val = dot(n, float3(70.0, 70.0, 70.0));
        
        value += amplitude * noise_val;
        fbm_p *= Lacunarity;
        amplitude *= Gain;
    }
    result = value;
}

// 최종 결과물을 0과 1 사이로 정규화
return (result + 1.0) * 0.5;