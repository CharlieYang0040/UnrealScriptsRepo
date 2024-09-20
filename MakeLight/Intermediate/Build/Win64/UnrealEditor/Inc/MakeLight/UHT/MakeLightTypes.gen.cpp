// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "D:/Unreal Projects/MakeSubSeq/Plugins/MakeLight/Source/MakeLight/Public/MakeLightTypes.h"
PRAGMA_DISABLE_DEPRECATION_WARNINGS
void EmptyLinkFunctionForGeneratedCodeMakeLightTypes() {}
// Cross Module References
	MAKELIGHT_API UEnum* Z_Construct_UEnum_MakeLight_EAttachBone();
	MAKELIGHT_API UEnum* Z_Construct_UEnum_MakeLight_ELightPurpose();
	MAKELIGHT_API UEnum* Z_Construct_UEnum_MakeLight_ELightType();
	UPackage* Z_Construct_UPackage__Script_MakeLight();
// End Cross Module References
	static FEnumRegistrationInfo Z_Registration_Info_UEnum_ELightType;
	static UEnum* ELightType_StaticEnum()
	{
		if (!Z_Registration_Info_UEnum_ELightType.OuterSingleton)
		{
			Z_Registration_Info_UEnum_ELightType.OuterSingleton = GetStaticEnum(Z_Construct_UEnum_MakeLight_ELightType, (UObject*)Z_Construct_UPackage__Script_MakeLight(), TEXT("ELightType"));
		}
		return Z_Registration_Info_UEnum_ELightType.OuterSingleton;
	}
	template<> MAKELIGHT_API UEnum* StaticEnum<ELightType>()
	{
		return ELightType_StaticEnum();
	}
	struct Z_Construct_UEnum_MakeLight_ELightType_Statics
	{
		static const UECodeGen_Private::FEnumeratorParam Enumerators[];
#if WITH_METADATA
		static const UECodeGen_Private::FMetaDataPairParam Enum_MetaDataParams[];
#endif
		static const UECodeGen_Private::FEnumParams EnumParams;
	};
	const UECodeGen_Private::FEnumeratorParam Z_Construct_UEnum_MakeLight_ELightType_Statics::Enumerators[] = {
		{ "ELightType::Spot", (int64)ELightType::Spot },
		{ "ELightType::Rect", (int64)ELightType::Rect },
		{ "ELightType::Point", (int64)ELightType::Point },
	};
#if WITH_METADATA
	const UECodeGen_Private::FMetaDataPairParam Z_Construct_UEnum_MakeLight_ELightType_Statics::Enum_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/MakeLightTypes.h" },
		{ "Point.Name", "ELightType::Point" },
		{ "Rect.Name", "ELightType::Rect" },
		{ "Spot.Name", "ELightType::Spot" },
	};
#endif
	const UECodeGen_Private::FEnumParams Z_Construct_UEnum_MakeLight_ELightType_Statics::EnumParams = {
		(UObject*(*)())Z_Construct_UPackage__Script_MakeLight,
		nullptr,
		"ELightType",
		"ELightType",
		Z_Construct_UEnum_MakeLight_ELightType_Statics::Enumerators,
		RF_Public|RF_Transient|RF_MarkAsNative,
		UE_ARRAY_COUNT(Z_Construct_UEnum_MakeLight_ELightType_Statics::Enumerators),
		EEnumFlags::None,
		(uint8)UEnum::ECppForm::EnumClass,
		METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UEnum_MakeLight_ELightType_Statics::Enum_MetaDataParams), Z_Construct_UEnum_MakeLight_ELightType_Statics::Enum_MetaDataParams)
	};
	UEnum* Z_Construct_UEnum_MakeLight_ELightType()
	{
		if (!Z_Registration_Info_UEnum_ELightType.InnerSingleton)
		{
			UECodeGen_Private::ConstructUEnum(Z_Registration_Info_UEnum_ELightType.InnerSingleton, Z_Construct_UEnum_MakeLight_ELightType_Statics::EnumParams);
		}
		return Z_Registration_Info_UEnum_ELightType.InnerSingleton;
	}
	static FEnumRegistrationInfo Z_Registration_Info_UEnum_ELightPurpose;
	static UEnum* ELightPurpose_StaticEnum()
	{
		if (!Z_Registration_Info_UEnum_ELightPurpose.OuterSingleton)
		{
			Z_Registration_Info_UEnum_ELightPurpose.OuterSingleton = GetStaticEnum(Z_Construct_UEnum_MakeLight_ELightPurpose, (UObject*)Z_Construct_UPackage__Script_MakeLight(), TEXT("ELightPurpose"));
		}
		return Z_Registration_Info_UEnum_ELightPurpose.OuterSingleton;
	}
	template<> MAKELIGHT_API UEnum* StaticEnum<ELightPurpose>()
	{
		return ELightPurpose_StaticEnum();
	}
	struct Z_Construct_UEnum_MakeLight_ELightPurpose_Statics
	{
		static const UECodeGen_Private::FEnumeratorParam Enumerators[];
#if WITH_METADATA
		static const UECodeGen_Private::FMetaDataPairParam Enum_MetaDataParams[];
#endif
		static const UECodeGen_Private::FEnumParams EnumParams;
	};
	const UECodeGen_Private::FEnumeratorParam Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::Enumerators[] = {
		{ "ELightPurpose::None", (int64)ELightPurpose::None },
		{ "ELightPurpose::Key", (int64)ELightPurpose::Key },
		{ "ELightPurpose::Fill", (int64)ELightPurpose::Fill },
		{ "ELightPurpose::LeftRim", (int64)ELightPurpose::LeftRim },
		{ "ELightPurpose::RightRim", (int64)ELightPurpose::RightRim },
		{ "ELightPurpose::ThreePoint", (int64)ELightPurpose::ThreePoint },
	};
