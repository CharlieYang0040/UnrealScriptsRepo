#include "MakeLightFunctionality.h"
#include "LevelEditor.h"
#include "Modules/ModuleManager.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "LevelSequence.h"
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "LevelSequenceEditorSubsystem.h"
#include "MovieScene.h"
#include "MovieSceneSpawnable.h"
#include "Components/SpotLightComponent.h"
#include "Engine/SpotLight.h"
#include "Engine/Selection.h"
#include "Animation/SkeletalMeshActor.h"
#include "Tracks/MovieScene3DAttachTrack.h"
#include "Sections/MovieScene3DAttachSection.h"
#include "Components/SkeletalMeshComponent.h"
#include "MovieSceneObjectBindingID.h"
#include "Engine/PointLight.h"
#include "Engine/RectLight.h"
#include "Kismet/KismetMathLibrary.h"

#define LOCTEXT_NAMESPACE "FMakeLightFunctionality"

DEFINE_LOG_CATEGORY(LogMakeLightFunctionality);

FReply FMakeLightFunctionality::OnAttachButtonClicked(ELightType LightType, ELightPurpose LightPurpose, EAttachBone AttachBone, const FString& CustomBoneName)
{
    if (LightPurpose == ELightPurpose::ThreePoint)
    {
        TArray<ELightPurpose> Purposes = { ELightPurpose::Key, ELightPurpose::Fill, ELightPurpose::LeftRim, ELightPurpose::RightRim };
        for (const auto& Purpose : Purposes)
        {
            CreateLightAndAttachToSelectedActor(LightType, Purpose, AttachBone, CustomBoneName);
        }
    }
    else
    {
        CreateLightAndAttachToSelectedActor(LightType, LightPurpose, AttachBone, CustomBoneName);
    }
    
    return FReply::Handled();
}

FReply FMakeLightFunctionality::OnAttachExistingLightButtonClicked(EAttachBone AttachBone, const FString& CustomBoneName)
{
    ALight* SelectedLight = Cast<ALight>(GetSelectedActorOfClass<ALight>());
    ASkeletalMeshActor* SkeletalMeshActor = Cast<ASkeletalMeshActor>(GetSelectedActorOfClass<ASkeletalMeshActor>());

    if (!SelectedLight || !SkeletalMeshActor)
    {
        UE_LOG(LogMakeLightFunctionality, Error, TEXT("조명 또는 스켈레탈 메시 액터가 선택되지 않았습니다."));
        return FReply::Handled();
    }

    if (AttachLightToSkeletalMesh(SelectedLight, SkeletalMeshActor, AttachBone, CustomBoneName))
    {
        ULevelSequenceEditorBlueprintLibrary::RefreshCurrentLevelSequence();
    }

    return FReply::Handled();
}

ALight* FMakeLightFunctionality::CreateLight(ELightType LightType, ELightPurpose LightPurpose, EAttachBone AttachBone)
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World) return nullptr;

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    FVector Location;
    FRotator Rotation;
    GetLightPositionAndRotation(LightPurpose, AttachBone, Location, Rotation);

    ALight* Light = nullptr;
    switch (LightType)
    {
    case ELightType::Spot:
        // 스팟라이트일때 회전값을 초기화
        Light = World->SpawnActor<ASpotLight>(ASpotLight::StaticClass(), Location, FRotator::ZeroRotator, SpawnParams);
        if (Light)
        {
            Light->SetActorRotation(Rotation);
        }
        break;
    case ELightType::Rect:
        Light = World->SpawnActor<ARectLight>(ARectLight::StaticClass(), Location, Rotation, SpawnParams);
        break;
    case ELightType::Point:
        Light = World->SpawnActor<APointLight>(APointLight::StaticClass(), Location, Rotation, SpawnParams);
        break;
    }

    if (Light)
    {
        // 라이트 이름 변경
        FString BaseLightName = FString::Printf(TEXT("%s_%s"),
            *GetLightTypeString(LightType),
            *GetLightPurposeString(LightPurpose));
        FString NewLightName = GenerateUniqueLightName(BaseLightName);
        Light->SetActorLabel(*NewLightName);
        UE_LOG(LogMakeLightFunctionality, Log, TEXT("라이트 이름이 %s로 변경되었습니다."), *NewLightName);
    }

    if (Light)
    {
        UE_LOG(LogMakeLightFunctionality, Log, TEXT("라이트 생성: %s 위치: %s 회전: %s"), *Light->GetName(), *Light->GetActorLocation().ToString(), *Light->GetActorRotation().ToString());
    }
    else
    {
        UE_LOG(LogMakeLightFunctionality, Error, TEXT("라이트 생성에 실패했습니다."));
    }
    return Light;
}

