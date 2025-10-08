param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Files
)

$LogDir = ".precommit_logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir "isort.log"

function Write-Log($Message) {
    Add-Content -Path $LogFile -Value $Message -Encoding UTF8
}

Write-Log "Running isort..."

$Failed = $false
foreach ($file in $Files) {
    $result = & isort $file 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ Failed: $file"
        Write-Log $result
        $Failed = $true
    } elseif ($result -match "Fixing" -or $result -match "Reordering") {
        Write-Log "🔧 Fixed imports: $file"
    } else {
        Write-Log "✅ Passed: $file"
    }
}

if ($Failed) { exit 1 } else { exit 0 }