#if WITH_METADATA
	const UECodeGen_Private::FMetaDataPairParam Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::Enum_MetaDataParams[] = {
		{ "Fill.Name", "ELightPurpose::Fill" },
		{ "Key.Comment", "// None \xec\x98\xb5\xec\x85\x98 \xec\xb6\x94\xea\xb0\x80\n" },
		{ "Key.Name", "ELightPurpose::Key" },
		{ "Key.ToolTip", "None \xec\x98\xb5\xec\x85\x98 \xec\xb6\x94\xea\xb0\x80" },
		{ "LeftRim.Name", "ELightPurpose::LeftRim" },
		{ "ModuleRelativePath", "Public/MakeLightTypes.h" },
		{ "None.Name", "ELightPurpose::None" },
		{ "RightRim.Name", "ELightPurpose::RightRim" },
		{ "ThreePoint.Name", "ELightPurpose::ThreePoint" },
	};
#endif
	const UECodeGen_Private::FEnumParams Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::EnumParams = {
		(UObject*(*)())Z_Construct_UPackage__Script_MakeLight,
		nullptr,
		"ELightPurpose",
		"ELightPurpose",
		Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::Enumerators,
		RF_Public|RF_Transient|RF_MarkAsNative,
		UE_ARRAY_COUNT(Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::Enumerators),
		EEnumFlags::None,
		(uint8)UEnum::ECppForm::EnumClass,
		METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::Enum_MetaDataParams), Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::Enum_MetaDataParams)
	};
	UEnum* Z_Construct_UEnum_MakeLight_ELightPurpose()
	{
		if (!Z_Registration_Info_UEnum_ELightPurpose.InnerSingleton)
		{
			UECodeGen_Private::ConstructUEnum(Z_Registration_Info_UEnum_ELightPurpose.InnerSingleton, Z_Construct_UEnum_MakeLight_ELightPurpose_Statics::EnumParams);
		}
		return Z_Registration_Info_UEnum_ELightPurpose.InnerSingleton;
	}
	static FEnumRegistrationInfo Z_Registration_Info_UEnum_EAttachBone;
	static UEnum* EAttachBone_StaticEnum()
	{
		if (!Z_Registration_Info_UEnum_EAttachBone.OuterSingleton)
		{
			Z_Registration_Info_UEnum_EAttachBone.OuterSingleton = GetStaticEnum(Z_Construct_UEnum_MakeLight_EAttachBone, (UObject*)Z_Construct_UPackage__Script_MakeLight(), TEXT("EAttachBone"));
		}
		return Z_Registration_Info_UEnum_EAttachBone.OuterSingleton;
	}
	template<> MAKELIGHT_API UEnum* StaticEnum<EAttachBone>()
	{
		return EAttachBone_StaticEnum();
	}
	struct Z_Construct_UEnum_MakeLight_EAttachBone_Statics
	{
		static const UECodeGen_Private::FEnumeratorParam Enumerators[];
#if WITH_METADATA
		static const UECodeGen_Private::FMetaDataPairParam Enum_MetaDataParams[];
#endif
		static const UECodeGen_Private::FEnumParams EnumParams;
	};
	const UECodeGen_Private::FEnumeratorParam Z_Construct_UEnum_MakeLight_EAttachBone_Statics::Enumerators[] = {
		{ "EAttachBone::None", (int64)EAttachBone::None },
		{ "EAttachBone::Head", (int64)EAttachBone::Head },
		{ "EAttachBone::Spine", (int64)EAttachBone::Spine },
		{ "EAttachBone::Custom", (int64)EAttachBone::Custom },
	};
