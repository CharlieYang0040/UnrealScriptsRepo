// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

// IWYU pragma: private, include "MakeLightTypes.h"
#include "Templates/IsUEnumClass.h"
#include "UObject/ObjectMacros.h"
#include "UObject/ReflectedTypeAccessors.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS
#ifdef MAKELIGHT_MakeLightTypes_generated_h
#error "MakeLightTypes.generated.h already included, missing '#pragma once' in MakeLightTypes.h"
#endif
#define MAKELIGHT_MakeLightTypes_generated_h

#undef CURRENT_FILE_ID
#define CURRENT_FILE_ID FID_MakeSubSeq_Plugins_MakeLight_Source_MakeLight_Public_MakeLightTypes_h


#define FOREACH_ENUM_ELIGHTTYPE(op) \
	op(ELightType::Spot) \
	op(ELightType::Rect) \
	op(ELightType::Point) 

enum class ELightType : uint8;
template<> struct TIsUEnumClass<ELightType> { enum { Value = true }; };
template<> MAKELIGHT_API UEnum* StaticEnum<ELightType>();

#define FOREACH_ENUM_ELIGHTPURPOSE(op) \
	op(ELightPurpose::None) \
	op(ELightPurpose::Key) \
	op(ELightPurpose::Fill) \
	op(ELightPurpose::LeftRim) \
	op(ELightPurpose::RightRim) \
	op(ELightPurpose::ThreePoint) 

enum class ELightPurpose : uint8;
template<> struct TIsUEnumClass<ELightPurpose> { enum { Value = true }; };
template<> MAKELIGHT_API UEnum* StaticEnum<ELightPurpose>();

#define FOREACH_ENUM_EATTACHBONE(op) \
	op(EAttachBone::None) \
	op(EAttachBone::Head) \
	op(EAttachBone::Spine) \
	op(EAttachBone::Custom) 

enum class EAttachBone : uint8;
template<> struct TIsUEnumClass<EAttachBone> { enum { Value = true }; };
template<> MAKELIGHT_API UEnum* StaticEnum<EAttachBone>();

PRAGMA_ENABLE_DEPRECATION_WARNINGS
