--[[
    HELIOS-9 V4 / LOCAL CINEMATICS
    StarterPlayer > StarterPlayerScripts > LocalScript

    NO HUD, countdown, prompts, phase text, ScreenGui or player UI.
    Crossfades THREE Roblox Creator Store score candidates as the physical
    reactor evolves. The server owns every machine, lever and timed event.
    If an asset is not permitted in your experience, Roblox may refuse to
    play it: replace the ID in the server CONFIG.AUDIO table, then Play.
]]

local Players=game:GetService("Players")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local Lighting=game:GetService("Lighting")
local RunService=game:GetService("RunService")
local TweenService=game:GetService("TweenService")
local SoundService=game:GetService("SoundService")
local StarterGui=game:GetService("StarterGui")
local player=Players.LocalPlayer
-- The reference is seen from inside the lab, not from behind an avatar
-- standing in the middle of the one clear sightline.
player.CameraMode=Enum.CameraMode.LockFirstPerson

-- Roblox's system menu/chat remain, but no game HUD covers the window.
task.spawn(function()
    for _=1,8 do
        local ok=pcall(function()
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Health,false)
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList,false)
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack,false)
        end)
        if ok then break end
        task.wait(0.55)
    end
end)
local remote=ReplicatedStorage:WaitForChild("HELIOS9_V4_CUES",30)
if not remote then
    warn("HELIOS-9 V4: RemoteEvent yok; V4 Server Script'ini etkinleştirin.")
    return
end

local scoreTracks={}
for i=1,2 do
    local name="HELIOS9_V4_ROBLOX_SCORE_"..i
    local previous=SoundService:FindFirstChild(name)
    if previous then previous:Destroy() end
    local s=Instance.new("Sound")
    s.Name=name
    s.Volume=0
    s.Looped=true -- Creator Store tracks can be shorter than a movement.
    s.Parent=SoundService
    scoreTracks[i]=s
end
local nextChannel=1
local musicVersion=0
local activeSound=nil
local pendingLoaded=nil
local pendingFades={}
local soundtrackActive=false
local escalation=0

local function cancelMusicTweens()
    for _,t in ipairs(pendingFades) do t:Cancel() end
    pendingFades={}
