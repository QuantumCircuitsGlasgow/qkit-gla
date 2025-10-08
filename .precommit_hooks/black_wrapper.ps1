param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Files
)
function Write-Log($Message) {
    Add-Content -Path $LogFile -Value $Message -Encoding UTF8
}

$LogDir = ".precommit_logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir "black.log"

"Running black..." | Out-File -FilePath $LogFile -Encoding utf8

$Failed = $false
foreach ($file in $Files) {
    $result = & black $file 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed: $file"
        Write-Log $result
        $Failed = $true
    } elseif ($result -match "reformatted") {
        Write-Log "Reformatted: $file"
    } else {
        Write-Log "✅ Passed: $file"
    }
}

if ($Failed) { exit 1 } else { exit 0 }
