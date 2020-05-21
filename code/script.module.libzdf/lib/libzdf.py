#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from datetime import date, timedelta
import xbmc
import xbmcgui
import xbmcaddon
import libzdfneu
import libzdfjsonparser as libZdfJsonParser
import libmediathek3 as libMediathek


channels = ('ZDF','ZDFinfo','ZDFneo')

def list():
	show_hint_mobile = libMediathek.getSettingBool('show_hint_mobile')
	if show_hint_mobile:
		libMediathek.setSettingBool('show_hint_mobile', False)
		addon = xbmcaddon.Addon()
		title = addon.getAddonInfo('name')
		text = addon.getLocalizedString(32100)
		xbmcgui.Dialog().ok(title, text)
	use_mobile = libMediathek.getSettingBool('use_mobile')
	use_mobile_prev_value = libMediathek.getSettingBool('use_mobile_prev_value')
	if (use_mobile != use_mobile_prev_value) or show_hint_mobile:
		params = libMediathek.get_params()
		if 'mode' in params:
			del params['mode']  # force default mode
		if use_mobile != use_mobile_prev_value:
			libMediathek.setSettingBool('use_mobile_prev_value', use_mobile)
			addon = xbmcaddon.Addon()
			title = addon.getAddonInfo('name')
			text = addon.getLocalizedString(32101)
			xbmcgui.Dialog().notification(title, text, os.path.join(addon.getAddonInfo('path'), 'icon.png'))
			xbmc.executebuiltin('Container.Update(path,replace)')
	if use_mobile:
		return libzdfneu.list()
	else:
		return libMediathek.list(modes, 'libZdfListMain', 'libZdfPlay', 'libZdfPlayById')

def getMostViewed():#used in unithek
	return libZdfJsonParser.parsePage('https://api.zdf.de/content/documents/meist-gesehen-100.json?profile=default')

def libZdfListMain():
	l = []
	translation = libMediathek.getTranslation
	l.append({'_name':translation(31031), 'mode':'libZdfListPage', '_type': 'dir', 'url':'https://api.zdf.de/content/documents/meist-gesehen-100.json?profile=default'})
	l.append({'_name':translation(31032), 'mode':'libZdfListShows', '_type': 'dir'})
	l.append({'_name':translation(31033), 'mode':'libZdfListChannel', '_type': 'dir'})
	l.append({'_name':translation(31034), 'mode':'libZdfListPage', '_type': 'dir', 'url':'https://api.zdf.de/search/documents?q=%2A&contentTypes=category'})
	l.append({'_name':translation(31039), 'mode':'libZdfSearch',   '_type': 'dir'})
	return l

def libZdfListShows():
	params = libMediathek.get_params()
	if 'url' in params:
		return libZdfJsonParser.getAZ(params['url'])
	else:
		return libZdfJsonParser.getAZ()

def libZdfListPage():
	params = libMediathek.get_params()
	return libZdfJsonParser.parsePage(params['url'])

def libZdfListVideos():
	params = libMediathek.get_params()
	return libZdfJsonParser.getVideos(params['url'])

def libZdfPlay():
	params = libMediathek.get_params()
	result = libZdfJsonParser.getVideoUrl(params['url'])
	result = libMediathek.getMetadata(result)
	return result

def libZdfPlayById():
	params = libMediathek.get_params()
	result = libZdfJsonParser.getVideoUrlById(params['id'])
	result = libMediathek.getMetadata(result)
	return result

def libZdfListChannel():
	l = []
	for channel in channels:
		d = {}
		d['mode'] = 'libZdfListChannelDate'
		d['_name'] = channel
		d['_type'] = 'dir'
		d['channel'] = channel
		l.append(d)
	return l

def libZdfListChannelDate():
	params = libMediathek.get_params()
	return libMediathek.populateDirDate('libZdfListChannelDateVideos',params['channel'])

def libZdfListChannelDateVideos():
	params = libMediathek.get_params()
	if 'datum' in params:
		day = date.today() - timedelta(int(params['datum']))
		yyyymmdd = day.strftime('%Y-%m-%d')
	else:
		ddmmyyyy = libMediathek.dialogDate()
		yyyymmdd = ddmmyyyy[4:8] + '-' + ddmmyyyy[2:4] + '-' + ddmmyyyy[0:2]
	l = []
	params['url'] = 'https://api.zdf.de/cmdm/epg/broadcasts?from='+yyyymmdd+'T00%3A00%3A00%2B02%3A00&to='+yyyymmdd+'T23%3A59%3A59%2B02%3A00&limit=500&profile=teaser&tvServices='+params['channel']

	return libZdfListPage()

def libZdfSearch():
	params = libMediathek.get_params()
	search_string = libMediathek.getSearchString()
	if (search_string):
		params['url'] = "https://api.zdf.de/search/documents?q="+search_string
		return libZdfListPage()
	else:
		return None

def libZdfGetVideoHtml(url):
	import re
	response = libMediathek.getUrl(url)
	return libZdfJsonParser.getVideoUrl(re.compile('"contentUrl": "(.+?)"', re.DOTALL).findall(response)[0])

modes = {
	'libZdfListMain':libZdfListMain,
	'libZdfListShows':libZdfListShows,
	'libZdfListVideos':libZdfListVideos,
	'libZdfListChannel':libZdfListChannel,
	'libZdfListChannelDate':libZdfListChannelDate,
	'libZdfListChannelDateVideos':libZdfListChannelDateVideos,
	'libZdfSearch':libZdfSearch,
	'libZdfListPage':libZdfListPage,
	'libZdfPlay':libZdfPlay,
	'libZdfPlayById':libZdfPlayById,
}