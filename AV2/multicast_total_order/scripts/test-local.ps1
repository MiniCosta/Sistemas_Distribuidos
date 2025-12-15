# Script PowerShell para testar o sistema localmente
# Executa testes após iniciar os processos com run-local.ps1

param(
    [string]$Mode = "normal"  # "normal" ou "delay"
)

Write-Host "=========================================="
Write-Host "  TESTE: Multicast com Ordenacao Total   "
Write-Host "=========================================="

$P0 = "http://localhost:5000"
$P1 = "http://localhost:5001"
$P2 = "http://localhost:5002"

function Test-Endpoint {
    param([string]$Url)
    try {
        $response = Invoke-RestMethod -Uri "$Url/health" -TimeoutSec 2
        return $true
    } catch {
        return $false
    }
}

# Verifica se os processos estão rodando
Write-Host "`n Verificando processos..."
$p0Ok = Test-Endpoint $P0
$p1Ok = Test-Endpoint $P1
$p2Ok = Test-Endpoint $P2

if (-not ($p0Ok -and $p1Ok -and $p2Ok)) {
    Write-Host " ERRO: Nem todos os processos estao rodando!" -ForegroundColor Red
    Write-Host "  P0: $(if($p0Ok){'OK'}else{'OFFLINE'})"
    Write-Host "  P1: $(if($p1Ok){'OK'}else{'OFFLINE'})"
    Write-Host "  P2: $(if($p2Ok){'OK'}else{'OFFLINE'})"
    Write-Host "`nExecute primeiro: .\scripts\run-local.ps1"
    exit 1
}

Write-Host " Todos os processos estao online!" -ForegroundColor Green

# Status inicial
Write-Host "`n=========================================="
Write-Host "  STATUS INICIAL                         "
Write-Host "=========================================="

Write-Host "`nP0:"
(Invoke-RestMethod -Uri "$P0/status") | ConvertTo-Json -Depth 3

Write-Host "`nP1:"
(Invoke-RestMethod -Uri "$P1/status") | ConvertTo-Json -Depth 3

Write-Host "`nP2:"
(Invoke-RestMethod -Uri "$P2/status") | ConvertTo-Json -Depth 3

# Teste 1: Envio sequencial
Write-Host "`n=========================================="
Write-Host "  TESTE 1: Envio Sequencial              "
Write-Host "=========================================="

Write-Host "`n P0 envia 'Mensagem A'..."
$r0 = Invoke-RestMethod -Uri "$P0/send" -Method Post -ContentType "application/json" -Body '{"content": "Mensagem A"}'
Write-Host "  msg_id: $($r0.msg_id), timestamp: $($r0.timestamp)"
Start-Sleep -Seconds 2

Write-Host "`n P1 envia 'Mensagem B'..."
$r1 = Invoke-RestMethod -Uri "$P1/send" -Method Post -ContentType "application/json" -Body '{"content": "Mensagem B"}'
Write-Host "  msg_id: $($r1.msg_id), timestamp: $($r1.timestamp)"
Start-Sleep -Seconds 2

Write-Host "`n P2 envia 'Mensagem C'..."
$r2 = Invoke-RestMethod -Uri "$P2/send" -Method Post -ContentType "application/json" -Body '{"content": "Mensagem C"}'
Write-Host "  msg_id: $($r2.msg_id), timestamp: $($r2.timestamp)"
Start-Sleep -Seconds 2

# Verifica ordenação
Write-Host "`n=========================================="
Write-Host "  VERIFICANDO ORDENACAO                  "
Write-Host "=========================================="

Write-Host "`n Mensagens processadas por P0:"
$proc0 = Invoke-RestMethod -Uri "$P0/processed"
foreach ($msg in $proc0.processed) {
    Write-Host "  - $($msg.content) (ts=$($msg.timestamp), from=P$($msg.sender_id))"
}

Write-Host "`n Mensagens processadas por P1:"
$proc1 = Invoke-RestMethod -Uri "$P1/processed"
foreach ($msg in $proc1.processed) {
    Write-Host "  - $($msg.content) (ts=$($msg.timestamp), from=P$($msg.sender_id))"
}

Write-Host "`n Mensagens processadas por P2:"
$proc2 = Invoke-RestMethod -Uri "$P2/processed"
foreach ($msg in $proc2.processed) {
    Write-Host "  - $($msg.content) (ts=$($msg.timestamp), from=P$($msg.sender_id))"
}

# Verifica se a ordem é a mesma
$order0 = ($proc0.processed | ForEach-Object { $_.msg_id }) -join ","
$order1 = ($proc1.processed | ForEach-Object { $_.msg_id }) -join ","
$order2 = ($proc2.processed | ForEach-Object { $_.msg_id }) -join ","

Write-Host "`n=========================================="
if ($order0 -eq $order1 -and $order1 -eq $order2) {
    Write-Host "  ORDENACAO TOTAL VERIFICADA!" -ForegroundColor Green
    Write-Host "  Todos os processos processaram na mesma ordem."
} else {
    Write-Host "  ATENCAO: Ordens diferentes!" -ForegroundColor Yellow
    Write-Host "  P0: $order0"
    Write-Host "  P1: $order1"
    Write-Host "  P2: $order2"
}
Write-Host "=========================================="

# Teste 2: Envio simultâneo
Write-Host "`n=========================================="
Write-Host "  TESTE 2: Envio Simultaneo              "
Write-Host "=========================================="

Write-Host "`n Enviando 3 mensagens simultaneamente..."

$job0 = Start-Job -ScriptBlock { 
    Invoke-RestMethod -Uri "http://localhost:5000/send" -Method Post -ContentType "application/json" -Body '{"content": "Simultanea 0"}' 
}
$job1 = Start-Job -ScriptBlock { 
    Invoke-RestMethod -Uri "http://localhost:5001/send" -Method Post -ContentType "application/json" -Body '{"content": "Simultanea 1"}' 
}
$job2 = Start-Job -ScriptBlock { 
    Invoke-RestMethod -Uri "http://localhost:5002/send" -Method Post -ContentType "application/json" -Body '{"content": "Simultanea 2"}' 
}

Wait-Job $job0, $job1, $job2 | Out-Null
Write-Host " Mensagens enviadas!"

Start-Sleep -Seconds 3

Write-Host "`n Verificando ordenacao apos envio simultaneo..."

$proc0 = Invoke-RestMethod -Uri "$P0/processed"
$proc1 = Invoke-RestMethod -Uri "$P1/processed"
$proc2 = Invoke-RestMethod -Uri "$P2/processed"

Write-Host "`nP0 processou ${$proc0.processed.Count} mensagens"
Write-Host "P1 processou ${$proc1.processed.Count} mensagens"
Write-Host "P2 processou ${$proc2.processed.Count} mensagens"

Write-Host "`n=========================================="
Write-Host "  TESTE CONCLUIDO!                       "
Write-Host "=========================================="
