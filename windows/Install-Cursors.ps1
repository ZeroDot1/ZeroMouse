param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Install', 'Uninstall')]
    [string] $Mode,

    [Parameter(Mandatory = $true)]
    [string] $CursorDir,

    [Parameter(Mandatory = $true)]
    [string] $BackupPath
)

$ErrorActionPreference = 'Stop'
$registryPath = 'Control Panel\Cursors'
$cursorFiles = [ordered]@{
    Arrow       = 'arrow.cur'
    Help        = 'help.cur'
    AppStarting = 'appstarting.ani'
    Wait        = 'wait.ani'
    Crosshair   = 'crosshair.cur'
    IBeam       = 'ibeam.cur'
    NWPen       = 'pencil.cur'
    No          = 'not-allowed.cur'
    SizeNS      = 'size-ns.cur'
    SizeWE      = 'size-we.cur'
    SizeNWSE    = 'size-nwse.cur'
    SizeNESW    = 'size-nesw.cur'
    SizeAll     = 'move.cur'
    UpArrow     = 'up-arrow.cur'
    Hand        = 'hand.cur'
}

function Send-CursorRefresh {
    if (-not ('ZeroMouse.CursorRefresh' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace ZeroMouse {
    public static class CursorRefresh {
        [DllImport("user32.dll", SetLastError=true)]
        public static extern bool SystemParametersInfo(uint action, uint param,
            IntPtr value, uint flags);
        [DllImport("user32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
        public static extern IntPtr SendMessageTimeout(IntPtr window, uint message,
            UIntPtr wParam, string lParam, uint flags, uint timeout, out UIntPtr result);
    }
}
'@
    }

    [UIntPtr] $result = [UIntPtr]::Zero
    [void][ZeroMouse.CursorRefresh]::SystemParametersInfo(0x0057, 0, [IntPtr]::Zero, 0x0002)
    [void][ZeroMouse.CursorRefresh]::SendMessageTimeout(
        [IntPtr] 0xffff, 0x001A, [UIntPtr]::Zero,
        'Control Panel\Cursors', 0x0002, 5000, [ref] $result
    )
}

$key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($registryPath, $true)
if ($null -eq $key) {
    $key = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($registryPath)
}

try {
    if ($Mode -eq 'Install') {
        foreach ($file in $cursorFiles.Values) {
            $path = Join-Path $CursorDir $file
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                throw "Required cursor file is missing: $path"
            }
        }

        if (-not (Test-Path -LiteralPath $BackupPath -PathType Leaf)) {
            $valuesToSave = @($cursorFiles.Keys) + @('Scheme Source')
            $snapshot = foreach ($name in $valuesToSave) {
                if ($key.GetValueNames() -contains $name) {
                    [pscustomobject]@{
                        Name = $name
                        Present = $true
                        Kind = $key.GetValueKind($name).ToString()
                        Value = $key.GetValue(
                            $name, $null,
                            [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames
                        )
                    }
                } else {
                    [pscustomobject]@{ Name = $name; Present = $false; Kind = $null; Value = $null }
                }
            }
            $parent = Split-Path -Parent $BackupPath
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
            ConvertTo-Json -InputObject @($snapshot) -Depth 5 |
                Set-Content -LiteralPath $BackupPath -Encoding UTF8
        }

        foreach ($name in $cursorFiles.Keys) {
            $path = (Join-Path $CursorDir $cursorFiles[$name])
            $key.SetValue($name, $path, [Microsoft.Win32.RegistryValueKind]::String)
        }
        $key.SetValue('Scheme Source', 1, [Microsoft.Win32.RegistryValueKind]::DWord)
        Send-CursorRefresh
        Write-Output 'ZeroMouse cursors are installed for the current Windows user.'
    } else {
        if (Test-Path -LiteralPath $BackupPath -PathType Leaf) {
            $snapshot = Get-Content -LiteralPath $BackupPath -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($entry in $snapshot) {
                if ($entry.Present) {
                    $kind = [Enum]::Parse([Microsoft.Win32.RegistryValueKind], [string]$entry.Kind)
                    $value = $entry.Value
                    if ($kind -eq [Microsoft.Win32.RegistryValueKind]::DWord) {
                        $value = [int]$value
                    } elseif ($kind -eq [Microsoft.Win32.RegistryValueKind]::QWord) {
                        $value = [long]$value
                    } elseif ($kind -eq [Microsoft.Win32.RegistryValueKind]::MultiString) {
                        $value = [string[]]$value
                    } elseif ($kind -eq [Microsoft.Win32.RegistryValueKind]::Binary) {
                        $value = [byte[]]$value
                    }
                    $key.SetValue($entry.Name, $value, $kind)
                } else {
                    $key.DeleteValue($entry.Name, $false)
                }
            }
            Send-CursorRefresh
            Write-Output 'The previous Windows cursor settings have been restored.'
        } else {
            Write-Warning 'No cursor backup was found; Windows cursor settings were left unchanged.'
        }
    }
} finally {
    if ($null -ne $key) { $key.Dispose() }
}