FString FMakeLightFunctionality::GetLightTypeString(ELightType LightType)
{
    switch (LightType)
    {
    case ELightType::Spot:
        return TEXT("Spot");
    case ELightType::Rect:
        return TEXT("Rect");
    case ELightType::Point:
        return TEXT("Point");
    default:
        return TEXT("Unknown");
    }
}

FString FMakeLightFunctionality::GetLightPurposeString(ELightPurpose LightPurpose)
{
    switch (LightPurpose)
    {
    case ELightPurpose::None:
        return TEXT("None");
    case ELightPurpose::Key:
        return TEXT("Key");
    case ELightPurpose::Fill:
        return TEXT("Fill");
    case ELightPurpose::LeftRim:
        return TEXT("LeftRim");
    case ELightPurpose::RightRim:
        return TEXT("RightRim");
    case ELightPurpose::ThreePoint:
        return TEXT("ThreePoint");
    default:
        return TEXT("Unknown");
    }
}

void FMakeLightFunctionality::GetLightPositionAndRotation(ELightPurpose LightPurpose, EAttachBone AttachBone, FVector& OutLocation, FRotator& OutRotation)
{
    if (LightPurpose == ELightPurpose::None)
    {
        OutLocation = FVector::ZeroVector;
        OutRotation = FRotator::ZeroRotator;
        return;
    }
    switch (AttachBone)
    {
    case EAttachBone::Head:
        switch (LightPurpose)
        {
        case ELightPurpose::Key: // 캐릭터 시점 기준 왼쪽 정면
            OutLocation = FVector(30, 345, -330);
            OutRotation = UKismetMathLibrary::MakeRotator(88, 40, -95);
            break;
        case ELightPurpose::Fill: // 캐릭터 시점 기준 오른쪽 정면
            OutLocation = FVector(5, 435, 410);
            OutRotation = UKismetMathLibrary::MakeRotator(-265, -40, 268);
            break;
        case ELightPurpose::LeftRim: // 캐릭터 시점 기준 왼쪽 뒤
            OutLocation = FVector(140, -380, -270);
            OutRotation = UKismetMathLibrary::MakeRotator(-75, 35, -238);
            break;
        case ELightPurpose::RightRim: // 캐릭터 시점 기준 오른쪽 뒤
            OutLocation = FVector(140, -380, 180);
            OutRotation = UKismetMathLibrary::MakeRotator(80, -15, 115);
            break;
        }
        break;

    case EAttachBone::Spine:
        switch (LightPurpose)
        {
        case ELightPurpose::Key: // 캐릭터 시점 기준 왼쪽 정면
            OutLocation = FVector(-11, 387, -231);
            OutRotation = UKismetMathLibrary::MakeRotator(82, 30, -85);
            break;
        case ELightPurpose::Fill: // 캐릭터 시점 기준 오른쪽 정면
            OutLocation = FVector(55, 386, 335);
            OutRotation = UKismetMathLibrary::MakeRotator(106, -35, -96);
            break;
        case ELightPurpose::LeftRim: // 캐릭터 시점 기준 오른쪽 뒤
            OutLocation = FVector(232, -332, -290);
            OutRotation = UKismetMathLibrary::MakeRotator(-84, 32, -233);
            break;
        case ELightPurpose::RightRim: // 캐릭터 시점 기준 오른쪽 뒤
            OutLocation = FVector(205, -336, 143);
            OutRotation = UKismetMathLibrary::MakeRotator(270, -20, 105);
            break;
        }
        break;

    case EAttachBone::None:
    default:
        switch (LightPurpose)
        {
        case ELightPurpose::Key: // 캐릭터 시점 기준 왼쪽 정면
            OutLocation = FVector(352, 313, 216);
            OutRotation = UKismetMathLibrary::MakeRotator(0, -13, -140);
            break;
        case ELightPurpose::Fill: // 캐릭터 시점 기준 오른쪽 정면
            OutLocation = FVector(-427, 433, 200);
            OutRotation = UKismetMathLibrary::MakeRotator(-3, 0, -47);
            break;
        case ELightPurpose::LeftRim: // 캐릭터 시점 기준 오른쪽 뒤
            OutLocation = FVector(272, -350, 358);
            OutRotation = UKismetMathLibrary::MakeRotator(2, -16, 120);
            break;
        case ELightPurpose::RightRim: // 캐릭터 시점 기준 오른쪽 뒤
            OutLocation = FVector(-128, -350, 358);
            OutRotation = UKismetMathLibrary::MakeRotator(2, -16, 67);
            break;
        }
        break;
    }
}

