param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Files
)
function Write-Log($Message) {
    Add-Content -Path $LogFile -Value $Message -Encoding UTF8
}


$LogDir = ".precommit_logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir "mypy.log"

"Running mypy..." | Out-File -FilePath $LogFile -Encoding utf8

$Failed = $false
foreach ($file in $Files) {
    $result = & mypy $file 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ Failed: $file"
        Write-Log $result
        $Failed = $true
    } else {
        Write-Log " ✅ PASSED: $file"
    }
}

if ($Failed) { exit 1 } else { exit 0 }
