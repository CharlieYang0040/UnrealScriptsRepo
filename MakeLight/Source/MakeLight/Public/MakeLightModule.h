#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "MakeLightTypes.h"

DECLARE_LOG_CATEGORY_EXTERN(LogMakeLightModule, Log, All);

class FMakeLightModule : public IModuleInterface, public TSharedFromThis<FMakeLightModule>
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void RegisterNomadTab();
    void AddPluginMenuExtension();
    void AddMenuEntry(FMenuBuilder& MenuBuilder);
    void OpenPluginTab();
    TSharedRef<SDockTab> OnSpawnPluginTab(const FSpawnTabArgs& SpawnTabArgs);

private:
    TSharedPtr<FExtender> MenuExtender;

    FString CustomBoneName; // Custom 본 이름을 저장할 변수 추가
    static FString GetLightTypeString(ELightType LightType);
    static FString GetLightPurposeString(ELightPurpose LightPurpose);
    static FString GetAttachBoneString(EAttachBone AttachBone);

    TArray<TSharedPtr<ELightType>> LightTypeOptions;
    TArray<TSharedPtr<ELightPurpose>> LightPurposeOptions;
    TArray<TSharedPtr<EAttachBone>> AttachBoneOptions;

    ELightType SelectedLightType;
    ELightPurpose SelectedLightPurpose;
    EAttachBone SelectedAttachBone;

    void InitializeComboBoxOptions();
};