#if WITH_METADATA
	const UECodeGen_Private::FMetaDataPairParam Z_Construct_UEnum_MakeLight_EAttachBone_Statics::Enum_MetaDataParams[] = {
		{ "Custom.Name", "EAttachBone::Custom" },
		{ "Head.Name", "EAttachBone::Head" },
		{ "ModuleRelativePath", "Public/MakeLightTypes.h" },
		{ "None.Name", "EAttachBone::None" },
		{ "Spine.Name", "EAttachBone::Spine" },
	};
#endif
	const UECodeGen_Private::FEnumParams Z_Construct_UEnum_MakeLight_EAttachBone_Statics::EnumParams = {
		(UObject*(*)())Z_Construct_UPackage__Script_MakeLight,
		nullptr,
		"EAttachBone",
		"EAttachBone",
		Z_Construct_UEnum_MakeLight_EAttachBone_Statics::Enumerators,
		RF_Public|RF_Transient|RF_MarkAsNative,
		UE_ARRAY_COUNT(Z_Construct_UEnum_MakeLight_EAttachBone_Statics::Enumerators),
		EEnumFlags::None,
		(uint8)UEnum::ECppForm::EnumClass,
		METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UEnum_MakeLight_EAttachBone_Statics::Enum_MetaDataParams), Z_Construct_UEnum_MakeLight_EAttachBone_Statics::Enum_MetaDataParams)
	};
	UEnum* Z_Construct_UEnum_MakeLight_EAttachBone()
	{
		if (!Z_Registration_Info_UEnum_EAttachBone.InnerSingleton)
		{
			UECodeGen_Private::ConstructUEnum(Z_Registration_Info_UEnum_EAttachBone.InnerSingleton, Z_Construct_UEnum_MakeLight_EAttachBone_Statics::EnumParams);
		}
		return Z_Registration_Info_UEnum_EAttachBone.InnerSingleton;
	}
	struct Z_CompiledInDeferFile_FID_MakeSubSeq_Plugins_MakeLight_Source_MakeLight_Public_MakeLightTypes_h_Statics
	{
		static const FEnumRegisterCompiledInInfo EnumInfo[];
	};
	const FEnumRegisterCompiledInInfo Z_CompiledInDeferFile_FID_MakeSubSeq_Plugins_MakeLight_Source_MakeLight_Public_MakeLightTypes_h_Statics::EnumInfo[] = {
		{ ELightType_StaticEnum, TEXT("ELightType"), &Z_Registration_Info_UEnum_ELightType, CONSTRUCT_RELOAD_VERSION_INFO(FEnumReloadVersionInfo, 3932331494U) },
		{ ELightPurpose_StaticEnum, TEXT("ELightPurpose"), &Z_Registration_Info_UEnum_ELightPurpose, CONSTRUCT_RELOAD_VERSION_INFO(FEnumReloadVersionInfo, 646589104U) },
		{ EAttachBone_StaticEnum, TEXT("EAttachBone"), &Z_Registration_Info_UEnum_EAttachBone, CONSTRUCT_RELOAD_VERSION_INFO(FEnumReloadVersionInfo, 1666139439U) },
	};
	static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_MakeSubSeq_Plugins_MakeLight_Source_MakeLight_Public_MakeLightTypes_h_2675394554(TEXT("/Script/MakeLight"),
		nullptr, 0,
		nullptr, 0,
		Z_CompiledInDeferFile_FID_MakeSubSeq_Plugins_MakeLight_Source_MakeLight_Public_MakeLightTypes_h_Statics::EnumInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_MakeSubSeq_Plugins_MakeLight_Source_MakeLight_Public_MakeLightTypes_h_Statics::EnumInfo));
PRAGMA_ENABLE_DEPRECATION_WARNINGS
