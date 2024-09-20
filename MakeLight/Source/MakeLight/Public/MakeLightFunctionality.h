#pragma once

#include "CoreMinimal.h"
#include "EngineUtils.h"
#include "Modules/ModuleManager.h"
#include "MovieSceneObjectBindingID.h"
#include "MakeLightTypes.h"

DECLARE_LOG_CATEGORY_EXTERN(LogMakeLightFunctionality, Log, All);

class ULevelSequence;
class AActor;
class ALight;
class ASkeletalMeshActor;
class UMovieScene;

class FMakeLightFunctionality : public IModuleInterface, public TSharedFromThis<FMakeLightFunctionality>
{
public:
    FReply OnAttachButtonClicked(ELightType LightType, ELightPurpose LightPurpose, EAttachBone AttachBone, const FString& CustomBoneName);
    FReply OnAttachExistingLightButtonClicked(EAttachBone AttachBone, const FString& CustomBoneName);

private:
    ALight* CreateLight(ELightType LightType, ELightPurpose LightPurpose, EAttachBone AttachBone);
    FString GetLightTypeString(ELightType LightType);
    FString GetLightPurposeString(ELightPurpose LightPurpose);
    void GetLightPositionAndRotation(ELightPurpose LightPurpose, EAttachBone AttachBone, FVector& OutLocation, FRotator& OutRotation);
    void CreateLightAndAttachToSelectedActor(ELightType LightType, ELightPurpose LightPurpose, EAttachBone AttachBone, const FString& CustomBoneName);
    bool AttachLightToSkeletalMesh(ALight* Light, ASkeletalMeshActor* SkeletalMeshActor, EAttachBone AttachBone, const FString& CustomBoneName);
    FString GenerateUniqueLightName(const FString& BaseName);

    template<class T>
    T* GetSelectedActorOfClass();
    
    FGuid GetActorGuid(UMovieScene* MovieScene, AActor* Actor);
    FName GetBoneNameFromEnum(EAttachBone AttachBone, const FString& CustomBoneName);
};
