#pragma once

#include "CoreMinimal.h"
#include "MakeLightTypes.generated.h"

UENUM()
enum class ELightType : uint8
{
    Spot,
    Rect,
    Point
};

UENUM()
enum class ELightPurpose : uint8
{
    None,   // None 옵션 추가
    Key,
    Fill,
    LeftRim,
    RightRim,
    ThreePoint
};

UENUM()
enum class EAttachBone : uint8
{
    None,
    Head,
    Spine,
    Custom // Custom 옵션 추가
};
