from __future__ import unicode_literals

import re

from .mtv import MTVServicesInfoExtractor
from ..compat import (
    compat_str,
    compat_urllib_parse_urlencode,
)
from ..utils import (
    ExtractorError,
    float_or_none,
    unified_strdate,
)


class ComedyCentralIE(MTVServicesInfoExtractor):
    _VALID_URL = r'''(?x)https?://(?:www\.)?cc\.com/
        (video-clips|episodes|cc-studios|video-collections|full-episodes|shows)
        /(?P<title>.*)'''
    _FEED_URL = 'http://comedycentral.com/feeds/mrss/'

    _TESTS = [{
        'url': 'http://www.cc.com/video-clips/kllhuv/stand-up-greg-fitzsimmons--uncensored---too-good-of-a-mother',
        'md5': 'c4f48e9eda1b16dd10add0744344b6d8',
        'info_dict': {
            'id': 'cef0cbb3-e776-4bc9-b62e-8016deccb354',
            'ext': 'mp4',
            'title': 'CC:Stand-Up|Greg Fitzsimmons: Life on Stage|Uncensored - Too Good of a Mother',
            'description': 'After a certain point, breastfeeding becomes c**kblocking.',
        },
    }, {
        'url': 'http://www.cc.com/shows/the-daily-show-with-trevor-noah/interviews/6yx39d/exclusive-rand-paul-extended-interview',
        'only_matching': True,
    }]


