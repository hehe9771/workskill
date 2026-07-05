# Quark Browser Rancher Password Autofill Fix Launcher
param([string]$Url = "https://rancher.nbmarket.cn/dashboard/auth/login")

$QuarkExe = "C:\Program Files\Quark\quark.exe"
$CdpPort = 9222

$FixScript = @'
(function() {
    'use strict';
    var observer = new MutationObserver(function() { fixInputs(); });
    function fixInputs() {
        if (window.location.href.indexOf('auth/login') < 0) return;
        var inputs = document.querySelectorAll('input[type="text"][autocomplete="off"]');
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].setAttribute('autocomplete', 'username');
            if (!inputs[i].name) inputs[i].setAttribute('name', 'username');
        }
        var pwdInputs = document.querySelectorAll('input[type="password"][autocomplete="off"]');
        for (var j = 0; j < pwdInputs.length; j++) {
            pwdInputs[j].setAttribute('autocomplete', 'current-password');
            if (!pwdInputs[j].name) pwdInputs[j].setAttribute('name', 'password');
        }
        var forms = document.querySelectorAll('form[autocomplete="off"]');
        for (var k = 0; k < forms.length; k++) {
            forms[k].setAttribute('autocomplete', 'on');
        }
    }
    if (document.body) fixInputs();
    observer.observe(document.documentElement || document, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['autocomplete', 'type']
    });
    document.addEventListener('DOMContentLoaded', function() { fixInputs(); });
    setTimeout(fixInputs, 500);
    setTimeout(fixInputs, 1500);
    setTimeout(fixInputs, 3000);
    setTimeout(fixInputs, 5000);
})();
'@

function Wait-Cdp($Timeout = 15) {
    $start = Get-Date
    while (((Get-Date) - $start).TotalSeconds -lt $Timeout) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:$CdpPort/json/version" -TimeoutSec 2 -UseBasicParsing
            if ($r.StatusCode -eq 200) { return $true }
        } catch {}
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Inject-Fix {
    try {
        $pages = Invoke-WebRequest -Uri "http://localhost:$CdpPort/json" -UseBasicParsing | ConvertFrom-Json
        foreach ($page in $pages) {
            if ($page.type -ne "page") { continue }
            try {
                $ws = New-Object System.Net.WebSockets.ClientWebSocket
                $ct = [System.Threading.CancellationToken]::None
                $ws.ConnectAsync($page.webSocketDebuggerUrl, $ct).Wait()
                $msg = @{ id = 1; method = "Page.addScriptToEvaluateOnNewDocument"; params = @{ source = $FixScript } } | ConvertTo-Json -Compress
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)
                $seg = [System.ArraySegment[byte]]::new($bytes)
                $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
                Write-Host "[OK] Injected fix to page: $($page.url.Substring(0, [Math]::Min(60, $page.url.Length)))"
                $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "", $ct).Wait()
            } catch {}
        }
    } catch {
        Write-Warning "Inject failed: $_"
    }
}

Write-Host "Starting Quark browser..."
Start-Process -FilePath $QuarkExe -ArgumentList "--remote-debugging-port=$CdpPort", "--remote-allow-origins=*"
Write-Host "Waiting for browser..."
if (-not (Wait-Cdp)) { Write-Error "Browser start timeout"; exit 1 }
Write-Host "Browser started"
Start-Sleep -Seconds 2
Inject-Fix
Start-Sleep -Seconds 1
Write-Host "Opening Rancher login page..."
Start-Process -FilePath $QuarkExe -ArgumentList $Url
Write-Host "[Done] Quark started with fix injected. Click username field to see password suggestion."
