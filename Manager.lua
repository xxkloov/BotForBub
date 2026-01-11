local HttpService = game:GetService("HttpService")
local Remotes = game.ReplicatedStorage:WaitForChild("Remotes")
local ReportPlayer = Remotes:WaitForChild("ReportPlayer")

local DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"
local BOT_SERVER_URL = "http://localhost:5000/report"

ReportPlayer.OnServerEvent:Connect(function(plr, targetplruserid, reasontxt)
	if not plr or not targetplruserid or not reasontxt then
		return
	end
	
	local targetPlayer = game.Players:GetPlayerByUserId(targetplruserid)
	if not targetPlayer then
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
		reason = reasontxt,
		timestamp = os.time(),
		serverId = game.JobId,
		placeId = game.PlaceId
	}
	
	local success, response = pcall(function()
		return HttpService:PostAsync(BOT_SERVER_URL, HttpService:JSONEncode(reportData), Enum.HttpContentType.ApplicationJson)
	end)
	
	if not success then
		warn("[Manager] Failed to send report to Discord bot:", response)
	end
end)