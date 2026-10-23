-- Native rendering owns fixed bases, elevation, smooth recoil and reload.
-- Only a bounded counter is saved for native gameplay diagnostics.
function SRW.EngineeringShot(weaponId)
 local part=data.srw and data.srw.MountedWeapons[weaponId]
 if part and (part.Kind=="srw_bunker_cannon" or part.Kind=="srw_bunker_machinegun") then
  part.ArtShotSerial=(part.ArtShotSerial or 0)+1
 end
end
