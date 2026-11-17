$ErrorActionPreference = 'Stop'
$project = 'C:\Users\21413\Documents\Codex\2026-10-24\ni'
$destination = 'E:\xiuxian'
if (Test-Path -LiteralPath $destination) { throw 'Destination already exists; inspect before merging.' }
$runtime = Join-Path $project 'outputs\太古仙尊每日助手\太古仙尊每日助手'
$source = Join-Path $project 'outputs\太古仙尊实验版'
$scratch = Join-Path $project 'work'
$archive = Join-Path $project 'outputs\太古仙尊每日助手.zip'
$proofs = [Collections.Generic.List[object]]::new()
function Copy-VerifiedDirectory([string]$from, [string]$to) {
    $resolved = (Resolve-Path -LiteralPath $from).Path
    if (-not $resolved.StartsWith($project + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Source outside workspace' }
    $absolute = [IO.Path]::GetFullPath($to)
    if ($absolute -ne $destination -and -not $absolute.StartsWith($destination + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination outside target' }
    $links = @(Get-ChildItem -LiteralPath $resolved -Force -Recurse | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
    if ($links.Count) { throw "Inspect reparse points before copying $resolved" }
    $files = @(Get-ChildItem -LiteralPath $resolved -File -Force -Recurse)
    New-Item -ItemType Directory -Path (Split-Path -Parent $absolute) -Force | Out-Null
    Copy-Item -LiteralPath $resolved -Destination $absolute -Recurse -Force
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($resolved.Length + 1)
        $target = Join-Path $absolute $relative
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Missing copied file: $relative" }
        $originalHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        $newHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
        if ($originalHash -ne $newHash) { throw "Hash mismatch: $relative" }
    }
    $proofs.Add([pscustomobject]@{Source=$resolved;Destination=$absolute;VerifiedFiles=$files.Count})
    Write-Output "Verified $($files.Count) files: $absolute"
}
Copy-VerifiedDirectory $runtime $destination
Copy-VerifiedDirectory $source (Join-Path $destination '开发资料\旧实验版')
Copy-VerifiedDirectory $scratch (Join-Path $destination '开发资料\work')
$packageDir = Join-Path $destination '发布包'
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null
$package = Join-Path $packageDir '太古仙尊每日助手.zip'
Copy-Item -LiteralPath $archive -Destination $package
if ((Get-FileHash -LiteralPath $archive).Hash -ne (Get-FileHash -LiteralPath $package).Hash) { throw 'Archive hash mismatch' }
$proofs | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $destination '迁移核验.json') -Encoding utf8
Write-Output 'Copy and SHA256 verification complete. C drive originals retained until E drive startup verification.'
