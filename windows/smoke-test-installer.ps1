$ErrorActionPreference = 'Stop'

$registryPath = 'HKCU:\Control Panel\Cursors'
$cursorNames = @(
    'Arrow', 'Help', 'AppStarting', 'Wait', 'Crosshair', 'IBeam', 'NWPen',
    'No', 'SizeNS', 'SizeWE', 'SizeNWSE', 'SizeNESW', 'SizeAll', 'UpArrow',
    'Hand', 'Scheme Source'
)
$expectedFiles = [ordered]@{
    Arrow = 'arrow.cur'
    Help = 'help.cur'
    AppStarting = 'appstarting.ani'
    Wait = 'wait.ani'
    Crosshair = 'crosshair.cur'
    IBeam = 'ibeam.cur'
    NWPen = 'pencil.cur'
    No = 'not-allowed.cur'
    SizeNS = 'size-ns.cur'
    SizeWE = 'size-we.cur'
    SizeNWSE = 'size-nwse.cur'
    SizeNESW = 'size-nesw.cur'
    SizeAll = 'move.cur'
    UpArrow = 'up-arrow.cur'
    Hand = 'hand.cur'
}

function Get-CursorSnapshot {
    $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
    $values = [ordered]@{}
    try {
        foreach ($name in $cursorNames) {
            if ($null -ne $key -and $key.GetValueNames() -contains $name) {
                $kind = $key.GetValueKind($name).ToString()
                $value = $key.GetValue(
                    $name, $null,
                    [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames
                )
                $values[$name] = [pscustomobject][ordered]@{
                    Present = $true
                    Kind = $kind
                    Value = $value
                }
            } else {
                $values[$name] = [pscustomobject][ordered]@{
                    Present = $false
                    Kind = $null
                    Value = $null
                }
            }
        }
    } finally {
        if ($null -ne $key) { $key.Dispose() }
    }
    ConvertTo-Json -InputObject $values -Depth 5 -Compress
}

$before = Get-CursorSnapshot
$installer = (Get-ChildItem 'dist/windows/ZeroMouse-Setup-*.exe' |
    Select-Object -First 1).FullName
$cursorDir = Join-Path $env:LOCALAPPDATA 'ZeroMouse\Cursors'
$uninstaller = Join-Path $env:LOCALAPPDATA 'ZeroMouse\unins000.exe'

try {
    $setup = Start-Process -FilePath $installer -ArgumentList @(
        '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-'
    ) -Wait -PassThru
    if ($setup.ExitCode -ne 0) { throw "Installer exited with code $($setup.ExitCode)." }

    foreach ($name in $expectedFiles.Keys) {
        $expectedPath = Join-Path $cursorDir $expectedFiles[$name]
        $actualPath = (Get-ItemProperty -LiteralPath $registryPath -Name $name).$name
        if ($actualPath -ine $expectedPath -or -not (Test-Path -LiteralPath $expectedPath)) {
            throw "Cursor role '$name' was not installed correctly."
        }
    }

    if (-not (Test-Path -LiteralPath $uninstaller)) {
        throw 'Uninstaller was not installed.'
    }
} finally {
    if (Test-Path -LiteralPath $uninstaller) {
        $uninstall = Start-Process -FilePath $uninstaller -ArgumentList @(
            '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'
        ) -Wait -PassThru
        if ($uninstall.ExitCode -ne 0) {
            throw "Uninstaller exited with code $($uninstall.ExitCode)."
        }
    }
}

if ((Get-CursorSnapshot) -cne $before) {
    throw 'The uninstaller did not restore the original Windows cursor settings.'
}
Write-Output 'Installer assigned all cursor roles and the uninstaller restored the previous settings.'
