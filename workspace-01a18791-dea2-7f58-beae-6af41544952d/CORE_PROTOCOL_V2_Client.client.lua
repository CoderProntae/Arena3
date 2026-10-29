-- CORE PROTOCOL V2 | CLIENT-ONLY FILM SCORE + CAMERA TREMOR
-- Install as a LocalScript in StarterPlayer > StarterPlayerScripts.
-- The server alone controls gameplay. This script adds NO permanent HUD.
local Players=game:GetService("Players")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local RunService=game:GetService("RunService")
local SoundService=game:GetService("SoundService")
local TweenService=game:GetService("TweenService")
local Workspace=game:GetService("Workspace")
local player=Players.LocalPlayer
local cues=ReplicatedStorage:WaitForChild("CORE_PROTOCOL_V2_CUES",60)
if not cues then
    warn("[CORE PROTOCOL] Server cue channel unavailable.")
    return
end

local gui=Instance.new("ScreenGui")
gui.Name="CORE_PROTOCOL_LENS_EFFECT_ONLY"
gui.IgnoreGuiInset=true
gui.ResetOnSpawn=false
gui.DisplayOrder=950
gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling
gui.Parent=player:WaitForChild("PlayerGui")
local flare=Instance.new("Frame")
flare.Name="EPHEMERAL_FILM_FLASH_NO_HUD"
flare.BorderSizePixel=0
flare.BackgroundTransparency=1
flare.BackgroundColor3=Color3.new(1,1,1)
flare.Size=UDim2.fromScale(1,1)
flare.Position=UDim2.fromScale(0,0)
flare.Parent=gui

local HUES={
    white=Color3.fromRGB(255,255,255),
    red=Color3.fromRGB(255,48,52),
    purple=Color3.fromRGB(198,91,255),
    ice=Color3.fromRGB(101,225,255),
}
local shakeEvents={}
local flashTween=nil
local activeScore=nil
local activeTween=nil
local soundSerial=0
local meltdownStartedAt=nil
local initialCamera=Workspace.CurrentCamera
local lastCameraFov=initialCamera and initialCamera.FieldOfView or 70
local function serverTime()
    return Workspace:GetServerTimeNow()
end
local function briefFlash(strength,hue)
    local alpha=math.clamp(tonumber(strength) or 0.3,0,1)
    if flashTween then flashTween:Cancel() end
    flare.BackgroundColor3=HUES[hue] or HUES.white
    flare.BackgroundTransparency=1-alpha*0.84
    local tweenInfo=TweenInfo.new(0.13+alpha*1.45,
        Enum.EasingStyle.Quart,Enum.EasingDirection.Out)
    flashTween=TweenService:Create(flare,tweenInfo,
        {BackgroundTransparency=1})
    flashTween:Play()
end
local function cueShake(strength,duration)
    local amount=math.clamp(tonumber(strength) or 0,0,4)
    local period=math.clamp(tonumber(duration) or 1,0.1,15)
    if amount<=0 then return end
    shakeEvents[#shakeEvents+1]={start=serverTime(),
        deadline=serverTime()+period,power=amount,duration=period}
    if #shakeEvents>18 then table.remove(shakeEvents,1) end
end
local function silenceScore()
    soundSerial=soundSerial+1
    if activeTween then activeTween:Cancel();activeTween=nil end
    if activeScore then
        local old=activeScore
        activeScore=nil
        TweenService:Create(old,TweenInfo.new(1.9,
            Enum.EasingStyle.Sine,Enum.EasingDirection.Out),
            {Volume=0}):Play()
        task.delay(2.1,function()
            if old.Parent then old:Destroy() end
        end)
    end