bool FMakeLightFunctionality::AttachLightToSkeletalMesh(ALight* Light, ASkeletalMeshActor* SkeletalMeshActor, EAttachBone AttachBone, const FString& CustomBoneName)
{
    if (!Light || !SkeletalMeshActor) return false;

    ULevelSequence* FocusedSequence = ULevelSequenceEditorBlueprintLibrary::GetFocusedLevelSequence();
    if (!FocusedSequence) return false;

    UMovieScene* MovieScene = FocusedSequence->GetMovieScene();
    if (!MovieScene) return false;

    FGuid LightGuid = GetActorGuid(MovieScene, Light);
    FGuid SkeletalMeshActorGuid = GetActorGuid(MovieScene, SkeletalMeshActor);

    if (!LightGuid.IsValid() || !SkeletalMeshActorGuid.IsValid()) return false;

    UMovieScene3DAttachTrack* AttachTrack = MovieScene->AddTrack<UMovieScene3DAttachTrack>(LightGuid);
    if (!AttachTrack) return false;

    FName BoneName = GetBoneNameFromEnum(AttachBone, CustomBoneName);
    UE::MovieScene::FRelativeObjectBindingID RelativeBindingID(SkeletalMeshActorGuid, MovieSceneSequenceID::Root);
    FMovieSceneObjectBindingID SkeletalMeshActorBindingID(RelativeBindingID);

    AttachTrack->AddConstraint(
        MovieScene->GetPlaybackRange().GetLowerBoundValue(),
        MovieScene->GetPlaybackRange().GetUpperBoundValue().Value - MovieScene->GetPlaybackRange().GetLowerBoundValue().Value,
        BoneName,
        (AttachBone == EAttachBone::None) ? NAME_None : SkeletalMeshActor->GetSkeletalMeshComponent()->GetFName(),
        SkeletalMeshActorBindingID
    );

    return true;
}

