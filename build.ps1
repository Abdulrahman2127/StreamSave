[CmdletBinding()]
param([string]$Python = "", [string]$FFmpegDirectory = "", [string]$DenoPath = "")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Push-Location $PSScriptRoot
try {
    if (-not $Python) {
        if (Test-Path .venv/Scripts/python.exe) { $Python = "$PSScriptRoot/.venv/Scripts/python.exe" }
        else { $Python = (Get-Command python -ErrorAction Stop).Source }
    }
    & $Python -c "import sys; assert sys.platform == 'win32', 'Build on Windows'; assert sys.version_info >= (3,11); import customtkinter, PIL, yt_dlp, yt_dlp_ejs, PyInstaller"
    if ($LASTEXITCODE -ne 0) { throw "Missing dependencies. Run: $Python -m pip install -r requirements-build.txt" }
    & $Python -c "import tkinter; app = tkinter.Tk(); app.withdraw(); app.destroy()"
    if ($LASTEXITCODE -ne 0) { throw "Tcl/Tk startup failed. Build from a normal Windows desktop with the full Python Tcl/Tk installation accessible." }
    & $Python -m pip check
    if ($LASTEXITCODE -ne 0) { throw "Python dependency validation failed." }
    New-Item -ItemType Directory -Force vendor | Out-Null
    $candidates = @($FFmpegDirectory, "$PSScriptRoot/vendor")
    $command = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
    if ($command) { $candidates += Split-Path $command.Source }
    $candidates += @('C:/ffmpeg/bin', 'C:/Program Files/ffmpeg/bin')
    $found = $null
    foreach ($directory in $candidates) {
        if ($directory -and (Test-Path "$directory/ffmpeg.exe") -and (Test-Path "$directory/ffprobe.exe")) {
            $found = (Resolve-Path $directory).Path
            break
        }
    }
    if (-not $found) { throw "Cannot locate ffmpeg.exe and ffprobe.exe. Add their directory to PATH, place them in vendor, or pass -FFmpegDirectory." }
    if (-not $DenoPath) {
        if (Test-Path vendor/deno.exe) { $DenoPath = "$PSScriptRoot/vendor/deno.exe" }
        else {
            $command = Get-Command deno.exe -ErrorAction SilentlyContinue
            if ($command) { $DenoPath = $command.Source }
        }
    }
    if (-not $DenoPath -or -not (Test-Path -LiteralPath $DenoPath -PathType Leaf)) {
        throw "Deno is required for a self-contained release. Place deno.exe in vendor, add it to PATH, or pass -DenoPath."
    }
    $tools = @{ 'ffmpeg.exe' = "$found/ffmpeg.exe"; 'ffprobe.exe' = "$found/ffprobe.exe"; 'deno.exe' = $DenoPath }
    foreach ($name in $tools.Keys) {
        $source = (Resolve-Path -LiteralPath $tools[$name]).Path
        $destination = [IO.Path]::GetFullPath("$PSScriptRoot/vendor/$name")
        if ($source -ne $destination) { Copy-Item -LiteralPath $source -Destination $destination }
        $versionArgument = if ($name -eq 'deno.exe') { '--version' } else { '-version' }
        $versionOutput = & $destination $versionArgument
        if ($LASTEXITCODE -ne 0) { throw "$name failed its version check. Use standalone binaries matching Windows architecture." }
        Write-Host $versionOutput[0]
    }
    if (-not (Test-Path vendor/licenses -PathType Container) -or -not (Get-ChildItem vendor/licenses -File -Recurse)) {
        throw "Place redistribution licenses/notices for your FFmpeg and Deno builds in vendor/licenses before building. See RELEASE.md."
    }
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Automated tests failed." }
    & $Python packaging/collect_licenses.py
    if ($LASTEXITCODE -ne 0) { throw "Could not collect dependency notices." }
    # The generated spec stays under build; the tracked spec is an equivalent manual entry point.
    & $Python -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name StreamSave `
        --specpath build --distpath dist --workpath build/pyinstaller `
        --version-file "$PSScriptRoot/packaging/version_info.txt" `
        --collect-all customtkinter --collect-all yt_dlp --collect-all yt_dlp_ejs `
        --add-binary "$PSScriptRoot/vendor/ffmpeg.exe;vendor" --add-binary "$PSScriptRoot/vendor/ffprobe.exe;vendor" `
        --add-binary "$PSScriptRoot/vendor/deno.exe;vendor" --add-data "$PSScriptRoot/vendor/licenses;vendor/licenses" "$PSScriptRoot/main.py"
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed. Review its output above." }
    if (-not (Test-Path dist/StreamSave.exe -PathType Leaf)) { throw "PyInstaller did not produce dist/StreamSave.exe." }
    $hash = (Get-FileHash dist/StreamSave.exe -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  StreamSave.exe" | Set-Content dist/SHA256SUMS.txt -Encoding ascii
    Compress-Archive -Path vendor/licenses/* -DestinationPath dist/THIRD-PARTY-NOTICES.zip -Force
    & $Python -m pip freeze | Set-Content dist/build-environment.txt -Encoding utf8
    Write-Host "Built v1.0.0: $PSScriptRoot/dist/StreamSave.exe"
    Write-Host "SHA-256: $hash"
} catch {
    [Console]::Error.WriteLine("StreamSave build failed: $_")
    exit 1
} finally { Pop-Location }
