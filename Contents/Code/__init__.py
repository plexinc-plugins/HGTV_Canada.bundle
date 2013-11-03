TITLE = "HGTV.ca"
ART = 'art-default.jpg'
ICON = 'icon-default.png'

HGTV_PARAMS = ["HmHUZlCuIXO_ymAAPiwCpTCNZ3iIF1EG", "z/HGTVNEWVC%20-%20New%20Video%20Center"]
FEED_LIST = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=%s&startIndex=1&endIndex=500&query=hasReleases&query=CustomText|PlayerTag|%s&field=airdate&field=fullTitle&field=author&field=description&field=PID&field=thumbnailURL&field=title&contentCustomField=title&field=ID&field=parent"
FEEDS_LIST = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=%s&startIndex=1&endIndex=500&query=categoryIDs|%s&sortField=airdate&sortDescending=true&field=airdate&field=author&field=description&field=length&field=PID&field=thumbnailURL&field=title&contentCustomField=title&contentCustomField=Episode&contentCustomField=Season"
DIRECT_FEED = "http://release.theplatform.com/content.select?format=SMIL&pid=%s&UserName=Unknown&Embedded=True&TrackBrowser=True&Tracking=True&TrackLocation=True"
LOADCATS = { 
	'full':["/Shows/"],
	'how-to':["/How-To/"]
	}
RE_SEASON_TEST = Regex("Season")
VIDEO_URL = 'http://www.hgtv.ca/video/?releasePID=%s'

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/hgtvcanada', MainMenu, TITLE, ICON, ART)

	# setup the default viewgroups for the plugin	
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = TITLE
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)
	EpisodeObject.thumb = R(ICON)
	EpisodeObject.art = R(ART)

	# Setup some basic things the plugin needs to know about
	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
def MainMenu():
	oc = ObjectContainer(
		objects = [
			DirectoryObject(
				key = Callback(LoadShowList, cats='full'),
				title = 'Shows'
			),
			DirectoryObject(
				key = Callback(LatestShows),
				title = 'Latest Videos Posted'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='how-to'),
				title = 'How To Videos'
			),
	] )

	return oc

	
####################################################################################################
def LoadShowList(cats):
	oc = ObjectContainer()
	
	shows_with_seasons = {}
	shows_without_seasons = {}

	network = HGTV_PARAMS
	content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))

	for item in content['items']:
		if WantedCats(item['parent'],cats):
			title = item['fullTitle'].split('/')[2]
			iid = item['ID']
			thumb_url = item['thumbnailURL']
			
			# a couple of shows have "Full Episodes" instead of "Season [0-9]"
			if RE_SEASON_TEST.search(item['fullTitle']) or "Full Episodes" in item['fullTitle']:
				if not(title in shows_with_seasons):
					Log.Debug("With Season: " + item['fullTitle'] + " --- " + item['title'])
					shows_with_seasons[title] = ""
					oc.add(
						DirectoryObject(
							key = Callback(SeasonsPage, cats=cats, network=network, showtitle=title),
							title = title, 
							thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
						)
					)
			else:				
				if not(title in shows_without_seasons) and not (title in shows_with_seasons):
					shows_without_seasons[title] = []
					shows_without_seasons[title].append(
						DirectoryObject(
							key = Callback(VideosPage, pid=network[0], iid=iid),
							title = title,
							thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
						)
					)

	for show in shows_without_seasons:
		if not(show in shows_with_seasons) and len([added_show for added_show in shows_with_seasons if show in added_show or added_show in show]) == 0:
			for item in shows_without_seasons[show]:
				oc.add(item)

	# sort here
	oc.objects.sort(key = lambda obj: obj.title)

	return oc