end
local function startScore(action,elapsed,id,stageStartedAt,roundStartedAt)
    if type(id)~="string" or not id:find("^rbxassetid://%d+$") then
        return
    end
    if type(roundStartedAt)=="number" then
        meltdownStartedAt=roundStartedAt
    elseif not meltdownStartedAt then
        meltdownStartedAt=serverTime()-(tonumber(elapsed) or 0)
    end
    if activeScore and activeScore.SoundId==id then return end
    soundSerial=soundSerial+1
    local serial=soundSerial
    local previous=activeScore
    local target=action=="START" and 0.28 or 0.32
    local music=Instance.new("Sound")
    music.Name="CORE_PROTOCOL_LOCAL_CINEMATIC_SCORE"
    music.SoundId=id
    music.Looped=true
    music.Volume=0
    music.PlaybackSpeed=1
    music.Parent=SoundService
    activeScore=music
    -- Roblox asset permissions depend on the OWNER of each experience.
    -- Mute/unavailable audio does NOT affect this independently modeled game.
    local function seek()
        if serial~=soundSerial or not music.Parent then return end
        local offset=math.max(0,serverTime()-(
            tonumber(stageStartedAt) or serverTime()))
        local length=music.TimeLength
        if length>0 then offset=offset%length end
        music.TimePosition=offset
    end
    if music.IsLoaded then seek()
    else
        music.Loaded:Connect(function()
            if serial==soundSerial then seek() end
        end)
    end
    music:Play()
    if music.IsLoaded then seek() end
    activeTween=TweenService:Create(music,
        TweenInfo.new(previous and 3.1 or 1.9,
            Enum.EasingStyle.Sine,Enum.EasingDirection.Out),
        {Volume=target})
    activeTween:Play()
    if previous then
        TweenService:Create(previous,TweenInfo.new(3.2,
            Enum.EasingStyle.Sine,Enum.EasingDirection.Out),
            {Volume=0}):Play()
        task.delay(3.4,function()
            if previous.Parent then previous:Destroy() end
        end)
    end
end
local function resetFilm()
    meltdownStartedAt=nil
    shakeEvents={}
    if flashTween then flashTween:Cancel();flashTween=nil end
    flare.BackgroundTransparency=1
    silenceScore()
    local camera=Workspace.CurrentCamera
    if camera then camera.FieldOfView=lastCameraFov end
end

cues.OnClientEvent:Connect(function(command,a,b,c,d,e)
    if command=="SHAKE" then
        cueShake(a,b)
    elseif command=="FLASH" then
        briefFlash(a,b)
    elseif command=="RESET" then
        resetFilm()
    elseif command=="MUSIC" then
        if a=="STOP" then
            -- A success/failed-startup/reset immediately ends camera tremor.
            meltdownStartedAt=nil
            silenceScore()
        elseif a=="START" or a=="CROSSFADE" then
            startScore(a,b,c,d,e)
        end
    end
end)

local noiseSeed=player.UserId%997
local renderTag="CORE_PROTOCOL_PHYSICAL_CAMERA"
pcall(function() RunService:UnbindFromRenderStep(renderTag) end)
RunService:BindToRenderStep(renderTag,
    Enum.RenderPriority.Camera.Value+1,function(dt)
    local camera=Workspace.CurrentCamera
    if not camera then return end
    local t=serverTime()
    local impulse=0
    for i=#shakeEvents,1,-1 do
        local event=shakeEvents[i]
        if t>=event.deadline then table.remove(shakeEvents,i)
        else
            local remaining=(event.deadline-t)/event.duration
            impulse=impulse+event.power*remaining*remaining
        end
    end
    local continuous=0
    if meltdownStartedAt then
        local age=math.max(0,t-meltdownStartedAt)
        local panic=math.clamp((age-85)/350,0,1)
        continuous=0.025+panic*0.16
        if age>=420 and age<=440 then
            continuous=continuous+0.24
        end
    end
    local intensity=math.min(4,impulse+continuous)
    if intensity>0.006 then
        local x=math.noise(t*12.1,noiseSeed,0)*intensity*0.72
        local y=math.noise(t*14.9,noiseSeed+17,0)*intensity*0.52
        local z=math.noise(t*10.2,noiseSeed+39,0)*intensity*0.31
        local pitch=math.noise(t*11.1,noiseSeed+58,0)
            *math.rad(1.8)*intensity
        local yaw=math.noise(t*9.2,noiseSeed+74,0)
            *math.rad(1.45)*intensity
        local roll=math.noise(t*8.1,noiseSeed+81,0)
            *math.rad(1.9)*intensity
        -- Apply AFTER Roblox's ordinary camera controller each frame;
        -- no permanent CFrame change accumulates across rendered frames.
        camera.CFrame=camera.CFrame*CFrame.new(x,y,z)
            *CFrame.Angles(pitch,yaw,roll)
        camera.FieldOfView=lastCameraFov+
            math.min(7,intensity*2.15)
    else
        if math.abs(camera.FieldOfView-lastCameraFov)>0.03 then
            camera.FieldOfView=camera.FieldOfView+
                (lastCameraFov-camera.FieldOfView)*
                math.min(1,dt*8)
        end
    end
end)

-- Ask for the CURRENT act on late join. The server accepts this command
-- only; client cannot change any reactor state, room damage, or inventory.
cues:FireServer("SYNC")
print("[CORE PROTOCOL V2] Film client active; reactor remains server-authoritative.")
