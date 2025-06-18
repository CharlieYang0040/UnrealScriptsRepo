// 2D 벡터를 입력받아 2D 의사 난수 벡터를 반환하는 간단한 해시 함수
// (다양한 해시 함수 구현이 가능합니다)
float2 hash22(float2 p)
{
    p = float2(dot(p, float2(127.1, 311.7)),
               dot(p, float2(269.5, 183.3)));
    return -1.0 + 2.0 * frac(sin(p) * 43758.5453123);
}

// 입력 UV 스케일링
float2 uv = uv_in * scale_in;

// 현재 셀 ID (정수 부분) 와 셀 내에서의 위치 (소수 부분) 계산
float2 cellID = floor(uv);
float2 fractUV = frac(uv);

// 가장 가까운 점까지의 최소 거리를 저장할 변수 (제곱 거리로 시작)
// 초기값은 매우 큰 값으로 설정 (예: 1.0 또는 그 이상)
float minDistSq = 10.0;

// 현재 셀과 주변 8개 셀 (총 3x3 영역)을 순회
for (int y = -1; y <= 1; y++)
{
    for (int x = -1; x <= 1; x++)
    {
        // 현재 검사 중인 이웃 셀의 ID 계산
        float2 neighborCellID = cellID + float2(x, y);

        // 이웃 셀의 특징점(feature point) 위치 계산
        // 해시 함수를 사용하여 셀 ID 기반의 랜덤 오프셋 생성 (-1 ~ 1 범위)
        // jitter_in을 곱하여 무작위성 조절 (0이면 오프셋 없음, 1이면 최대 오프셋)
        float2 pointOffset = hash22(neighborCellID) * jitter_in;

        // 특징점의 최종 위치 (셀 중심(0.5,0.5) + 랜덤 오프셋)
        // (해시 함수 결과가 0~1 범위라면 + pointOffset만 해도 됩니다)
        float2 featurePoint = float2(0.5, 0.5) + pointOffset * 0.5; // -0.5 ~ 0.5 범위로 조정

        // 현재 픽셀 위치와 이웃 셀의 특징점 사이의 거리 벡터 계산
        // neighborCellID + featurePoint : 월드 기준 특징점 위치
        // uv : 월드 기준 현재 픽셀 위치
        // (float(x), float(y)) : 현재 셀에서 이웃 셀까지의 오프셋
        // fractUV : 현재 셀 내에서의 픽셀 위치
        // 아래는 거리 벡터를 계산하는 한 가지 방법입니다.
        float2 diff = float2(x, y) - fractUV + featurePoint;

        // 거리의 제곱 계산 (sqrt보다 연산 비용이 저렴)
        float distSq = dot(diff, diff);

        // 현재까지의 최소 거리 제곱보다 작으면 업데이트
        minDistSq = min(minDistSq, distSq);
    }
}

// 최종 결과: 최소 거리의 제곱근 반환 (0~1 범위에 가까움)
// 또는 minDistSq 자체를 사용해도 다른 느낌의 패턴이 됩니다.
return sqrt(minDistSq);