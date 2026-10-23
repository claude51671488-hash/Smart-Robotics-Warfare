param([string]$Source=(Join-Path (Split-Path -Parent $PSScriptRoot) 'art-source/engineering-rig'))
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$target=Join-Path (Split-Path -Parent $PSScriptRoot) 'ui/textures/engineering/rig'
New-Item -ItemType Directory -Path $target -Force | Out-Null
# Mechanical sprite assembly: all painted parts come from ImageGen. No frame
# redraws: every frame uses the same parts and smooth, repeatable transforms.
function Cut($sheet,$r) {
 $b=$sheet.Clone([Drawing.Rectangle]::new($r[0],$r[1],$r[2],$r[3]),[Drawing.Imaging.PixelFormat]::Format32bppArgb)
 $l=$b.Width;$t=$b.Height;$rr=-1;$bb=-1
 for($y=0;$y -lt $b.Height;$y++){for($x=0;$x -lt $b.Width;$x++){if($b.GetPixel($x,$y).A -gt 32){$l=[math]::Min($l,$x);$t=[math]::Min($t,$y);$rr=[math]::Max($rr,$x);$bb=[math]::Max($bb,$y)}}}
 if($rr -lt 0){throw 'Empty rig component'}
 $out=$b.Clone([Drawing.Rectangle]::new($l,$t,$rr-$l+1,$bb-$t+1),[Drawing.Imaging.PixelFormat]::Format32bppArgb);$b.Dispose();return $out
}
function Canvas {return [Drawing.Bitmap]::new(1536,512,[Drawing.Imaging.PixelFormat]::Format32bppArgb)}
function DrawPart($canvas,$part,$x,$y,$width) {
 $g=[Drawing.Graphics]::FromImage($canvas);$g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
 $g.DrawImage($part,[Drawing.RectangleF]::new($x,$y,$width,($part.Height*$width/$part.Width)));$g.Dispose()
}
function SaveBoth($bitmap,$name,$flip) {
 $bitmap.Save((Join-Path $target ($name+'.png')),[Drawing.Imaging.ImageFormat]::Png)
 $bitmap.RotateFlip($flip)
 $bitmap.Save((Join-Path $target ($name+'_left.png')),[Drawing.Imaging.ImageFormat]::Png)
 $bitmap.Dispose()
}
function Ease($t){$t=[math]::Clamp([double]$t,0.0,1.0);return $t*$t*(3-2*$t)}
$metadata=@{}
$heads=[Drawing.Bitmap]::FromFile((Join-Path $Source 'turret-heads-final.png'))
$shield=[Drawing.Bitmap]::FromFile((Join-Path $Source 'machinegun-shield.png'))
foreach($kind in @('cannon','machinegun')) {
 $sheet=[Drawing.Bitmap]::FromFile((Join-Path $Source ($kind+'-parts.png')))
 $rects=if($kind -eq 'cannon'){@(@(0,100,620,320),@(620,140,916,240),@(130,460,350,205),@(690,510,810,135),@(100,735,530,210),@(790,710,690,300))}else{@(@(50,130,600,310),@(640,125,860,275),@(170,475,400,285),@(900,475,405,285),@(270,810,300,165),@(950,780,330,230))}
 $parts=@();foreach($r in $rects){$parts+=Cut $sheet $r};$sheet.Dispose()
 $footX=if($kind -eq 'cannon'){510.}else{369.}
 # Preserve the low foot of the reference rather than the open U-shaped rig.
 $stripY=[int]($parts[0].Height*.84)
 $pedestal=$parts[0].Clone([Drawing.Rectangle]::new(0,$stripY,$parts[0].Width,$parts[0].Height-$stripY),[Drawing.Imaging.PixelFormat]::Format32bppArgb)
 $baseWidth=420.;$baseX=$footX-$baseWidth/2;$baseH=$pedestal.Height*$baseWidth/$pedestal.Width
 $armour=if($kind -eq 'cannon'){Cut $heads @(0,0,1050,803)}else{Cut $shield @(0,0,$shield.Width,$shield.Height)}
 $armourWidth=if($kind -eq 'cannon'){430.}else{330.}
 $axleX=if($kind -eq 'cannon'){.985}else{.15}
 $axleY=if($kind -eq 'cannon'){.7}else{.38}
 $armourHeight=$armour.Height*$armourWidth/$armour.Width
 $armourX=$footX-$armourWidth/2;$armourY=480.-$baseH-$armourHeight+2
 $jointX=$armourX+$armourWidth*$axleX;$jointY=$armourY+$armourHeight*$axleY
 $barrelWidth=720.;$barrelHeight=$parts[1].Height*$barrelWidth/$parts[1].Width
 $axisRatio=if($kind -eq 'cannon'){.40}else{.50}
 # Hide the breech behind the stationary housing; only the gun traverses.
 $barrelX=$jointX-$(if($kind -eq 'cannon'){160.}else{56.});$barrelY=$jointY-$barrelHeight*$axisRatio
 $base=Canvas;DrawPart $base $pedestal $baseX (480-$baseH) $baseWidth
 $pedestal.Dispose()
 SaveBoth $base ($kind+'_base') ([Drawing.RotateFlipType]::RotateNoneFlipX)
 # The entire armoured housing remains on the fixed base.
 $head=Canvas
 DrawPart $head $armour $armourX $armourY $armourWidth
 SaveBoth $head ($kind+'_head') ([Drawing.RotateFlipType]::RotateNoneFlipX)
 $armour.Dispose()
 $barrel=Canvas;DrawPart $barrel $parts[1] $barrelX $barrelY $barrelWidth
 SaveBoth $barrel ($kind+'_barrel') ([Drawing.RotateFlipType]::RotateNoneFlipY)
 $muzzleX=$barrelX+$barrelWidth-12
 $muzzleY=$barrelY+$barrelHeight*$axisRatio
 for($i=0;$i -lt 48;$i++) {
  $t=$i/47.;$c=Canvas
  if($kind -eq 'cannon') {
   # Hatch opens, a round slides smoothly into the breech, rammer follows,
   # retracts and hatch closes. The mounting geometry never changes.
   $open=(Ease ($t/.18))*(1-(Ease (($t-.78)/.22)))
   if($t -gt .12 -and $t -lt .69) {
    $feed=Ease (($t-.18)/.43)
    DrawPart $c $parts[4] ($footX-230+165*$feed) ($jointY-78) 150
   }
   if($t -gt .20 -and $t -lt .84) {
    $push=(Ease (($t-.25)/.34))*(1-(Ease (($t-.62)/.2)))
    DrawPart $c $parts[3] ($footX-320+180*$push) ($jointY-48) 245
   }
   DrawPart $c $parts[2] ($footX-64) ($jointY-80-54*$open) 82
  } else {
   $open=(Ease ($t/.2))*(1-(Ease (($t-.8)/.2)))
   $feed=Ease (($t-.2)/.55)
   DrawPart $c $parts[3] ($jointX-44+30*$feed) ($jointY-96+34*$feed) 72
   DrawPart $c $parts[2] ($jointX+3) ($jointY-82-30*$open) 68
  }
  $loadFlip=if($kind -eq 'cannon'){[Drawing.RotateFlipType]::RotateNoneFlipX}else{[Drawing.RotateFlipType]::RotateNoneFlipY}
  SaveBoth $c ('{0}_load_{1:00}' -f $kind,($i+1)) $loadFlip
 }
 # Store an isolated flash for the effect at the real barrel hardpoint.
 $parts[5].Save((Join-Path $target ($kind+'_flash.png')),[Drawing.Imaging.ImageFormat]::Png)
 $metadata[$kind]=@{Width=1536;Height=512;FootX=$footX;FootY=480;JointX=$jointX;JointY=$jointY;MuzzleX=$muzzleX;MuzzleY=$muzzleY;Scale=$(if($kind -eq 'cannon'){.52}else{.25});LoadingFrames=48}
 foreach($part in $parts){$part.Dispose()}
}
$heads.Dispose()
$shield.Dispose()
# Bullet rendering uses the native bullet sprite route, not the composite actor
# used by cannon rounds. Resize the approved artwork; preserve its alpha.
$tracer=[Drawing.Bitmap]::FromFile((Join-Path (Split-Path $target) 'animated/tracer.png'))
$bullet=[Drawing.Bitmap]::new(59,[int][math]::Round(59*$tracer.Height/$tracer.Width),[Drawing.Imaging.PixelFormat]::Format32bppArgb)
$bg=[Drawing.Graphics]::FromImage($bullet);$bg.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$bg.DrawImage($tracer,0,0,$bullet.Width,$bullet.Height);$bg.Dispose();$tracer.Dispose()
$bullet.Save((Join-Path $target 'bullet.png'),[Drawing.Imaging.ImageFormat]::Png);$bullet.Dispose()
$empty=Canvas;$empty.Save((Join-Path $target 'empty.png'),[Drawing.Imaging.ImageFormat]::Png);$empty.Dispose()
$metadata|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $target 'geometry.json') -Encoding utf8
$lua='SRWBunkerRigGeometry={'
foreach($kind in @('cannon','machinegun')){$v=$metadata[$kind];$lua+=$kind+'={';foreach($key in $v.Keys){$lua+=$key+'='+([Convert]::ToString($v[$key],[Globalization.CultureInfo]::InvariantCulture))+','};$lua+='},'}
$lua+='}'
[IO.File]::WriteAllText((Join-Path $target 'geometry.lua'),$lua,[Text.UTF8Encoding]::new($false))
$metadata|ConvertTo-Json -Depth 4
