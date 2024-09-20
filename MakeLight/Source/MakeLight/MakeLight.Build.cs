// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class MakeLight : ModuleRules
{
	public MakeLight(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicIncludePaths.AddRange(
			new string[] {
				"C:/Program Files/Epic Games/UE_5.3/Engine/Source/Runtime/MovieSceneTracks/Public",
				"D:/Unreal Projects/MakeSubSeq/Plugins/MakeLight/Source/MakeLight/Public"
				// ... add other public include paths required here ...
			}
		);
				
		
		PrivateIncludePaths.AddRange(
			new string[] {
				"C:/Program Files/Epic Games/UE_5.3/Engine/Source/Runtime/MovieSceneTracks/Private",
				"D:/Unreal Projects/MakeSubSeq/Plugins/MakeLight/Source/MakeLight/Private"
				// ... add other private include paths required here ...
			}
		);
			
		
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"InputCore",
				"LevelSequence",
				"LevelSequenceEditor",
				"MovieScene",
				"MovieSceneTracks",
				"Sequencer",
				"Slate",
				"SlateCore",
				"InteractiveToolsFramework",
				"EditorFramework",
				"UnrealEd",
				"EditorStyle",
                "AssetTools"
			}
			);
			
		
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"Projects",
				"Core",
				"Engine",
				"InputCore",
				"ToolMenus",
				"CoreUObject",
				"LevelSequence",
				"LevelSequenceEditor",
				"Sequencer",
				"MovieScene",
				"MovieSceneTracks",
				"Sequencer",
				"Slate",
				"SlateCore",
				"InteractiveToolsFramework",
				"EditorFramework",
				"UnrealEd",
				"EditorStyle",
				"AssetTools"
			}
			);
		
		
		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
			);
	}
}
