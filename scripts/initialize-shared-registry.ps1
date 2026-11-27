[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$envPath = Join-Path (Split-Path -Parent $PSScriptRoot) '.env'
$existing = if (Test-Path -LiteralPath $envPath) { Get-Content -LiteralPath $envPath -Raw }

function New-NexusSecret {
    $random = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $bytes = [byte[]]::new(32)
        $random.GetBytes($bytes)
        return ([BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
    } finally {
        $random.Dispose()
    }
}

$items = [ordered]@{
    COMPOSE_PROFILES = 'shared'
    NEXUS_REGISTRY_DB_HOST = 'postgres'
    NEXUS_DB_ADMIN_PASSWORD = $null
    NEXUS_DB_APP_PASSWORD = $null
    NEXUS_SHARED_OWNER_TOKEN = $null
    NEXUS_SHARED_READER_TOKEN = $null
}

$newEntries = foreach ($key in $items.Keys) {
    if ($existing -notmatch "(?m)^\s*$key\s*=") {
        $value = $items[$key]
        if ($null -eq $value) { $value = New-NexusSecret }
        "$key=$value"
    }
}

if ($newEntries) {
    $block = [Environment]::NewLine + ($newEntries -join [Environment]::NewLine) + [Environment]::NewLine
    [IO.File]::AppendAllText($envPath, $block)
}
Write-Output 'Shared registry configuration is available in the local .env file.'
