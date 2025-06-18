// 1. 빛 방향과 표면 법선의 내적 계산
//   내적(Dot Product)은 두 벡터가 얼마나 같은 방향을 향하는지 나타냅니다. (결과: -1 ~ 1)
//   saturate()는 값을 0과 1 사이로 제한합니다.
float NdotL = saturate(dot(normal_in, lightDir_in));

// 2. 임계값을 기준으로 색상 결정
//   step(edge, x) 함수는 x가 edge보다 크거나 같으면 1, 아니면 0을 반환합니다.
//   이를 이용해 NdotL 값에 따라 그림자/중간톤/하이라이트 영역을 구분합니다.

// 그림자 영역 체크 (NdotL < shadowStep_in 이면 1, 아니면 0)
float shadowFactor = step(NdotL, shadowStep_in);

// 하이라이트 영역 체크 (NdotL >= highlightStep_in 이면 1, 아니면 0)
// step 함수의 결과를 반대로 생각하거나, 아래처럼 계산할 수도 있습니다.
float highlightFactor = step(highlightStep_in, NdotL);

// 중간톤 영역 계산 (그림자도 아니고 하이라이트도 아닌 영역)
// (1 - shadowFactor)는 그림자가 아닌 영역(1)
// (1 - highlightFactor)는 하이라이트가 아닌 영역(1)
// 둘 다 1인 경우, 즉 중간톤 영역에서만 1이 됩니다. (약간 복잡하게 느껴질 수 있습니다)
// 더 쉬운 방법: if 문 사용 (아래 주석 참고)
float midFactor = (1 - shadowFactor) * (1 - highlightFactor);

// 3. 최종 색상 계산
// 각 영역에 해당하는 Tint 색상을 곱하고 더합니다.
float3 finalColor = (shadowFactor * shadowTint_in) + (midFactor * midTint_in) + (highlightFactor * highlightTint_in);

// 4. 기본 색상과 곱하기 (선택 사항: Tint가 이미 색을 포함하면 생략 가능)
// finalColor *= baseColor_in; // 주석 해제하여 기본 색상과 혼합

return finalColor;


/* // if 문을 사용한 더 직관적인 방법 (위 step 함수 로직 대신 사용 가능)
float3 finalColor;
if (NdotL < shadowStep_in)
{
    finalColor = shadowTint_in;
}
else if (NdotL >= highlightStep_in)
{
    finalColor = highlightTint_in;
}
else
{
    finalColor = midTint_in;
}
// finalColor *= baseColor_in; // 기본 색상과 혼합
return finalColor;
*/