end
local function smoothVolume(sound,volume,seconds)
    local trackTween=TweenService:Create(sound,
        TweenInfo.new(seconds,Enum.EasingStyle.Sine,
            Enum.EasingDirection.InOut),{Volume=volume})
    trackTween:Play()
    pendingFades[#pendingFades+1]=trackTween
end
local function stopMusic()
    musicVersion=musicVersion+1
    local token=musicVersion
    soundtrackActive=false
    escalation=0
    cancelMusicTweens()
    if pendingLoaded then pendingLoaded:Disconnect();pendingLoaded=nil end
    for _,s in ipairs(scoreTracks) do smoothVolume(s,0,1.6) end
    task.delay(1.75,function()
        if token~=musicVersion then return end
        for _,s in ipairs(scoreTracks) do s:Stop() end
        activeSound=nil
    end)
end
local function playMovement(id,position,serverStamp,isTransition)
    if not id or id=="" then return end
    musicVersion=musicVersion+1
    local token=musicVersion
    soundtrackActive=true
    if not isTransition then escalation=1
    else escalation=math.min(3,escalation+1) end
    cancelMusicTweens()
    if pendingLoaded then pendingLoaded:Disconnect();pendingLoaded=nil end
    local outgoing=activeSound
    local incoming=scoreTracks[nextChannel]
    nextChannel=3-nextChannel
    if outgoing==incoming then outgoing=nil end
    incoming:Stop()
    incoming.SoundId=id
    incoming.Volume=0
    incoming.Looped=true
    local startAt=math.max(0,tonumber(position) or 0)
    local function seekWhenLoaded()
        if musicVersion~=token or not incoming.IsLoaded then return end
        local age=type(serverStamp)=="number" and math.max(0,
            workspace:GetServerTimeNow()-serverStamp) or 0
        local duration=incoming.TimeLength
        if duration>0.15 then
            incoming.TimePosition=(startAt+age)%duration
        end
    end
    incoming:Play()
    if incoming.IsLoaded then seekWhenLoaded()
    else
        pendingLoaded=incoming.Loaded:Connect(function()
            seekWhenLoaded()
            if pendingLoaded then pendingLoaded:Disconnect();pendingLoaded=nil end
        end)
    end
    activeSound=incoming
    local fadeSeconds=isTransition and 3.9 or 2.9
    smoothVolume(incoming,escalation>=3 and 0.73 or 0.61,fadeSeconds)
    if outgoing then
        smoothVolume(outgoing,0,fadeSeconds)
        task.delay(fadeSeconds+0.25,function()
            if musicVersion==token then outgoing:Stop() end
        end)
    end
end

local priorGrade=Lighting:FindFirstChild("HELIOS9_V4_LOCAL_FILM")
if priorGrade then priorGrade:Destroy() end
local grade=Instance.new("ColorCorrectionEffect")
grade.Name="HELIOS9_V4_LOCAL_FILM"
grade.Brightness=0
grade.Contrast=0
grade.Saturation=0
grade.TintColor=Color3.new(1,1,1)
grade.Parent=Lighting
local priorBlur=Lighting:FindFirstChild("HELIOS9_V4_LOCAL_BLUR")
if priorBlur then priorBlur:Destroy() end
local blur=Instance.new("BlurEffect")
blur.Name="HELIOS9_V4_LOCAL_BLUR"
blur.Size=0
blur.Parent=Lighting
local rng=Random.new()
local impulses={}
local clock=0
local colorToken=0

local function flash(power,hue)
    colorToken=colorToken+1
    local this=colorToken
    local strength=math.clamp(tonumber(power) or 0.2,0.05,1)
    local tint=hue=="red" and Color3.fromRGB(255,129,134)
        or hue=="orange" and Color3.fromRGB(255,194,128)
        or hue=="purple" and Color3.fromRGB(224,153,255)
        or hue=="ice" and Color3.fromRGB(173,241,255)
        or Color3.fromRGB(255,255,255)
    grade.TintColor=tint
    grade.Brightness=math.min(0.8,strength*0.68)
    grade.Contrast=math.min(0.52,strength*0.30)
    blur.Size=math.min(18,strength*12)
    TweenService:Create(grade,
        TweenInfo.new(strength>0.9 and 3.3 or 0.87,
            Enum.EasingStyle.Quad,Enum.EasingDirection.Out),
        {Brightness=0,Contrast=0,TintColor=Color3.new(1,1,1)}):Play()
    TweenService:Create(blur,
        TweenInfo.new(strength>0.9 and 3.8 or 1.0),{Size=0}):Play()
    task.delay(4.1,function()
        if colorToken==this then grade.Brightness=0;blur.Size=0 end
    end)
end

remote.OnClientEvent:Connect(function(kind,a,b,c,d)
    if kind=="MUSIC" then
        if a=="START" then
            playMovement(c,b,d,false)
        elseif a=="CROSSFADE" then
            playMovement(c,b,d,true)
        elseif a=="STOP" then
            stopMusic()
        end
    elseif kind=="TREMOR" then
        local force=math.clamp(tonumber(a) or 0.3,0,4)
        local seconds=math.clamp(tonumber(b) or 1,0.1,12)
        impulses[#impulses+1]={power=force,left=seconds,
            duration=seconds,phase=rng:NextNumber(0,100)}
        while #impulses>9 do table.remove(impulses,1) end
    elseif kind=="FLASH" then
        flash(a,b)
    elseif kind=="RESET" then
        stopMusic()
        impulses={}
        colorToken=colorToken+1
        grade.Brightness=0
        grade.Contrast=0
        grade.TintColor=Color3.new(1,1,1)
        blur.Size=0
    end
end)

RunService:BindToRenderStep("HELIOS9_V4_LOCAL_TREMORS",
    Enum.RenderPriority.Camera.Value+1,function(dt)
        clock=clock+dt
        local shake=0
        for i=#impulses,1,-1 do
            local entry=impulses[i]
            entry.left=entry.left-dt
            if entry.left<=0 then
                table.remove(impulses,i)
            else
                local decay=entry.left/entry.duration
                shake=shake+entry.power*decay*decay
            end
        end
        -- The core continuously throbs during the disaster, not just when
        -- a far-away pipe breaks. Slight enough not to interfere with walking.
        if soundtrackActive then
            shake=shake+0.06+escalation*0.022
        end
        if shake<0.015 then return end
        local cam=workspace.CurrentCamera
        if not cam then return end
        local distance=(cam.CFrame.Position-Vector3.new(0,54,0)).Magnitude
        local falloff=math.clamp(1-distance/490,0.31,1)
        local amount=math.min(2.35,shake)*falloff
        local x=math.noise(clock*19,0,0)*0.50*amount
        local y=math.noise(0,clock*21,0)*0.39*amount
        local z=math.noise(0,0,clock*16)*0.17*amount
        local yaw=math.rad(math.noise(clock*13,4.3,0)*1.2*amount)
        local pitch=math.rad(math.noise(clock*17,9.1,0)*0.7*amount)
        local roll=math.rad(math.noise(clock*15,1.7,0)*0.7*amount)
        cam.CFrame=cam.CFrame*CFrame.new(x,y,z)
            *CFrame.Angles(pitch,yaw,roll)
    end)

print("[HELIOS-9 V4] HUD yok; Roblox sesleri, kamera ve iki kanalli skor hazir.")
