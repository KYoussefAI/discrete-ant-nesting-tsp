$ErrorActionPreference = "Stop"

$Distro = "Ubuntu"
$TestDistro = "Ubuntu-test"
$BackupDir = "E:\wsl-backups"
$BackupTar = Join-Path $BackupDir "Ubuntu-backup-2026-06-29.tar"
$TargetRoot = "D:\wsl"
$TestInstall = Join-Path $TargetRoot "Ubuntu-test"
$SourceProjects = "E:\projects"
$TargetProjects = "D:\wsl\projects"
$Log = Join-Path $BackupDir "migration-safe-2026-06-29.log"

function Log($Message) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $Log -Value $line
    Write-Host $line
}

function Run($File, [string[]]$ArgList) {
    Log ("> {0} {1}" -f $File, ($ArgList -join " "))
    & $File @ArgList 2>&1 | Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $File $($ArgList -join ' ')"
    }
}

function RunAllow($File, [string[]]$ArgList) {
    Log ("> {0} {1}" -f $File, ($ArgList -join " "))
    & $File @ArgList 2>&1 | Tee-Object -FilePath $Log -Append
    return $LASTEXITCODE
}

New-Item -ItemType Directory -Force $BackupDir | Out-Null
New-Item -ItemType Directory -Force $TargetRoot | Out-Null
Set-Content -Path $Log -Value "Safe WSL migration log started $(Get-Date -Format o)"

Log "Inspecting WSL distros"
Run "wsl.exe" @("-l", "-v")

$distroNames = (& wsl.exe -l -q) -replace "`0", "" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
if ($distroNames -notcontains $Distro) {
    throw "Expected distro '$Distro' was not found. Found: $($distroNames -join ', ')"
}
if ($distroNames -contains $TestDistro) {
    throw "Test distro '$TestDistro' already exists. Refusing to overwrite it."
}
if (Test-Path $TestInstall) {
    throw "Target test install path already exists: $TestInstall. Refusing to overwrite it."
}

Log "Creating target directories"
New-Item -ItemType Directory -Force $BackupDir | Out-Null
New-Item -ItemType Directory -Force $TargetRoot | Out-Null

Log "Shutting down WSL before export"
Run "wsl.exe" @("--shutdown")

if (-not (Test-Path $BackupTar)) {
    Log "Exporting $Distro to $BackupTar"
    Run "wsl.exe" @("--export", $Distro, $BackupTar)
} else {
    Log "Backup tar already exists, leaving it untouched: $BackupTar"
}

Log "Importing non-destructive test distro $TestDistro into $TestInstall"
Run "wsl.exe" @("--import", $TestDistro, $TestInstall, $BackupTar, "--version", "2")

Log "Restoring /etc/wsl.conf in $TestDistro"
$wslConfCmd = "cat > /etc/wsl.conf <<'EOF'`n[boot]`nsystemd=true`n`n[user]`ndefault=youssef`n`n[interop]`nappendWindowsPath=true`nEOF"
Run "wsl.exe" @("-d", $TestDistro, "--user", "root", "--", "bash", "-lc", $wslConfCmd)
Run "wsl.exe" @("--terminate", $TestDistro)

Log "Copying projects from $SourceProjects to $TargetProjects, excluding envs"
New-Item -ItemType Directory -Force $TargetProjects | Out-Null
$roboArgs = @($SourceProjects, $TargetProjects, "/E", "/COPY:DAT", "/DCOPY:DAT", "/XD", (Join-Path $SourceProjects "envs"), "/R:2", "/W:2", "/NFL", "/NDL", "/NP")
Log ("> robocopy.exe {0}" -f ($roboArgs -join " "))
& robocopy.exe @roboArgs 2>&1 | Tee-Object -FilePath $Log -Append
$roboExit = $LASTEXITCODE
if ($roboExit -ge 8) {
    throw "Robocopy failed with exit code $roboExit"
}
Log "Robocopy completed with non-fatal exit code $roboExit"

Log "Recreating Python environment in $TestDistro"
$setupCmd = @'
set -euo pipefail
TARGET=/mnt/d/wsl/projects
ENV=$TARGET/envs/youssef
PY=$TARGET/.tools/python3.10/python/bin/python3.10
mkdir -p "$TARGET/envs"
if [ ! -x "$PY" ]; then
  echo "Expected Python tool is not executable: $PY"
  ls -la "$TARGET/.tools/python3.10/python/bin" || true
  exit 10
fi
"$PY" --version
rm -rf "$ENV"
"$PY" -m venv "$ENV"
"$ENV/bin/python" -m pip install --upgrade pip
"/mnt/e/projects/envs/youssef/bin/python" -m pip freeze > "$TARGET/youssef-requirements-freeze.txt"
echo "Requirement path reference scan:"
grep -nE "/mnt/e|E:|file://|^-e " "$TARGET/youssef-requirements-freeze.txt" || true
if grep -qE "/mnt/e|E:|file://|^-e " "$TARGET/youssef-requirements-freeze.txt"; then
  echo "Path-based requirements detected; stopping before install."
  exit 11
fi
"$ENV/bin/python" -m pip install -r "$TARGET/youssef-requirements-freeze.txt"
'@
Run "wsl.exe" @("-d", $TestDistro, "--", "bash", "-lc", $setupCmd)

Log "Updating aliases in $TestDistro"
$aliasCmd = @'
set -euo pipefail
cp ~/.bashrc ~/.bashrc.backup-before-d-migration
python3 - <<'PY'
from pathlib import Path
p = Path.home() / ".bashrc"
s = p.read_text()
s = s.replace("alias youssef='cd /mnt/e/projects && source /mnt/e/projects/envs/youssef/bin/activate'",
              "alias youssef='cd /mnt/d/wsl/projects && source /mnt/d/wsl/projects/envs/youssef/bin/activate'")
s = s.replace("alias projectpdf='python3.10 /mnt/e/projects/project_to_pdf.py'",
              "alias projectpdf='/mnt/d/wsl/projects/envs/youssef/bin/python /mnt/d/wsl/projects/project_to_pdf.py'")
s = s.replace("alias to_pdf='python3.10 /mnt/e/projects/project_to_pdf.py'",
              "alias to_pdf='/mnt/d/wsl/projects/envs/youssef/bin/python /mnt/d/wsl/projects/project_to_pdf.py'")
p.write_text(s)
PY
'@
Run "wsl.exe" @("-d", $TestDistro, "--", "bash", "-lc", $aliasCmd)

Log "Verifying test distro before restart"
$verifyCmd = @'
set -euo pipefail
echo "whoami=$(whoami)"
echo "home=$HOME"
bash -ic 'type youssef; youssef; echo "pwd=$(pwd)"; echo "python=$(command -v python)"; python --version; echo "pip=$(command -v pip)"; pip --version'
test -d /mnt/d/wsl/projects/metaheuristics/discrete-ant-nesting-tsp
test -x /mnt/d/wsl/projects/envs/youssef/bin/python
echo "Remaining important E project refs:"
rg -n "/mnt/e/projects|E:\\projects|E:/projects" ~/.bashrc ~/.profile ~/.bash_aliases ~/.config ~/.local/bin 2>/dev/null || true
'@
Run "wsl.exe" @("-d", $TestDistro, "--", "bash", "-lc", $verifyCmd)

Log "Restarting test distro and verifying again"
Run "wsl.exe" @("--terminate", $TestDistro)
Run "wsl.exe" @("-d", $TestDistro, "--", "bash", "-lc", $verifyCmd)

Log "Safe migration phase completed successfully. Original Ubuntu was not unregistered and old E: folders were not deleted."
