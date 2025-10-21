# sync_git.ps1
# 
# 用法：
#   powershell -ExecutionPolicy Bypass -File .\sync_git.ps1
#   可选参数：-MaxRetries <重试次数> -DelaySeconds <每次重试间隔秒数>
#   例如：powershell -ExecutionPolicy Bypass -File .\sync_git.ps1 -MaxRetries 10 -DelaySeconds 8
#
# 功能：
#   自动执行 git pull 和 git push，遇到网络或其他错误时自动重试。
#   默认最大重试5次，每次间隔5秒。

param(
    [int]$MaxRetries = 5,
    [int]$DelaySeconds = 5
)

function Retry-GitCommand {
    param(
        [string]$Command,
        [int]$MaxRetries,
        [int]$DelaySeconds
    )
    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        Write-Host "Running: $Command (Attempt $($attempt+1)/$MaxRetries)"
        try {
            Invoke-Expression $Command
            if ($LASTEXITCODE -eq 0) {
                Write-Host "$Command succeeded."
                return $true
            } else {
                Write-Host "$Command failed with exit code $LASTEXITCODE."
            }
        } catch {
            Write-Host "$Command encountered an error: $_"
        }
        $attempt++
        if ($attempt -lt $MaxRetries) {
            Write-Host "Retrying in $DelaySeconds seconds..."
            Start-Sleep -Seconds $DelaySeconds
        }
    }
    Write-Host "$Command failed after $MaxRetries attempts."
    return $false
}

# Pull
if (-not (Retry-GitCommand "git pull" $MaxRetries $DelaySeconds)) {
    Write-Host "git pull failed after retries. Exiting."
    exit 1
}

# Push
if (-not (Retry-GitCommand "git push" $MaxRetries $DelaySeconds)) {
    Write-Host "git push failed after retries. Exiting."
    exit 1
}

Write-Host "Git pull and push completed successfully."