class ComedyCentralShowsIE(MTVServicesInfoExtractor):
    IE_DESC = 'The Daily Show / The Colbert Report'
    # urls can be abbreviations like :thedailyshow
    # urls for episodes like:
    # or urls for clips like: http://www.thedailyshow.com/watch/mon-december-10-2012/any-given-gun-day
    #                     or: http://www.colbertnation.com/the-colbert-report-videos/421667/november-29-2012/moon-shattering-news
    #                     or: http://www.colbertnation.com/the-colbert-report-collections/422008/festival-of-lights/79524
    _VALID_URL = r'''(?x)^(:(?P<shortname>tds|thedailyshow)
                      |https?://(:www\.)?
                          (?P<showname>thedailyshow|thecolbertreport|tosh)\.(?:cc\.)?com/
                         ((?:full-)?episodes/(?:[0-9a-z]{6}/)?(?P<episode>.*)|
                          (?P<clip>
                              (?:(?:guests/[^/]+|videos|video-(?:clips|playlists)|special-editions|news-team/[^/]+)/[^/]+/(?P<videotitle>[^/?#]+))
                              |(the-colbert-report-(videos|collections)/(?P<clipID>[0-9]+)/[^/]*/(?P<cntitle>.*?))
                              |(watch/(?P<date>[^/]*)/(?P<tdstitle>.*))
                          )|
                          (?P<interview>
                              extended-interviews/(?P<interID>[0-9a-z]+)/
                              (?:playlist_tds_extended_)?(?P<interview_title>[^/?#]*?)
                              (?:/[^/?#]?|[?#]|$))))
                     '''
    _TESTS = [{
        'url': 'http://thedailyshow.cc.com/watch/thu-december-13-2012/kristen-stewart',
        'md5': '4e2f5cb088a83cd8cdb7756132f9739d',
        'info_dict': {
            'id': 'ab9ab3e7-5a98-4dbe-8b21-551dc0523d55',
            'ext': 'mp4',
            'upload_date': '20121213',
            'description': 'Kristen Stewart learns to let loose in "On the Road."',
            'uploader': 'thedailyshow',
            'title': 'thedailyshow kristen-stewart part 1',
        }
    }, {
        'url': 'http://thedailyshow.cc.com/extended-interviews/b6364d/sarah-chayes-extended-interview',
        'info_dict': {
            'id': 'sarah-chayes-extended-interview',
            'description': 'Carnegie Endowment Senior Associate Sarah Chayes discusses how corrupt institutions function throughout the world in her book "Thieves of State: Why Corruption Threatens Global Security."',
            'title': 'thedailyshow Sarah Chayes Extended Interview',
        },
        'playlist': [
            {
                'info_dict': {
                    'id': '0baad492-cbec-4ec1-9e50-ad91c291127f',
                    'ext': 'mp4',
                    'upload_date': '20150129',
                    'description': 'Carnegie Endowment Senior Associate Sarah Chayes discusses how corrupt institutions function throughout the world in her book "Thieves of State: Why Corruption Threatens Global Security."',
                    'uploader': 'thedailyshow',
                    'title': 'thedailyshow sarah-chayes-extended-interview part 1',
                },
            },
            {
                'info_dict': {
                    'id': '1e4fb91b-8ce7-4277-bd7c-98c9f1bbd283',
                    'ext': 'mp4',
                    'upload_date': '20150129',
                    'description': 'Carnegie Endowment Senior Associate Sarah Chayes discusses how corrupt institutions function throughout the world in her book "Thieves of State: Why Corruption Threatens Global Security."',
                    'uploader': 'thedailyshow',
                    'title': 'thedailyshow sarah-chayes-extended-interview part 2',
                },
            },
        ],
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://thedailyshow.cc.com/extended-interviews/xm3fnq/andrew-napolitano-extended-interview',
        'only_matching': True,
    }, {
        'url': 'http://thecolbertreport.cc.com/videos/29w6fx/-realhumanpraise-for-fox-news',
        'only_matching': True,
    }, {
        'url': 'http://thecolbertreport.cc.com/videos/gh6urb/neil-degrasse-tyson-pt--1?xrs=eml_col_031114',
        'only_matching': True,
    }, {
        'url': 'http://thedailyshow.cc.com/guests/michael-lewis/3efna8/exclusive---michael-lewis-extended-interview-pt--3',
        'only_matching': True,
    }, {
        'url': 'http://thedailyshow.cc.com/episodes/sy7yv0/april-8--2014---denis-leary',
        'only_matching': True,
    }, {
        'url': 'http://thecolbertreport.cc.com/episodes/8ase07/april-8--2014---jane-goodall',
        'only_matching': True,
    }, {
        'url': 'http://thedailyshow.cc.com/video-playlists/npde3s/the-daily-show-19088-highlights',
        'only_matching': True,
    }, {
        'url': 'http://thedailyshow.cc.com/video-playlists/t6d9sg/the-daily-show-20038-highlights/be3cwo',
        'only_matching': True,
    }, {
        'url': 'http://thedailyshow.cc.com/special-editions/2l8fdb/special-edition---a-look-back-at-food',
        'only_matching': True,
    }, {
        'url': 'http://thedailyshow.cc.com/news-team/michael-che/7wnfel/we-need-to-talk-about-israel',
        'only_matching': True,
    }, {
        'url': 'http://tosh.cc.com/video-clips/68g93d/twitter-users-share-summer-plans',
        'only_matching': True,
    }]

    _available_formats = ['3500', '2200', '1700', '1200', '750', '400']

    _video_extensions = {
        '3500': 'mp4',
        '2200': 'mp4',
        '1700': 'mp4',
        '1200': 'mp4',
        '750': 'mp4',
        '400': 'mp4',
    }
    _video_dimensions = {
        '3500': (1280, 720),
        '2200': (960, 540),
        '1700': (768, 432),
        '1200': (640, 360),
        '750': (512, 288),
        '400': (384, 216),
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)

        if mobj.group('shortname'):
            return self.url_result('http://www.cc.com/shows/the-daily-show-with-trevor-noah/full-episodes')

        if mobj.group('clip'):
            if mobj.group('videotitle'):
                epTitle = mobj.group('videotitle')
            elif mobj.group('showname') == 'thedailyshow':
                epTitle = mobj.group('tdstitle')
            else:
                epTitle = mobj.group('cntitle')
            dlNewest = False
        elif mobj.group('interview'):
            epTitle = mobj.group('interview_title')
            dlNewest = False
        else:
            dlNewest = not mobj.group('episode')
            if dlNewest:
                epTitle = mobj.group('showname')
            else:
                epTitle = mobj.group('episode')
        show_name = mobj.group('showname')

        webpage, htmlHandle = self._download_webpage_handle(url, epTitle)
        if dlNewest:
            url = htmlHandle.geturl()
            mobj = re.match(self._VALID_URL, url, re.VERBOSE)
            if mobj is None:
                raise ExtractorError('Invalid redirected URL: ' + url)
            if mobj.group('episode') == '':
                raise ExtractorError('Redirected URL is still not specific: ' + url)
            epTitle = (mobj.group('episode') or mobj.group('videotitle')).rpartition('/')[-1]

        mMovieParams = re.findall('(?:<param name="movie" value="|var url = ")(http://media.mtvnservices.com/([^"]*(?:episode|video).*?:.*?))"', webpage)
        if len(mMovieParams) == 0:
            # The Colbert Report embeds the information in a without
            # a URL prefix; so extract the alternate reference
            # and then add the URL prefix manually.

            altMovieParams = re.findall('data-mgid="([^"]*(?:episode|video|playlist).*?:.*?)"', webpage)
            if len(altMovieParams) == 0:
                raise ExtractorError('unable to find Flash URL in webpage ' + url)
            else:
                mMovieParams = [('http://media.mtvnservices.com/' + altMovieParams[0], altMovieParams[0])]

        uri = mMovieParams[0][1]
        # Correct cc.com in uri
        uri = re.sub(r'(episode:[^.]+)(\.cc)?\.com', r'\1.com', uri)

        index_url = 'http://%s.cc.com/feeds/mrss?%s' % (show_name, compat_urllib_parse_urlencode({'uri': uri}))
        idoc = self._download_xml(
            index_url, epTitle,
            'Downloading show index', 'Unable to download episode index')

        title = idoc.find('./channel/title').text
        description = idoc.find('./channel/description').text

        entries = []
        item_els = idoc.findall('.//item')
        for part_num, itemEl in enumerate(item_els):
            upload_date = unified_strdate(itemEl.findall('./pubDate')[0].text)
            thumbnail = itemEl.find('.//{http://search.yahoo.com/mrss/}thumbnail').attrib.get('url')

            content = itemEl.find('.//{http://search.yahoo.com/mrss/}content')
            duration = float_or_none(content.attrib.get('duration'))
            mediagen_url = content.attrib['url']
            guid = itemEl.find('./guid').text.rpartition(':')[-1]

            cdoc = self._download_xml(
                mediagen_url, epTitle,
                'Downloading configuration for segment %d / %d' % (part_num + 1, len(item_els)))

            turls = []
            for rendition in cdoc.findall('.//rendition'):
                finfo = (rendition.attrib['bitrate'], rendition.findall('./src')[0].text)
                turls.append(finfo)

            formats = []
            for format, rtmp_video_url in turls:
                w, h = self._video_dimensions.get(format, (None, None))
                formats.append({
                    'format_id': 'vhttp-%s' % format,
                    'url': self._transform_rtmp_url(rtmp_video_url),
                    'ext': self._video_extensions.get(format, 'mp4'),
                    'height': h,
                    'width': w,
                })
                formats.append({
                    'format_id': 'rtmp-%s' % format,
                    'url': rtmp_video_url.replace('viacomccstrm', 'viacommtvstrm'),
                    'ext': self._video_extensions.get(format, 'mp4'),
                    'height': h,
                    'width': w,
                })
                self._sort_formats(formats)

            subtitles = self._extract_subtitles(cdoc, guid)

            virtual_id = show_name + ' ' + epTitle + ' part ' + compat_str(part_num + 1)
            entries.append({
                'id': guid,
                'title': virtual_id,
                'formats': formats,
                'uploader': show_name,
                'upload_date': upload_date,
                'duration': duration,
                'thumbnail': thumbnail,
                'description': description,
                'subtitles': subtitles,
            })

        return {
            '_type': 'playlist',
            'id': epTitle,
            'entries': entries,
            'title': show_name + ' ' + title,
            'description': description,
        }


class ComedyCentralTVIE(MTVServicesInfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?comedycentral\.tv/(?:staffeln|shows)/(?P<id>[^/?#&]+)'
    _TESTS = [{
        'url': 'http://www.comedycentral.tv/staffeln/7436-the-mindy-project-staffel-4',
        'info_dict': {
            'id': 'local_playlist-f99b626bdfe13568579a',
            'ext': 'flv',
            'title': 'Episode_the-mindy-project_shows_season-4_episode-3_full-episode_part1',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        'url': 'http://www.comedycentral.tv/shows/1074-workaholics',
        'only_matching': True,
    }, {
        'url': 'http://www.comedycentral.tv/shows/1727-the-mindy-project/bonus',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        mrss_url = self._search_regex(
            r'data-mrss=(["\'])(?P<url>(?:(?!\1).)+)\1',
            webpage, 'mrss url', group='url')

        return self._get_videos_info_from_url(mrss_url, video_id)
