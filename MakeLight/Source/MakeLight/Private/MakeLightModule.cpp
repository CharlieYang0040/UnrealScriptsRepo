#include "MakeLightModule.h"
#include "MakeLightFunctionality.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Input/SButton.h"
#include "LevelEditor.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FMakeLightModule, MakeLight)

#define LOCTEXT_NAMESPACE "FMakeLightModule"

DEFINE_LOG_CATEGORY(LogMakeLightModule);

void FMakeLightModule::StartupModule()
{
    UE_LOG(LogMakeLightModule, Log, TEXT("MakeLight 모듈이 시작되었습니다."));

    RegisterNomadTab();
    AddPluginMenuExtension();
    InitializeComboBoxOptions();
}

void FMakeLightModule::ShutdownModule()
{
    UE_LOG(LogMakeLightModule, Log, TEXT("MakeLight 모듈이 종료됩니다."));

    if (FSlateApplication::IsInitialized())
    {
        FGlobalTabmanager::Get()->UnregisterNomadTabSpawner("MakeLightTab");
    }
}

void FMakeLightModule::RegisterNomadTab()
{
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MakeLightTab", FOnSpawnTab::CreateRaw(this, &FMakeLightModule::OnSpawnPluginTab))
        .SetDisplayName(LOCTEXT("MakeLightTabTitle", "MakeLight"))
        .SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FMakeLightModule::AddPluginMenuExtension()
{
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");

    MenuExtender = MakeShareable(new FExtender);
    MenuExtender->AddMenuExtension("WindowLayout", EExtensionHook::After, nullptr, FMenuExtensionDelegate::CreateRaw(this, &FMakeLightModule::AddMenuEntry));

    LevelEditorModule.GetMenuExtensibilityManager()->AddExtender(MenuExtender);
}

void FMakeLightModule::InitializeComboBoxOptions()
{
    LightTypeOptions.Add(MakeShareable(new ELightType(ELightType::Spot)));
    LightTypeOptions.Add(MakeShareable(new ELightType(ELightType::Rect)));
    LightTypeOptions.Add(MakeShareable(new ELightType(ELightType::Point)));

    LightPurposeOptions.Add(MakeShareable(new ELightPurpose(ELightPurpose::None))); // None 옵션 추가
    LightPurposeOptions.Add(MakeShareable(new ELightPurpose(ELightPurpose::Key)));
    LightPurposeOptions.Add(MakeShareable(new ELightPurpose(ELightPurpose::Fill)));
    LightPurposeOptions.Add(MakeShareable(new ELightPurpose(ELightPurpose::LeftRim)));
    LightPurposeOptions.Add(MakeShareable(new ELightPurpose(ELightPurpose::RightRim)));
    LightPurposeOptions.Add(MakeShareable(new ELightPurpose(ELightPurpose::ThreePoint)));

    AttachBoneOptions.Add(MakeShareable(new EAttachBone(EAttachBone::None)));
    AttachBoneOptions.Add(MakeShareable(new EAttachBone(EAttachBone::Head)));
    AttachBoneOptions.Add(MakeShareable(new EAttachBone(EAttachBone::Spine)));
    AttachBoneOptions.Add(MakeShareable(new EAttachBone(EAttachBone::Custom))); // Custom 옵션 추가

    SelectedLightType = ELightType::Spot;
    SelectedLightPurpose = ELightPurpose::None;
    SelectedAttachBone = EAttachBone::None;
    CustomBoneName = FString(); // Custom 본 이름을 저장할 변수 추가
}

void FMakeLightModule::AddMenuEntry(FMenuBuilder& MenuBuilder)
{
    MenuBuilder.AddMenuEntry(
        LOCTEXT("MakeLightMenuEntry", "MakeLight 플러그인 열기"),
        LOCTEXT("MakeLightMenuEntryTooltip", "MakeLight 플러그인을 엽니다."),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateRaw(this, &FMakeLightModule::OpenPluginTab))
    );
}

void FMakeLightModule::OpenPluginTab()
{
    FGlobalTabmanager::Get()->TryInvokeTab(FName("MakeLightTab"));
}

