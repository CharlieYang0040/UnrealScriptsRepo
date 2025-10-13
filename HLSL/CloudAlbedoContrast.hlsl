return lerp(
    max(Color, 0.0),
    ( max(Color,0.0) *
      (
        // ratio = Lc / L
        (
          // Lc = 로그 대비 + 롤오프 적용된 새로운 휘도
          ( (RollOff > 0.0)
            ? ( 
                // L_new
                exp2( (log2(max(dot(max(Color,0.0), float3(0.2126,0.7152,0.0722)), 1e-6)) - log2(max(Pivot,1e-6))) * Contrast + log2(max(Pivot,1e-6)) )
                / ( 1.0 + RollOff * exp2( (log2(max(dot(max(Color,0.0), float3(0.2126,0.7152,0.0722)), 1e-6)) - log2(max(Pivot,1e-6))) * Contrast + log2(max(Pivot,1e-6)) ) )
              )
            : (
                exp2( (log2(max(dot(max(Color,0.0), float3(0.2126,0.7152,0.0722)), 1e-6)) - log2(max(Pivot,1e-6))) * Contrast + log2(max(Pivot,1e-6)) )
              )
          )
        ) / max(dot(max(Color,0.0), float3(0.2126,0.7152,0.0722)), 1e-6)
      )
    ),
    saturate(
        (
          // 하이라이트 포커스 마스크 m
          ( (HighlightFocus > 0.0)
              ? lerp( 1.0,
                      saturate( (dot(max(Color,0.0), float3(0.2126,0.7152,0.0722)) - T) / max(Softness,1e-6) ),
                      saturate(HighlightFocus) )
              : 1.0
            )
        ) * saturate(Strength)
    )
);
