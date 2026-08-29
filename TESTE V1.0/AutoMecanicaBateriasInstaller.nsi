!include "MUI2.nsh"

Name "Auto Mecânica & Baterias"
OutFile "dist\\AutoMecanicaBateriasInstaller.exe"
InstallDir "$PROGRAMFILES\\AutoMecanicaBaterias"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Instalar"
  SetOutPath "$INSTDIR"
  File ".\\dist\\AutoMecanicaBaterias.exe"
  CreateDirectory "$SMPROGRAMS\\Auto Mecânica & Baterias"
  CreateShortCut "$SMPROGRAMS\\Auto Mecânica & Baterias\\Auto Mecânica & Baterias.lnk" "$INSTDIR\\AutoMecanicaBaterias.exe"
  CreateShortCut "$DESKTOP\\Auto Mecânica & Baterias.lnk" "$INSTDIR\\AutoMecanicaBaterias.exe"
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\AutoMecanicaBaterias.exe"
  Delete "$INSTDIR\\Uninstall.exe"
  Delete "$SMPROGRAMS\\Auto Mecânica & Baterias\\Auto Mecânica & Baterias.lnk"
  Delete "$DESKTOP\\Auto Mecânica & Baterias.lnk"
  RMDir "$SMPROGRAMS\\Auto Mecânica & Baterias"
  RMDir "$INSTDIR"
SectionEnd
