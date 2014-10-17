from __future__ import unicode_literals

import itertools
import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    parse_iso8601,
)


class TwitchIE(InfoExtractor):
    # TODO: One broadcast may be split into multiple videos. The key
    # 'broadcast_id' is the same for all parts, and 'broadcast_part'
    # starts at 1 and increases. Can we treat all parts as one video?
    _VALID_URL = r"""(?x)^(?:http://)?(?:www\.)?twitch\.tv/
        (?:
            (?P<channelid>[^/]+)|
            (?:(?:[^/]+)/b/(?P<videoid>[^/]+))|
            (?:(?:[^/]+)/c/(?P<chapterid>[^/]+))
        )
        /?(?:\#.*)?$
        """
    _PAGE_LIMIT = 100
    _API_BASE = 'https://api.twitch.tv'
    _TEST = {
        'url': 'http://www.twitch.tv/thegamedevhub/b/296128360',
        'md5': 'ecaa8a790c22a40770901460af191c9a',
        'info_dict': {
            'id': '296128360',
            'ext': 'flv',
            'upload_date': '20110927',
            'uploader_id': 25114803,
            'uploader': 'thegamedevhub',
            'title': 'Beginner Series - Scripting With Python Pt.1'
        }
    }

    def _handle_error(self, response):
        if not isinstance(response, dict):
            return
        error = response.get('error')
        if error:
            raise ExtractorError(
                '%s returned error: %s - %s' % (self.IE_NAME, error, response.get('message')),
                expected=True)

    def _download_json(self, url, video_id, note='Downloading JSON metadata'):
        response = super(TwitchIE, self)._download_json(url, video_id, note)
        self._handle_error(response)
        return response

    def _extract_media(self, item, item_id):
        ITEMS = {
            'a': 'video',
            'c': 'chapter',
        }
        info = self._extract_info(self._download_json(
            '%s/kraken/videos/%s%s' % (self._API_BASE, item, item_id), item_id,
            'Downloading %s info JSON' % ITEMS[item]))
        response = self._download_json(
            '%s/api/videos/%s%s' % (self._API_BASE, item, item_id), item_id,
            'Downloading %s playlist JSON' % ITEMS[item])
        entries = []
        chunks = response['chunks']
        qualities = list(chunks.keys())
        for num, fragment in enumerate(zip(*chunks.values()), start=1):
            formats = []
            for fmt_num, fragment_fmt in enumerate(fragment):
                format_id = qualities[fmt_num]
                fmt = {
                    'url': fragment_fmt['url'],
                    'format_id': format_id,
                    'quality': 1 if format_id == 'live' else 0,
                }
                m = re.search(r'^(?P<height>\d+)[Pp]', format_id)
                if m:
                    fmt['height'] = int(m.group('height'))
                formats.append(fmt)
            self._sort_formats(formats)
            entry = dict(info)
            entry['title'] = '%s part %d' % (entry['title'], num)
            entry['formats'] = formats
            entries.append(entry)
        return entries

    def _extract_info(self, info):
        return {
            'id': info['_id'],
            'title': info['title'],
            'description': info['description'],
            'duration': info['length'],
            'thumbnail': info['preview'],
            'uploader': info['channel']['display_name'],
            'uploader_id': info['channel']['name'],
            'timestamp': parse_iso8601(info['recorded_at']),
            'view_count': info['views'],
        }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        if mobj.group('chapterid'):
            return self._extract_media('c', mobj.group('chapterid'))

            """
            webpage = self._download_webpage(url, chapter_id)
            m = re.search(r'PP\.archive_id = "([0-9]+)";', webpage)
            if not m:
                raise ExtractorError('Cannot find archive of a chapter')
            archive_id = m.group(1)

            api = api_base + '/broadcast/by_chapter/%s.xml' % chapter_id
            doc = self._download_xml(
                api, chapter_id,
                note='Downloading chapter information',
                errnote='Chapter information download failed')
            for a in doc.findall('.//archive'):
                if archive_id == a.find('./id').text:
                    break
            else:
                raise ExtractorError('Could not find chapter in chapter information')

            video_url = a.find('./video_file_url').text
            video_ext = video_url.rpartition('.')[2] or 'flv'

            chapter_api_url = 'https://api.twitch.tv/kraken/videos/c' + chapter_id
            chapter_info = self._download_json(
                chapter_api_url, 'c' + chapter_id,
                note='Downloading chapter metadata',
                errnote='Download of chapter metadata failed')

            bracket_start = int(doc.find('.//bracket_start').text)
            bracket_end = int(doc.find('.//bracket_end').text)

            # TODO determine start (and probably fix up file)
            #  youtube-dl -v http://www.twitch.tv/firmbelief/c/1757457
            #video_url += '?start=' + TODO:start_timestamp
            # bracket_start is 13290, but we want 51670615
            self._downloader.report_warning('Chapter detected, but we can just download the whole file. '
                                            'Chapter starts at %s and ends at %s' % (formatSeconds(bracket_start), formatSeconds(bracket_end)))

            info = {
                'id': 'c' + chapter_id,
                'url': video_url,
                'ext': video_ext,
                'title': chapter_info['title'],
                'thumbnail': chapter_info['preview'],
                'description': chapter_info['description'],
                'uploader': chapter_info['channel']['display_name'],
                'uploader_id': chapter_info['channel']['name'],
            }
            return info
            """
        elif mobj.group('videoid'):
            return self._extract_media('a', mobj.group('videoid'))
        elif mobj.group('channelid'):
            channel_id = mobj.group('channelid')
            info = self._download_json(
                '%s/kraken/channels/%s' % (self._API_BASE, channel_id),
                channel_id, 'Downloading channel info JSON')
            channel_name = info.get('display_name') or info.get('name')
            entries = []
            offset = 0
            limit = self._PAGE_LIMIT
            for counter in itertools.count(1):
                response = self._download_json(
                    '%s/kraken/channels/%s/videos/?offset=%d&limit=%d'
                    % (self._API_BASE, channel_id, offset, limit),
                    channel_id, 'Downloading channel videos JSON page %d' % counter)
                videos = response['videos']
                if not videos:
                    break
                entries.extend([self.url_result(video['url'], 'Twitch') for video in videos])
                offset += limit
            return self.playlist_result(entries, channel_id, channel_name)