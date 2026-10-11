$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRoot '.venv\Scripts\python.exe'
$taskScript = Join-Path $PSScriptRoot 'run_student_reasoning_study.py'
$taskReports = Join-Path $taskRoot 'reports'
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Create the project .venv and install requirements first. See README.md.'
}
New-Item -ItemType Directory -Path $taskReports -Force | Out-Null
# No credential is passed in arguments or saved. The child opens a masked dialog.
$taskProcess = Start-Process -FilePath $taskPython -ArgumentList @(
    '-X', 'utf8', ('"' + $taskScript + '"'), '--mode', 'api', '--prompt-key-gui',
    '--budget', '10', '--groups', '3'
) -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $taskReports 'student_live_stdout.log') `
    -RedirectStandardError (Join-Path $taskReports 'student_live_stderr.log')
$taskProcess.Id | Set-Content -LiteralPath (Join-Path $taskReports 'student_live.pid')
Write-Output ('Launched masked key entry. Process ID: ' + $taskProcess.Id)
