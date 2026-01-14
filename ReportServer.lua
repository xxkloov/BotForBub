local HttpService = game:GetService("HttpService")
local Remotes = game.ReplicatedStorage:WaitForChild("Events")
local ReportPlayer = Remotes:WaitForChild("ReportPlayer")

local DISCORD_WEBHOOK_URL = ""
local BOT_SERVER_URL = "https://botforbub.onrender.com/report"
local Testing = false
local API_KEY = ""

local ALLOWED_ABUSE_TYPES = {
	["Exploiting"] = true,
	["Bug Abuse"] = true,
	["Adult Content"] = true,
	["Inappropriate Avatar"] = true,
	["Discrimination / Slurs"] = true,
	["Other"] = true,
	["Spam / Flood"] = true,
	["Roblox Guidlines"] = true
}

local REQUEST_TIMEOUT = 10
local MAX_RETRIES = 3
local RETRY_DELAY_BASE = 1

local function isValidAbuseType(abuseType)
	return abuseType and type(abuseType) == "string" and ALLOWED_ABUSE_TYPES[abuseType] == true
end

local function validatePlayerData(plr)
	if not plr or not plr.Parent then
		return false, "Reporter player is invalid"
	end
	if not plr.UserId or plr.UserId <= 0 then
		return false, "Reporter user ID is invalid"
	end
	if not plr.Name or plr.Name == "" then
		return false, "Reporter name is invalid"
	end
	return true, nil
end

local function sendRequestWithRetry(url, data, maxRetries)
	maxRetries = maxRetries or MAX_RETRIES
	local attempt = 0
	
	while attempt < maxRetries do
		local success, response = pcall(function()
			local options = {
				Url = url,
				Method = "POST",
				Headers = {
					["Content-Type"] = "application/json"
				},
				Body = HttpService:JSONEncode(data)
			}
			
			if API_KEY and API_KEY ~= "" then
				options.Headers["X-API-Key"] = API_KEY
			end
			
			return HttpService:RequestAsync(options)
		end)
		
		if success then
			if response.Success then
				local responseData = {}
				local decodeSuccess, decoded = pcall(function()
					return HttpService:JSONDecode(response.Body)
				end)
				
				if decodeSuccess and decoded then
					responseData = decoded
				end
				
				return true, responseData, response.StatusCode
			else
				if response.StatusCode == 429 then
					local retryAfter = 5
					if response.Headers and response.Headers["Retry-After"] then
						retryAfter = tonumber(response.Headers["Retry-After"]) or 5
					end
					attempt = attempt + 1
					if attempt < maxRetries then
						task.wait(retryAfter)
						continue
					end
				end
				
				return false, string.format("HTTP %d: %s", response.StatusCode, response.Body or "Unknown error"), response.StatusCode
			end
		else
			attempt = attempt + 1
			if attempt < maxRetries then
				local delay = RETRY_DELAY_BASE * (2 ^ (attempt - 1))
				task.wait(delay)
			else
				return false, response, nil
			end
		end
	end
	
	return false, "Max retries exceeded", nil
end

local function sendTestMessage()
	local testData = {
		reporter = {
			name = "Test1",
			displayName = "Unknown1",
			userId = 1,
			thumbnail = "https://www.roblox.com/headshot-thumbnail/image?userId=1&width=420&height=420&format=png",
			profileUrl = "https://www.roblox.com/users/1/profile"
		},
		reported = {
			name = "Test2",
			displayName = "Unknown2",
			userId = 2,
			thumbnail = "https://www.roblox.com/headshot-thumbnail/image?userId=2&width=420&height=420&format=png",
			profileUrl = "https://www.roblox.com/users/2/profile"
		},
		abuseType = "Exploiting",
		additionalInfo = "This is a test message to verify the report system is working correctly.",
		timestamp = os.time(),
		serverId = game.JobId,
		placeId = game.PlaceId
	}

	local success, response, statusCode = sendRequestWithRetry(BOT_SERVER_URL, testData)

	if success then
		print("[ReportServer] Test message sent successfully")
	else
		warn("[ReportServer] Failed to send test message:", response, statusCode and "Status: " .. statusCode or "")
	end
end

if Testing then
	task.spawn(function()
		while Testing do
			sendTestMessage()
			task.wait(60)
		end
	end)
end

local cd = {}

ReportPlayer.OnServerEvent:Connect(function(plr, targetplruserid, additionalInfo, abuseType)
	if not plr or not targetplruserid or not abuseType or cd[plr.UserId] == true then
		return
	end
	
	if not isValidAbuseType(abuseType) then
		warn("[ReportServer] Invalid abuse type from player", plr.UserId, ":", abuseType)
		return
	end
	
	local isValid, errorMsg = validatePlayerData(plr)
	if not isValid then
		warn("[ReportServer] Invalid reporter data:", errorMsg)
		return
	end
	
	cd[plr.UserId] = true
	task.delay(35, function()
		cd[plr.UserId] = false
	end)
	
	local targetPlayer = game.Players:GetPlayerByUserId(targetplruserid)
	if not targetPlayer then
		warn("[ReportServer] Target player not found:", targetplruserid)
		return
	end
	
	local isValidTarget, targetErrorMsg = validatePlayerData(targetPlayer)
	if not isValidTarget then
		warn("[ReportServer] Invalid target player data:", targetErrorMsg)
		return
	end

	local reporterName = plr.Name
	local reporterId = plr.UserId
	local reporterDisplayName = plr.DisplayName

	local reportedName = targetPlayer.Name
	local reportedId = targetPlayer.UserId
	local reportedDisplayName = targetPlayer.DisplayName

	local reporterThumbnail = string.format("https://www.roblox.com/headshot-thumbnail/image?userId=%d&width=420&height=420&format=png", reporterId)
	local reportedThumbnail = string.format("https://www.roblox.com/headshot-thumbnail/image?userId=%d&width=420&height=420&format=png", reportedId)

	local reportData = {
		reporter = {
			name = reporterName,
			displayName = reporterDisplayName,
			userId = reporterId,
			thumbnail = reporterThumbnail,
			profileUrl = string.format("https://www.roblox.com/users/%d/profile", reporterId)
		},
		reported = {
			name = reportedName,
			displayName = reportedDisplayName,
			userId = reportedId,
			thumbnail = reportedThumbnail,
			profileUrl = string.format("https://www.roblox.com/users/%d/profile", reportedId)
		},
		abuseType = abuseType,
		additionalInfo = additionalInfo or "",
		timestamp = os.time(),
		serverId = game.JobId,
		placeId = game.PlaceId
	}

	task.spawn(function()
		local success, response, statusCode = sendRequestWithRetry(BOT_SERVER_URL, reportData)

		if success then
			print("[ReportServer] Report sent successfully for player", reportedId, "by", reporterId)
		else
			warn("[ReportServer] Failed to send report to Discord bot:", response, statusCode and "Status: " .. statusCode or "")
		end
	end)
end)