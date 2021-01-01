#SingleInstance force
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

SetTitleMatchMode, RegEx

;; Use this until I hit the first issue then document here and set back to default value.
SetDefaultMouseSpeed, 0

;; Copy clean file/directory path to clipboard (use forward slashes as file separators) {{{
;; https://stackoverflow.com/questions/1589930/so-what-is-the-right-direction-of-the-paths-slash-or-under-windows/1589959#1589959

;; WARNING: This clipboard substitution has the issue that after the substitution, pasting the file does not work anymore!!
;; Because of this, we don’t run the substitution OnClipboardChange globally but only when we consider it save and otherwise using a (manual) shortcut.
;; Situations where we know it is save:
;; * Double Commander calls CopyFullNamesToClip.
;; * Location bar in Explorer has focus. See limitations below!

;; The expected workflow is:
;; 1. Do what you usually do to copy a path.
;; 2. We try to do what is necessary to have a clean path in the clipboard.
;; 3. If we cannot do it by default (we don’t know that it is save), we do nothing and you have to manually make the path in the clipboard clean by pressing Shift+Super+C.

;; Ref: Get-CleanPath in ../../MS_Shell/Modules/ypidDotfiles/ypidDotfiles.psm1
;; Seems up to and including Windows 10, UNC paths with forward slashes don’t work.
;; At least //files.example.org/home and \\files.example.org/home and //files.example.org\home don’t work.
clean_path_in_clipboard() {
    If (RegExMatch(Clipboard, "^(?i)(?:[a-z]:)?\\[^\\]")) {
        StringReplace, Clipboard, Clipboard,\,/, All
    }
    Return
}

;; Shift+Super+C | Clean file/directory path in clipboard {{{
+#C::
    ; ClipSaved := ClipboardAll
    ; Clipboard = 

    ; Send ^c
    ;; Ensure that we are only working on text.
    ; ClipWait

    ; currentPath =
    ; WinGetClass explorerClass, A
    ; ControlGetText currentPath, Edit1, ahk_class %explorerClass%
    ; msgbox %currentPath%

    ; If (ErrorLevel) {
    ;     Clipboard := ClipSaved
    ;     MsgBox, 48, Clipboard copy warning, Failed to copy to clipboard.
    ;     Return
    ; }

    clean_path_in_clipboard()
Return
;; }}}

;; Shift+Alt+C | Hook Double Commander calls to CopyFullNamesToClip and run clean_path_in_clipboard afterwards.
;; We can "safely" do this because when CopyFullNamesToClip is called, the user wants to copy the path as text.
#UseHook
#IfWinActive ahk_exe doublecmd.exe
+!c::
    Send +!c
    clean_path_in_clipboard()
Return
#IfWinActive
#UseHook off

OnClipboardChange:
    ;; Fix file path when in transit in Explorer (or Double Commander).
    ;; Ensure that we are only working on text.
    If (WinActive("ahk_exe (?i)(?:explorer.exe|doublecmd.exe)") and A_EventInfo == 1) {

        ;; Location bar in Explorer has focus.
        ;; Run clean_path_in_clipboard after copying text to clipboard in Explorer when cursor is above "Location bar" known as Edit1 (bad programming/variable naming M$??).
        ;; Technically this is not 100 % bulletproof because you could do the copy to clipboard with Ctrl+L followed Ctrl+C while the cursor focuses some other control.
        If (WinActive("ahk_exe (?i)(?:explorer.exe)")) {
            MouseGetPos, , , , control_below_cursor
            If (control_below_cursor == "Edit1") {
                clean_path_in_clipboard()
            }
        }

        ;; We cannot do this globally, see WARNING above.
        ; clean_path_in_clipboard()
    }
return

;; }}}