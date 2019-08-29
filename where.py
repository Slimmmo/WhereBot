import discord, json, os

from config import *

locations = None
locationLookup = None

client = discord.Client()

def locationMatches (loc):
	if loc in commonAbbrevs:
		return [ commonAbbrevs[loc] ]
	if loc in locationLookup:
		return [ loc ]
	locArr = loc.split(' ')
	if len(locArr) == 1:
		return [ s for s in locationLookup if locArr[0] in s ]
	elif len(locArr) > 1:
		matchArray = []
		for name in locationLookup:
			fullMatch = True
			for sub in locArr:
				if sub not in name:
					fullMatch = False
					break
			if fullMatch:
				matchArray.append(name)
		return matchArray

def msgAuthorThisBot (message):
	return message.author == client.user

def reloadData ():
	global locations, locationLookup
	locatedJSON = open('LocatedJSON.json')
	locations = json.load(locatedJSON)
	locationLookup = {}
	for key in locations:
		locationLookup[key.lower()] = key

async def parseMessage (message, beforeList = []):
	if '!where' in message.content:
		whereSplit = message.content.split('!where')
		for raw in whereSplit[1:]:
			matchingArray = locationMatches(raw.strip().lower())
			if len(matchingArray) == 1:
				if matchingArray[0] not in beforeList:
					found = locations[locationLookup[matchingArray[0]]]
					await message.channel.send('{}  http://maps.google.com/maps?q={},{}'.format(locationLookup[matchingArray[0]], found['lat'], found['lng']))
			elif len(matchingArray) > 1:
				messageText = 'Please edit your message and be more specific. Your search `{}` matched multiple stops; listed below.\n\n'.format(raw)
				for stop in matchingArray:
					messageText += locationLookup[stop] + '\n'
				await message.author.send(messageText)
			else:
				await message.author.send('Your search `{}` matched no stops.\nThink this is wrong? Message a mod.'.format(raw))

@client.event
async def on_message (message):
	if msgAuthorThisBot(message):
		return
	if '!whereload' in message.content:
		if reloadRole in [role.name for role in message.author.roles]:
			reloadData()
	else:
		await parseMessage(message)

@client.event
async def on_message_edit (before, after):
	if msgAuthorThisBot(after):
		return
	beforeList = []
	if '!where' in before.content:
		beforeSplit = before.content.split('!where')
		for loc in beforeSplit[1:]:
			matches = locationMatches(loc.strip().lower())
			if len(matches) == 1:
				beforeList.append(matches[0])
	await parseMessage(after, beforeList)

reloadData()
client.run(os.environ.get('discord_token'))
