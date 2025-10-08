param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Files
)

function Write-Log($Message) {
    Add-Content -Path $LogFile -Value $Message -Encoding UTF8
}


$LogDir = ".precommit_logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir "vulture.log"



Write-Log "Running vulture (dead code detector)..."

$Failed = $false
foreach ($file in $Files) {
    $result = & vulture $file 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ Error: $file"
        Write-Log $result
        $Failed = $true
    } elseif ($result -match "unused") {
        Write-Log "⚠️  Possibly unused code in: $file"
        Write-Log $result
        $Failed = $true
    } else {
        Write-Log "✅ Clean: $file"
    }
}

if ($Failed) { exit 1 } else { exit 0 }