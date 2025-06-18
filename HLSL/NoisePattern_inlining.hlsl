// 입력 UV 스케일링
float2 uv = uv_in * scale_in;

// 현재 셀 ID (정수 부분) 와 셀 내에서의 위치 (소수 부분) 계산
float2 cellID = floor(uv);
float2 fractUV = frac(uv);

// 가장 가까운 점까지의 최소 거리를 저장할 변수 (제곱 거리로 시작)
float minDistSq = 10.0; // 충분히 큰 초기값

// 현재 셀과 주변 8개 셀 (총 3x3 영역)을 순회
for (int y = -1; y <= 1; y++)
{
    for (int x = -1; x <= 1; x++)
    {
        // 현재 검사 중인 이웃 셀의 ID 계산
        float2 neighborCellID = cellID + float2(x, y);

        // --- hash22 함수의 로직을 여기에 직접 삽입 ---
        float2 p_hash_input = neighborCellID; // 해시 함수의 입력이 될 값
        float2 hashed_value_components;
        hashed_value_components.x = dot(p_hash_input, float2(127.1, 311.7));
        hashed_value_components.y = dot(p_hash_input, float2(269.5, 183.3));
        float2 pointOffset_unscaled = -1.0 + 2.0 * frac(sin(hashed_value_components) * 43758.5453123);
        // --- 인라이닝된 hash22 로직 끝 ---

        float2 pointOffset = pointOffset_unscaled * jitter_in;

        // 특징점의 최종 위치 (셀 중심(0.5,0.5) + 랜덤 오프셋)
        float2 featurePoint = float2(0.5, 0.5) + pointOffset * 0.5; // 오프셋을 -0.5 ~ 0.5 범위로 조정

        // 현재 픽셀 위치와 이웃 셀의 특징점 사이의 거리 벡터 계산
        float2 diff = float2(x, y) - fractUV + featurePoint;

        // 거리의 제곱 계산
        float distSq = dot(diff, diff);

        // 현재까지의 최소 거리 제곱보다 작으면 업데이트
        minDistSq = min(minDistSq, distSq);
    }
}

// 최종 결과: 최소 거리의 제곱근 반환
return sqrt(minDistSq);