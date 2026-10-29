-- Server-side API: only attach a user-supplied / rights-cleared Roblox audio asset.
-- A track is played by the same replicated Sound that carries TrackTitle.
local RadioPlayer={}
function RadioPlayer.play(sound,assetId,title,volume)
 assert(sound and sound:IsA('Sound'),'sound must be Sound')
 local id=tostring(assetId or ''):match('^(%d+)$') or tostring(assetId or ''):match('^rbxassetid://(%d+)$')
 assert(id and #id<=20,'numeric Roblox audio asset ID required')
 assert(type(title)=='string' and title:match('%S'),'non-empty track title required')
 local safe=title:gsub('[%c]',' ');local cut=utf8.offset(safe,181);if cut then safe=string.sub(safe,1,cut-1) end
 sound:Stop();sound:SetAttribute('TrackTitle',safe);sound.SoundId='rbxassetid://'..id;sound.Volume=math.clamp(tonumber(volume) or .35,0,1);sound:Play()
end
function RadioPlayer.stop(sound)
 assert(sound and sound:IsA('Sound'),'sound must be Sound');sound:Stop()
end
return RadioPlayer
