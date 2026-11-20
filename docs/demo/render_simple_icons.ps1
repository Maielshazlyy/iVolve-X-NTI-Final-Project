param(
  [int]$CanvasSize = 384
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationCore, PresentationFramework, WindowsBase

$iconDirectory = Join-Path $PSScriptRoot 'assets\logos'
$outputDirectory = Join-Path $iconDirectory 'rasterized'
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null

$brandColors = @{
  ansible    = '#F4F4F4'
  docker     = '#2496ED'
  flask      = '#F4F4F4'
  github     = '#F4F4F4'
  jenkins    = '#D24939'
  kubernetes = '#326CE5'
  mysql      = '#4479A1'
  nodedotjs  = '#5FA04E'
  python     = '#FFD43B'
  springboot = '#6DB33F'
  terraform  = '#844FBA'
  trivy      = '#7B61FF'
}

foreach ($svgFile in Get-ChildItem -LiteralPath $iconDirectory -Filter '*.svg' -File) {
  [xml]$svg = Get-Content -LiteralPath $svgFile.FullName -Raw
  $root = $svg.DocumentElement
  $viewBox = @($root.GetAttribute('viewBox') -split '\s+' | ForEach-Object { [double]$_ })
  if ($viewBox.Count -ne 4) { throw "Missing SVG viewBox: $($svgFile.Name)" }
  $viewX, $viewY, $viewWidth, $viewHeight = $viewBox
  $scale = [Math]::Min(($CanvasSize - 44) / $viewWidth, ($CanvasSize - 44) / $viewHeight)
  $offsetX = ($CanvasSize - $viewWidth * $scale) / 2 - $viewX * $scale
  $offsetY = ($CanvasSize - $viewHeight * $scale) / 2 - $viewY * $scale
  $color = [System.Windows.Media.ColorConverter]::ConvertFromString($brandColors[$svgFile.BaseName])
  $brush = [System.Windows.Media.SolidColorBrush]::new($color)
  $visual = [System.Windows.Media.DrawingVisual]::new()
  $drawing = $visual.RenderOpen()
  $drawing.PushTransform([System.Windows.Media.MatrixTransform]::new($scale, 0, 0, $scale, $offsetX, $offsetY))

  foreach ($pathNode in $root.SelectNodes("//*[local-name()='path']")) {
    $pathData = $pathNode.GetAttribute('d')
    if (-not [string]::IsNullOrWhiteSpace($pathData)) {
      $geometry = [System.Windows.Media.Geometry]::Parse($pathData)
      $drawing.DrawGeometry($brush, $null, $geometry)
    }
  }

  $drawing.Pop()
  $drawing.Close()
  $bitmap = [System.Windows.Media.Imaging.RenderTargetBitmap]::new(
    $CanvasSize, $CanvasSize, 96, 96, [System.Windows.Media.PixelFormats]::Pbgra32
  )
  $bitmap.Render($visual)
  $encoder = [System.Windows.Media.Imaging.PngBitmapEncoder]::new()
  $encoder.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($bitmap))
  $outputPath = Join-Path $outputDirectory "$($svgFile.BaseName).png"
  $stream = [System.IO.File]::Open($outputPath, [System.IO.FileMode]::Create)
  try { $encoder.Save($stream) } finally { $stream.Dispose() }
  Write-Output "Rendered $($svgFile.BaseName)"
}