TSharedRef<SDockTab> FMakeLightModule::OnSpawnPluginTab(const FSpawnTabArgs& SpawnTabArgs)
{
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot()
                .AutoWidth()
                [
                    SNew(STextBlock)
                    .Text(LOCTEXT("LightTypeLabel", "조명 종류:"))
                ]
                + SHorizontalBox::Slot()
                .AutoWidth()
                [
                    SNew(SComboBox<TSharedPtr<ELightType>>)
                    .OptionsSource(&LightTypeOptions)
                    .OnSelectionChanged_Lambda([this](TSharedPtr<ELightType> NewValue, ESelectInfo::Type) {
                        if (NewValue.IsValid())
                        {
                            SelectedLightType = *NewValue;
                        }
                    })
                    .OnGenerateWidget_Lambda([](TSharedPtr<ELightType> Item) {
                        return SNew(STextBlock).Text(FText::FromString(GetLightTypeString(*Item)));
                    })
                    .InitiallySelectedItem(LightTypeOptions[0])
                    [
                        SNew(STextBlock)
                        .Text_Lambda([this]() {
                            return FText::FromString(GetLightTypeString(SelectedLightType));
                        })
                    ]
                ]
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot()
                .AutoWidth()
                [
                    SNew(STextBlock)
                    .Text(LOCTEXT("LightPurposeLabel", "조명 용도:"))
                ]
                + SHorizontalBox::Slot()
                .AutoWidth()
                [
                    SNew(SComboBox<TSharedPtr<ELightPurpose>>)
                    .OptionsSource(&LightPurposeOptions)
                    .OnSelectionChanged_Lambda([this](TSharedPtr<ELightPurpose> NewValue, ESelectInfo::Type) {
                        if (NewValue.IsValid())
                        {
                            SelectedLightPurpose = *NewValue;
                        }
                    })
                    .OnGenerateWidget_Lambda([](TSharedPtr<ELightPurpose> Item) {
                        return SNew(STextBlock).Text(FText::FromString(GetLightPurposeString(*Item)));
                    })
                    .InitiallySelectedItem(LightPurposeOptions[0])
                    [
                        SNew(STextBlock)
                        .Text_Lambda([this]() {
                            return FText::FromString(GetLightPurposeString(SelectedLightPurpose));
                        })
                    ]
                ]
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot()
                .AutoWidth()
                [
                    SNew(STextBlock)
                    .Text(LOCTEXT("AttachBoneLabel", "부착할 본:"))
                ]
                + SHorizontalBox::Slot()
                .AutoWidth()
                [
                    SNew(SComboBox<TSharedPtr<EAttachBone>>)
                    .OptionsSource(&AttachBoneOptions)
                    .OnSelectionChanged_Lambda([this](TSharedPtr<EAttachBone> NewValue, ESelectInfo::Type) {
                        if (NewValue.IsValid())
                        {
                            SelectedAttachBone = *NewValue;
                        }
                    })
                    .OnGenerateWidget_Lambda([](TSharedPtr<EAttachBone> Item) {
                        return SNew(STextBlock).Text(FText::FromString(GetAttachBoneString(*Item)));
                    })
                    .InitiallySelectedItem(AttachBoneOptions[0])
                    [
                        SNew(STextBlock)
                        .Text_Lambda([this]() {
                            return FText::FromString(GetAttachBoneString(SelectedAttachBone));
                        })
                    ]
                ]
                + SHorizontalBox::Slot()
                .AutoWidth()
                .Padding(5, 0, 0, 0)
                [
                    SNew(SEditableTextBox)
                    .IsEnabled_Lambda([this]() { return SelectedAttachBone == EAttachBone::Custom; })
                    .HintText(LOCTEXT("CustomBoneHint", "Custom 본 이름 입력"))
                    .OnTextCommitted_Lambda([this](const FText& NewText, ETextCommit::Type CommitType) {
                        CustomBoneName = NewText.ToString();
                    })
                ]
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(SButton)
                .Text(LOCTEXT("CreateAndAttachButtonText", "조명 생성 및 부착"))
                .OnClicked_Lambda([this]() -> FReply {
                    UE_LOG(LogMakeLightModule, Warning, TEXT("조명 생성 및 부착 버튼이 클릭되었습니다."));
                    FMakeLightFunctionality MakeLightFunctionality;
                    return MakeLightFunctionality.OnAttachButtonClicked(SelectedLightType, SelectedLightPurpose, SelectedAttachBone, CustomBoneName);
                })
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(10)
            [
                SNew(SButton)
                .Text(LOCTEXT("AttachExistingLightButtonText", "기존 조명 부착"))
                .OnClicked_Lambda([this]() -> FReply {
                    UE_LOG(LogMakeLightModule, Warning, TEXT("기존 조명 부착 버튼이 클릭되었습니다."));
                    FMakeLightFunctionality MakeLightFunctionality;
                    return MakeLightFunctionality.OnAttachExistingLightButtonClicked(SelectedAttachBone, CustomBoneName);
                })
            ]
        ];

}

FString FMakeLightModule::GetLightTypeString(ELightType LightType)
{
    switch (LightType)
    {
        case ELightType::Spot: return "Spot";
        case ELightType::Rect: return "Rect";
        case ELightType::Point: return "Point";
        default: return "Unknown";
    }
}

FString FMakeLightModule::GetLightPurposeString(ELightPurpose LightPurpose)
{
    switch (LightPurpose)
    {
        case ELightPurpose::None: return "None";
        case ELightPurpose::Key: return "Key";
        case ELightPurpose::Fill: return "Fill";
        case ELightPurpose::LeftRim: return "Left Rim";
        case ELightPurpose::RightRim: return "Right Rim";
        case ELightPurpose::ThreePoint: return "ThreePoint";
        default: return "Unknown";
    }
}

FString FMakeLightModule::GetAttachBoneString(EAttachBone AttachBone)
{
    switch (AttachBone)
    {
        case EAttachBone::None: return "None";
        case EAttachBone::Head: return "Head";
        case EAttachBone::Spine: return "Spine";
        case EAttachBone::Custom: return "Custom";
        default: return "Unknown";
    }
}

#undef LOCTEXT_NAMESPACE
