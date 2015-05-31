PREFIX = '/video/hgtvcanada'

TITLE = 'HGTV Canada'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

FEED_URL = 'http://feed.theplatform.com/f/dtjsEC/EAlt6FfQ_kCX?count=true&byCategoryIDs=%s&startIndex=%s&endIndex=%s&sort=pubDate|desc'
MOST_RECENT_ITEMS = 50
VIDEO_URL_TEMPLATE = 'http://www.hgtv.ca/video/video.html?v=%s'
FULL_EPISODE_TYPES = ['episode', 'webisode']

####################################################################################################
def Start():
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'

##########################################################################################
@handler(PREFIX, TITLE)
def MainMenu():
    oc = ObjectContainer()
    
    title = 'Most Recent'
    oc.add(
        DirectoryObject(
            key = Callback(MostRecent, title=title),
            title = title
        )
    )    

    title = 'All Shows'
    oc.add(
        DirectoryObject(
            key = Callback(AllShows, title=title),
            title = title
        )
    )
    
    return oc
    
##########################################################################################
@route(PREFIX + '/mostrecent')
def MostRecent(title):

    oc = ObjectContainer(title2 = title)    
    json_data = JSON.ObjectFromURL(FEED_URL % ('', 1, MOST_RECENT_ITEMS))
    
    for entry in json_data['entries']:
        if entry['pl1$clipType'] not in FULL_EPISODE_TYPES:
            continue

        oc.add(CreateVideoObject(entry))

    return oc

##########################################################################################
@route(PREFIX + '/allshows')
def AllShows(title):

    oc = ObjectContainer(title2 = title)
    
    json_data = JSON.ObjectFromURL(FEED_URL % ('', 1, 1000))
    shows = {}
    
    for entry in json_data['entries']:
        show = entry['pl1$show']
        
        if not show in shows:
            shows[show] = {}
            shows[show]['episode_count'] = 1
            shows[show]['thumb'] = entry['defaultThumbnailUrl']
        else:
            shows[show]['episode_count'] = shows[show]['episode_count'] + 1
        
    for show in shows:
        oc.add(
            DirectoryObject(
                key = Callback(Videos, show=show),
                title = show + " (%s videos)" % (shows[show]['episode_count']),
                thumb = shows[show]['thumb']
            )
        )
    
    oc.objects.sort(key = lambda obj: obj.title)
    
    return oc

##########################################################################################
@route(PREFIX + '/clips')
def Clips(show):
    return Videos(show=show, full_episodes_only=False)

##########################################################################################
@route(PREFIX + '/videos', full_episodes_only = bool)
def Videos(show, full_episodes_only=True):

    oc = ObjectContainer(title2 = show)
    
    if full_episodes_only:
        clips_oc = Clips(show)
        
        if len(clips_oc) > 1:
            oc.add(DirectoryObject(key=Callback(Clips, show=show), title="Clips"))
    
    json_data = JSON.ObjectFromURL(FEED_URL % ('', 1, 1000))    
    
    for entry in json_data['entries']:
        if str(show) != str(entry['pl1$show']):
            continue

        if full_episodes_only:
            if entry['pl1$clipType'] not in FULL_EPISODE_TYPES:
                continue
        else:
            if entry['pl1$clipType'] in FULL_EPISODE_TYPES:
                continue
                
        oc.add(CreateVideoObject(entry))

    return oc

##########################################################################################
def CreateVideoObject(entry):

    url = VIDEO_URL_TEMPLATE % entry['id'].split("/")[-1]
    title = entry['title']
    summary = entry['description'] if 'description' in entry else None
    thumb = entry['defaultThumbnailUrl'] if 'defaultThumbnailUrl' in entry else None
    
    show = None
    season = None
    index = None
    if entry['pl1$clipType'] in FULL_EPISODE_TYPES:
        show = entry['pl1$show'] if 'pl1$show' in entry else None
        season = int(entry['pl1$season']) if 'pl1$season' in entry else None
        index = int(entry['pl1$episode']) if 'pl1$episode' in entry else None

    originally_available_at = Datetime.FromTimestamp(entry['pubDate'] / 1000).date() if 'pubDate' in entry else None

    duration = None
    if 'content' in entry:
        if 'duration' in entry['content'][0]:
            duration = int(float(entry['content'][0]['duration']) * 1000) 

    if entry['pl1$clipType'] in FULL_EPISODE_TYPES:
        return EpisodeObject(
            url = url,
            title = title,
            summary = summary,
            thumb = thumb,
            show = show,
            season = season,
            index = index,
            originally_available_at = originally_available_at,
            duration = duration
        )
    else:
        return VideoClipObject(
            url = url,
            title = title,
            summary = summary,
            thumb = thumb,
            originally_available_at = originally_available_at,
            duration = duration
        )


