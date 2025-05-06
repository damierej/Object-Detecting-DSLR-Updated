#SingleInstance Force  ; Ensure only one instance of the script runs
SetWorkingDir A_ScriptDir  ; Set the working directory to the script's directory

; Set the window title match mode to partial match and case-insensitive
SetTitleMatchMode 2
SetTitleMatchMode "Slow"

; Set coordinate mode to window-relative
CoordMode "Mouse", "Window"

; Possible window titles to try
possibleTitles := ["EOS 90D", "EOS Utility", "Canon EOS Utility", "EOS Utility 3", "Canon EOS Utility 3"]

; Flag to track if the window was found
windowFound := false

; Try to find and activate the Canon EOS Utility window
for title in possibleTitles
{
    if WinExist(title)
    {
        WinActivate(title)
        ; Wait for the window to become active, with a 2-second timeout
        if WinWaitActive(title, , 2)
        {
            windowFound := true
            break
        }
    }
}

; Check if the window was found and activated
if (!windowFound)
{
    ; Manually concatenate the array elements into a string
    titlesList := ""
    for index, title in possibleTitles
    {
        if (index > 1)
            titlesList .= ", "
        titlesList .= title
    }
    MsgBox("Could not activate Canon EOS Utility window! Please ensure the app is open and the window title matches one of: " titlesList)
    ExitApp
}

; Add a delay to ensure the window is fully active
Sleep 500

; Move mouse to the shutter button and click (using window-relative coordinates)
MouseMove(310, 126, 0)  ; Replace with your new Window coordinates from Window Spy
Click()
Sleep 100  ; Small delay to ensure the click registers

; Wait for the camera to capture the image
Sleep 2000

ExitApp  ; Exit the script after running