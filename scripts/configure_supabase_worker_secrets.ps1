param(
    [string] $WorkerDir = "$PSScriptRoot\..\cloudflare-worker"
)

$ErrorActionPreference = "Stop"

function Require-EnvVar {
    param([string] $Name)

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Variabile d'ambiente mancante: $Name"
    }
    return $value.Trim()
}

$supabaseUrl = Require-EnvVar "SUPABASE_URL"
$serviceRoleKey = Require-EnvVar "SUPABASE_SERVICE_ROLE_KEY"

if (-not $supabaseUrl.StartsWith("https://")) {
    throw "SUPABASE_URL deve iniziare con https://"
}

if ($serviceRoleKey.Length -lt 40) {
    throw "SUPABASE_SERVICE_ROLE_KEY sembra troppo corta."
}

Push-Location $WorkerDir
try {
    $supabaseUrl | npx wrangler secret put SUPABASE_URL
    $serviceRoleKey | npx wrangler secret put SUPABASE_SERVICE_ROLE_KEY
    npx wrangler secret list
}
finally {
    Pop-Location
}
