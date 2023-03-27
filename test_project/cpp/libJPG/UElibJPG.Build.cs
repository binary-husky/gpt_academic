// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class UElibJPG : ModuleRules
{
	public UElibJPG(ReadOnlyTargetRules Target) : base(Target)
    {
        Type = ModuleType.External;

		string libJPGPath = Target.UEThirdPartySourceDirectory + "libJPG";
		PublicIncludePaths.Add(libJPGPath);

		ShadowVariableWarningLevel = WarningLevel.Off;
	}
}
