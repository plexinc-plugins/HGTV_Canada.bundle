TITLE = "HGTV.ca"
ART = 'art-default.jpg'
ICON = 'icon-default.png'

HGTV_PARAMS = ["HmHUZlCuIXO_ymAAPiwCpTCNZ3iIF1EG", "z/HGTV%20Player%20-%20Video%20Center"]
FEED_LIST = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=%s&startIndex=1&endIndex=500&query=hasReleases&query=CustomText|PlayerTag|%s&field=airdate&field=fullTitle&field=author&field=description&field=PID&field=thumbnailURL&field=title&contentCustomField=title&field=ID&field=parent"
FEEDS_LIST = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=%s&startIndex=1&endIndex=500&query=categoryIDs|%s&sortField=airdate&sortDescending=true&field=airdate&field=author&field=description&field=length&field=PID&field=thumbnailURL&field=title&contentCustomField=title&contentCustomField=Episode&contentCustomField=Season"
DIRECT_FEED = "http://release.theplatform.com/content.select?format=SMIL&pid=%s&UserName=Unknown&Embedded=True&TrackBrowser=True&Tracking=True&TrackLocation=True"
LOADCATS = { 
	'full':["Full Episodes","Sarah Richardson","Mike Holmes","Peter Fallico","Sam Pynn","Colin and Justin","Classics"],
	'sarah':['Sarah Richardson'],
	'mike':['Mike Holmes'],
	"peter":["Peter Fallico"],
	"sam":["Sam Pynn"],
	"colin":["Colin and Justin"],
	"classics":["Classics"],
	"original":["Original Video"],
	"diy":["DIY Projects"],
	"web":["Web Exclusives"],
	"kitchens":["Kitchens"],
	"realestate":["Real Estate"],
	"backyard":["Backyard Living"],
	"renos":["Renovations"],
	"recent":["Most Recent"]
	}
RE_SEASON_TEST = Regex("Season")

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

	if not Platform.HasFlash:
		return MessageContainer(NAME, L('This channel requires Flash. Please download and install Adobe Flash on the computer running Plex Media Server.'))

	oc = ObjectContainer(
		objects = [
			DirectoryObject(
				key = Callback(LongVideos),
				title = 'Full Length Shows'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='recent'),
				title = 'Recently Added'
			),
			DirectoryObject(
				key = Callback(ShortVideos),
				title = 'Shorter Video Clips'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='web'),
				title = 'Web Exclusives'
			),
	] )
	
	return oc

####################################################################################################
def LongVideos():

	oc = ObjectContainer(
		objects = [
			DirectoryObject(
				key = Callback(LoadShowList, cats='full'),
				title = 'All Shows'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='sarah'),
				title = 'Sarah Richardson'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='mike'),
				title = 'Mike Holmes'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='peter'),
				title = 'Peter Fallico'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='sam'),
				title = 'Sam Pynn'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='colin'),
				title = 'Colin and Justin'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='classics'),
				title = 'Classics'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='recent'),
				title = 'Recently Released'
			)
	] )
	
	return oc

####################################################################################################
def ShortVideos():
	
	oc = ObjectContainer(
		objects = [
			DirectoryObject(
				key = Callback(LoadShowList, cats='original'),
				title = 'Original Video'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='diy'),
				title = 'DIY Projects'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='kitchens'),
				title = 'Kitchens'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='realestate'),
				title = 'Real Estate'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='backyard'),
				title = 'Backyard Living'
			),
			DirectoryObject(
				key = Callback(LoadShowList, cats='renos'),
				title = 'Renovations'
			)

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
			title = item['title']
			# there are a good handful of thumbnailUrls that have carriage returns in the middle of them!
			thumb_url = item['thumbnailURL'].replace("\r\n\r\n","")
			iid = item['ID']
			
			if RE_SEASON_TEST.search(title):
				show, season = title.split("Season")
				if show=="":
					# bad data from provider, skip this one
					continue
				show = show.rstrip().split(":")[0].rstrip().rstrip('.')
				
				if not(show in shows_with_seasons):
					shows_with_seasons[show] = ""
					oc.add(
						DirectoryObject(
							key = Callback(SeasonsPage, cats=cats, network=network, showtitle=show),
							title = show, 
							thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=R(ICON))
						)
					)
			else:
				if title=="":
					# bad data from provider, skip this one
					continue
				if not(title in shows_without_seasons):
					shows_without_seasons[title] = []
					shows_without_seasons[title].append(
						DirectoryObject(
							key = Callback(VideosPage, pid=network[0], iid=iid),
							title = title,
							thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=R(ICON))
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
def VideoParse(pid):

	videosmil = HTTP.Request(DIRECT_FEED % pid).content
	player = videosmil.split("ref src")
	player = player[2].split('"')

	if ".mp4" in player[1]:
		player = player[1].replace(".mp4", "")
		try:
			clip = player.split(";")
			clip = "mp4:" + clip[4]
		except:
			clip = player.split("/video/")
			player = player.split("/video/")[0]
			clip = "mp4:/video/" + clip[-1]
	else:
		player = player[1].replace(".flv", "")
		try:
			clip = player.split(";")
			clip = clip[4]
		except:
			clip = player.split("/video/")
			player = player.split("/video/")[0]
			clip = "/video/" + clip[-1]

	return Redirect(RTMPVideoItem(player, clip))


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
		summary =  item['description'].replace('In Full:', '')
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
# 			Log("Gerk: %i-%i : %s",seasonint, episodeint, title)
			oc.add(
				EpisodeObject(
					key = Callback(VideoParse, pid=pid),
					rating_key = pid, 
					title = title,
					summary=summary,
					duration=duration,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=R(ICON)),
					originally_available_at = originally_available_at,
	 				season = seasonint,
	 				index = episodeint
				)
			)

		except:
			# if we don't get the season/episode info then don't set it
			oc.add(
				EpisodeObject(
					key = Callback(VideoParse, pid=pid),
					rating_key = pid, 
					title = title,
					summary=summary,
					duration=duration,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=R(ICON)),
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
		if WantedCats(item['parent'], cats) and showtitle in item['title']:
			title = item['title'].split(showtitle)[1].lstrip(':').lstrip('.').lstrip()
			if title not in season_list:
				if title=="":
					# bad data from provider, this is a corner case and happens often
					# enough that it's worth adding these in as uncategorized if they
					# made it to the Seasons list (it means they have child elements to view)
					title="Uncategorized Items"
				season_list.append(title)
				iid = item['ID']
				pid = item['PID']
				# there are a good handful of thumbnailUrls that have carriage returns in the middle of them!
				thumb_url = item['thumbnailURL'].replace("\r\n\r\n","")
				oc.add(
					DirectoryObject(
						key = Callback(VideosPage, pid=pid, iid=iid),
						title = title,
						thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=R(ICON))
					)
				)
	oc.objects.sort(key = lambda obj: obj.title)
	return oc

####################################################################################################
def WantedCats(thisShow,cats):

	for show in LOADCATS[cats]:
		if show in thisShow:
			return 1				
	return 0

