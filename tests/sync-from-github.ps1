param([string]$Repository=(Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference='Stop'
$Repository=[IO.Path]::GetFullPath($Repository)
$gitArgs=@('-c',('safe.directory='+$Repository),'-C',$Repository)
$remote=(& git @gitArgs remote get-url origin)
if($LASTEXITCODE -ne 0 -or $remote -ne 'https://github.com/claude51671488-hash/Smart-Robotics-Warfare.git'){throw 'Unexpected Git remote'}
$dirty=(& git @gitArgs status --porcelain)
if($LASTEXITCODE -ne 0){throw 'Cannot inspect Git working tree'}
if($dirty){throw 'Local changes exist; synchronization stopped without overwriting them'}
& git @gitArgs fetch origin
if($LASTEXITCODE -ne 0){throw 'Fetch failed; no working files changed'}
& git @gitArgs merge --ff-only origin/main
if($LASTEXITCODE -ne 0){throw 'Branches diverged; manual review is required. No reset or force push was used'}
Write-Output 'Source files synchronized. Restart Forts before installing changed game resources.'