void FMakeLightFunctionality::CreateLightAndAttachToSelectedActor(ELightType LightType, ELightPurpose LightPurpose, EAttachBone AttachBone, const FString& CustomBoneName)
{
    // 먼저 선택된 스켈레탈 메시 액터가 있는지 확인합니다.
    ASkeletalMeshActor* SkeletalMeshActor = Cast<ASkeletalMeshActor>(GetSelectedActorOfClass<ASkeletalMeshActor>());
    if (!SkeletalMeshActor)
    {
        UE_LOG(LogMakeLightFunctionality, Warning, TEXT("선택된 스켈레탈 메시 액터가 없습니다. 라이트만 생성합니다."));
    }

    ALight* Light = CreateLight(LightType, LightPurpose, AttachBone);
    if (!Light)
    {
        UE_LOG(LogMakeLightFunctionality, Error, TEXT("라이트 생성에 실패했습니다."));
        return;
    }

    FPlatformProcess::Sleep(0.1f);

    ULevelSequenceEditorSubsystem* LevelSequenceEditorSubsystem = GEditor->GetEditorSubsystem<ULevelSequenceEditorSubsystem>();
    if (!LevelSequenceEditorSubsystem) return;

    TArray<AActor*> ActorsToAdd = { Light };
    TArray<FMovieSceneBindingProxy> BindingProxies = LevelSequenceEditorSubsystem->AddActors(ActorsToAdd);
    if (BindingProxies.Num() == 0) return;
    TArray<FMovieSceneBindingProxy> SpawnableProxies = LevelSequenceEditorSubsystem->ConvertToSpawnable(BindingProxies[0]);
    if (SpawnableProxies.Num() == 0) return;

    // 스켈레탈 메시 액터가 있을 때만 부착을 시도합니다.
    if (SkeletalMeshActor)
    {
        if (AttachLightToSkeletalMesh(Light, SkeletalMeshActor, AttachBone, CustomBoneName))
        {
            UE_LOG(LogMakeLightFunctionality, Log, TEXT("라이트를 스켈레탈 메시에 성공적으로 부착했습니다."));
            ULevelSequenceEditorBlueprintLibrary::RefreshCurrentLevelSequence();
        }
        else
        {
            UE_LOG(LogMakeLightFunctionality, Warning, TEXT("라이트를 스켈레탈 메시에 부착하는데 실패했습니다."));
        }
    }
    else
    {
        UE_LOG(LogMakeLightFunctionality, Log, TEXT("라이트가 생성되었지만 부착할 스켈레탈 메시가 없습니다."));
    }
}

template<class T>
T* FMakeLightFunctionality::GetSelectedActorOfClass()
{
    USelection* SelectedActors = GEditor->GetSelectedActors();
    for (FSelectionIterator Iter(*SelectedActors); Iter; ++Iter)
    {
        if (T* Actor = Cast<T>(*Iter))
        {
            return Actor;
        }
    }
    return nullptr;
}

FGuid FMakeLightFunctionality::GetActorGuid(UMovieScene* MovieScene, AActor* Actor)
{
    for (const FMovieSceneBinding& Binding : MovieScene->GetBindings())
    {
        if (Binding.GetName() == Actor->GetActorLabel())
        {
            return Binding.GetObjectGuid();
        }
    }
    return FGuid();
}

FName FMakeLightFunctionality::GetBoneNameFromEnum(EAttachBone AttachBone, const FString& CustomBoneName)
{
    switch (AttachBone)
    {
    case EAttachBone::Head: return FName("Bip001-Head");
    case EAttachBone::Spine: return FName("Bip001-Spine2");
    case EAttachBone::Custom: return FName(*CustomBoneName);
    default: return NAME_None;
    }
}

FString FMakeLightFunctionality::GenerateUniqueLightName(const FString& BaseName)
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World) return BaseName + TEXT("_00");

    int32 Counter = 0;
    FString NewName;
    bool bNameExists;

    do
    {
        NewName = FString::Printf(TEXT("%s_%02d"), *BaseName, Counter);
        bNameExists = false;

        for (TActorIterator<ALight> It(World); It; ++It)
        {
            if (It->GetActorLabel() == NewName)
            {
                bNameExists = true;
                break;
            }
        }

        Counter++;
    } while (bNameExists);

    return NewName;
}

#undef LOCTEXT_NAMESPACE