####################################################################################################
def VideosPage(pid, iid):

	oc = ObjectContainer(
		view_group = 'InfoList'
	)
	pageUrl = FEEDS_LIST % (pid, iid)
	feeds = JSON.ObjectFromURL(pageUrl)

	for item in feeds['items']:	
		title = item['title']
		pid = item['PID']
		summary = item['description'].replace('In Full:', '')
		duration = item['length']
		# there are a good handful of thumbnailUrls that have carriage returns in the middle of them!
		thumb_url = item['thumbnailURL'].replace("\r\n\r\n","")
		airdate = int(item['airdate'])/1000
		originally_available_at = Datetime.FromTimestamp(airdate).date()
		
		try:
			# try to set the seasons and episode info
			# NB: episode is set with 'index' (not in framework docs)!
			season = item['contentCustomData'][1]['value']
			seasonint = int(float(season))
			episode = item['contentCustomData'][0]['value']
			episodeint = int(float(episode))

			oc.add(
				EpisodeObject(
					url = VIDEO_URL % pid,
					title = title,
					summary=summary,
					duration=duration,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON),
					originally_available_at = originally_available_at,
	 				season = seasonint,
	 				index = episodeint
				)
			)

		except:
			# if we don't get the season/episode info then don't set it
			oc.add(
				EpisodeObject(
					url = VIDEO_URL % pid,
					title = title,
					summary=summary,
					duration=duration,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON),
					originally_available_at = originally_available_at
				)
			)

	return oc

####################################################################################################
def SeasonsPage(cats, network, showtitle):

	oc = ObjectContainer()
	
	content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
	season_list = []

	for item in content['items']:
		if WantedCats(item['parent'], cats) and showtitle in item['parent']: # and RE_SEASON_TEST.search(item['title'])
			title = item['title']
			
			# if this title is a season title prepend a space (to get it to top of list alphabetically
			# for cases there there's a lot of other content (i.e. Decked Out)
			if RE_SEASON_TEST.search(title):
				title = " " + title
			
			# corner cases:  There are now some shows that don't follow this logic properly. We need to workaround these
			# which have multiple seasons with the 'title' being "Full Episodes" (instead of the expected Season X).  We will 
			# do this by prepending the last part of the 'parent' (which is almost all cases of these are either "Season X" 
			# or the actual show title so either way it presents ok within the menus and still allows us to filter dupes 
			# -- i.e. we won't have multiple items with the standard show title, only if they have multiple seasons) 
			# Gerk -- Nov 2/13
			if title == 'Full Episodes':
				title = " " + item['parent'].split("/")[-1] + " " + title
			
			if title not in season_list:
				season_list.append(title)

				iid = item['ID']
				thumb_url = item['thumbnailURL']
				oc.add(
					DirectoryObject(
						key = Callback(VideosPage, pid=network[0], iid=iid),
						title = title,
						thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
					)
				)
	oc.objects.sort(key = lambda obj: obj.title)
	return oc

def LatestShows():
	content = JSON.ObjectFromURL("http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=HmHUZlCuIXO_ymAAPiwCpTCNZ3iIF1EG&startIndex=1&endIndex=50&field=airdate&field=author&field=description&field=length&field=PID&&field=URL&field=thumbnailURL&field=title&contentCustomField=title&contentCustomField=Episode&contentCustomField=Season&contentCustomField=Show")
	oc = ObjectContainer()
	
	for item in content['items']:
		vidTitle = item['title'];
		pid = item['PID']
		show = item['contentCustomData'][2]['value']
		season = item['contentCustomData'][1]['value']
		episode = item['contentCustomData'][0]['value']
		
		title = "%s" % (show)
		
		if season != "":
			title = "%s - S%s" % (title, season)
		if episode != "":
			title = "%sE%s" % (title, episode)

		title = "%s - %s" % (title, vidTitle)

		summary = item['description']
		duration = item['length']
		thumb_url = item['thumbnailURL'].replace("\r\n\r\n","")
		airdate = int(item['airdate'])/1000
		originally_available_at = Datetime.FromTimestamp(airdate).date()

		oc.add(
			VideoClipObject(
				url = VIDEO_URL % pid,
				title = title,
				summary=summary,
				duration=duration,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON),
				originally_available_at = originally_available_at
			)
		)
		
	return oc
			

####################################################################################################
def WantedCats(thisShow,cats):

	for show in LOADCATS[cats]:
		if show in thisShow:
			return 1				
	return 0

