from typing import List
from discord.ext import commands

import random
import requests
import json

from cogs.admin import Key
from datetime import datetime

i = 0

class API(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def get_hypixel(self, uuid, hypixel_key=None, data='player', id_tag='uuid'):


		#uuid can be data other than uuid in some cases
		global i
		i += 1
		i %= Key.key_index_len
		hypixel_key = Key.get_key(self, i)
		response =  None

		response = requests.get(f'https://api.hypixel.net/{data}?key={hypixel_key}&{id_tag}={uuid}')
		response = json.loads(response.text)

		return response

	def get_key_info(self, key):
		response = requests.get(f"https://api.hypixel.net/key?key={key}")
		response = json.loads(response.text)

		key_info = None
		
		if response['success'] == True:
			data = response['record']
			key_info = [data['key'], data['owner'], data['totalQueries'], data['queriesInPastMin'], data['limit']]
		else:
			key_info = [False, "Invalid API Key!", key]

		return key_info

	def get_namemc(self, user):
		return f"namemc.com/profile/{user}"

	def get_ign(self, uuid):
		response = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names")
		response = json.loads(response.text)
		try:
			ign = response[-1]['name']
		except:
			ign = '?'
		return ign
	
	def get_names(self, uuid) -> List:
		response = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names")
		response = json.loads(response.text)

		names = []
		names_len = len(response)

		while names_len >= 0:

			try:
				time_unix = int(response[names_len-1]['changedToAt'])
				
				timestamp = datetime.fromtimestamp(round(time_unix/1000,0))
				timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
			except:			#other line lenghts =
				timestamp = 'first:             '

			date_name = str(timestamp + ' - ' + response[names_len-1]['name'])

			names.append(date_name)
			names_len -= 1

		return names

	def get_uuid(self, ign):
		try:
			response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{ign}')
			response = json.loads(response.text)

			uuid = response['id']
			ign = response['name']
		except:
			return None
		return [uuid, ign]


	def get_guild(self, ign, guild_name = None):

		try: 
			uuid = API.get_uuid(self, ign)[0]
		except:
			return None

		if guild_name != None:
			g_uuid = API.get_hypixel(self, guild_name, data='findGuild', id_tag='byName')['guild']

			guild = API.get_hypixel(self, str(g_uuid), data='guild', id_tag='id')

			return guild
		else:

			g_uuid = API.get_hypixel(self, uuid, data='findGuild', id_tag='byUuid')

			guild_name = '?'

			if g_uuid['success'] == True:
				g_uuid = g_uuid['guild']

			guild = API.get_hypixel(self, g_uuid, data='guild', id_tag='id')

			if guild['success'] == True:
				guild_name = guild['guild']['name']

			return guild_name

def setup(bot):
    bot.add_cog(API(bot))

