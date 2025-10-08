param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Files
)

$LogDir = ".precommit_logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir "autoflake.log"

function Write-Log($Message) {
    Add-Content -Path $LogFile -Value $Message -Encoding UTF8
}

Write-Log "Running autoflake (remove unused imports / vars)..."

$Failed = $false
foreach ($file in $Files) {
    $result = & autoflake --remove-all-unused-imports --remove-unused-variables --in-place --expand-star-imports $file 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ Failed: $file"
        Write-Log $result
        $Failed = $true
    } else {
        Write-Log "🔧 Cleaned: $file"
    }
}

if ($Failed) { exit 1 } else { exit 0 }
