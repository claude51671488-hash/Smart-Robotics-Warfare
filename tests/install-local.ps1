param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $sourceRoot '..'))
# Development installs must never overwrite Steam's subscribed Workshop cache.
# Otherwise clients download the published revision while the host runs new files
# under the same Workshop ID, causing frame-2 Devices/Scripts desync.
$targets = @('C:\Program Files (x86)\Steam\steamapps\common\Forts\data\mods\SmartRoboticsWarfare')

$runtimeDirectories = @('audio','devices','effects','materials','mods','scripts','ui','weapons')
$files = @(Get-Item -LiteralPath (Join-Path $sourceRoot 'script.lua'),(Join-Path $sourceRoot 'mod.lua'),(Join-Path $sourceRoot 'displayname.lua'))
foreach ($name in $runtimeDirectories) {
    $files += @(Get-ChildItem -LiteralPath (Join-Path $sourceRoot $name) -Recurse -File)
}
$files = @($files | Where-Object { $_.Name -ne '.gitkeep' })
$plan = @()
for ($i=0; $i -lt $targets.Count; $i++) {
    $target = [IO.Path]::GetFullPath($targets[$i])
    if (-not (Test-Path -LiteralPath $target -PathType Container)) { throw "Missing known mod copy: $target" }
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($sourceRoot.Length+1)
        if ($relative -match '(^|\\)(publishedfileid|itemversion)\.lua$') { throw 'Workshop metadata in runtime list' }
        $destination = [IO.Path]::GetFullPath((Join-Path $target $relative))
        if (-not $destination.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Path escaped mod folder' }
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        $previous = if (Test-Path -LiteralPath $destination -PathType Leaf) { (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash } else { $null }
        $plan += [pscustomobject]@{Copy=$i;Relative=$relative;Source=$file.FullName;Destination=$destination;Hash=$hash;Previous=$previous;Changed=($hash -ne $previous)}
    }
}
if (-not $Apply) {
    $plan | Group-Object Copy | ForEach-Object { [pscustomobject]@{Copy=$_.Name;Files=$_.Count;Changed=@($_.Group | Where-Object Changed).Count} } | ConvertTo-Json
    return
}
if (Get-Process Forts -ErrorAction SilentlyContinue) { throw 'Forts is running; installation stopped before writing' }
$backup = Join-Path $workspaceRoot ('srw-backups\0.52.2-dynamit-faster-run-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
$metadata = @{}
foreach ($target in $targets) {
    foreach ($name in @('publishedfileid.lua','itemversion.lua')) {
        $file = Join-Path $target $name
        if (Test-Path -LiteralPath $file) { $metadata[$file]=(Get-FileHash -LiteralPath $file).Hash }
    }
}
New-Item -ItemType Directory -Path $backup -Force | Out-Null
foreach ($entry in $plan) {
    if (-not $entry.Changed) { continue }
    if ($entry.Previous) {
        $saved = Join-Path $backup (Join-Path ('copy-'+$entry.Copy) $entry.Relative)
        New-Item -ItemType Directory -Path (Split-Path -Parent $saved) -Force | Out-Null
        Copy-Item -LiteralPath $entry.Destination -Destination $saved
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $entry.Destination) -Force | Out-Null
    Copy-Item -LiteralPath $entry.Source -Destination $entry.Destination -Force
}
foreach ($entry in $plan) {
    if ((Get-FileHash -LiteralPath $entry.Destination -Algorithm SHA256).Hash -ne $entry.Hash) { throw "Hash mismatch: $($entry.Destination)" }
}
foreach ($name in $metadata.Keys) {
    if ((Get-FileHash -LiteralPath $name).Hash -ne $metadata[$name]) { throw 'Workshop metadata changed unexpectedly' }
}
$manifest=[pscustomobject]@{Version='0.52.2-dynamit-faster-run';Targets=$targets;FilesPerCopy=$files.Count;Changed=@($plan | Where-Object Changed).Count;MetadataPreserved=$true;Files=$plan}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backup 'install-manifest.json') -Encoding utf8
[pscustomobject]@{Backup=$backup;FilesPerCopy=$files.Count;Changed=$manifest.Changed;Copies=$targets.Count;MetadataPreserved=$true;AllHashesVerified=$true} | ConvertTo-Json
