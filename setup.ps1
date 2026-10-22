$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (!(Test-Path ".env")) {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $secretBytes = New-Object byte[] 48
    $passwordBytes = New-Object byte[] 24
    $rng.GetBytes($secretBytes)
    $rng.GetBytes($passwordBytes)
    $secret = [BitConverter]::ToString($secretBytes).Replace("-", "").ToLower()
    $password = [BitConverter]::ToString($passwordBytes).Replace("-", "").ToLower()
    @("SECRET_KEY=$secret", "POSTGRES_PASSWORD=$password") | Set-Content -Encoding ascii ".env"
    $rng.Dispose()
    Write-Host "Created local settings."
}
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw "Startup failed. Check Docker Desktop and the output above." }
$port = (Select-String -Path ".env" -Pattern "^HTTP_PORT=(\d+)" | ForEach-Object { $_.Matches[0].Groups[1].Value })
if ($port -and $port -ne "80") { Write-Host "Open http://localhost:$port" } else { Write-Host "Open http://localhost" }
