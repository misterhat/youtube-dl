# coding: utf-8
from __future__ import unicode_literals

import random
import re

from .common import InfoExtractor
from ..compat import compat_urllib_parse_unquote_plus
from ..utils import (
    int_or_none,
    float_or_none,
    timeconvert,
    update_url_query,
    xpath_text,
)


class KUSIIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?kusi\.com/(?P<path>story/.+|video\?clipId=(?P<clipId>\d+))'
    _TESTS = [{
        'url': 'http://www.kusi.com/story/31183873/turko-files-case-closed-put-on-hold',
        'md5': 'f926e7684294cf8cb7bdf8858e1b3988',
        'info_dict': {
            'id': '12203019',
            'ext': 'mp4',
            'title': 'Turko Files: Case Closed! & Put On Hold!',
            'duration': 231.0,
            'upload_date': '20160210',
            'timestamp': 1455087571,
            'thumbnail': 're:^https?://.*\.jpg$'
        },
    }, {
        'url': 'http://kusi.com/video?clipId=12203019',
        'info_dict': {
            'id': '12203019',
            'ext': 'mp4',
            'title': 'Turko Files: Case Closed! & Put On Hold!',
            'duration': 231.0,
            'upload_date': '20160210',
            'timestamp': 1455087571,
            'thumbnail': 're:^https?://.*\.jpg$'
        },
        'params': {
            'skip_download': True,  # Same as previous one
        },
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        clip_id = mobj.group('clipId')
        video_id = clip_id or mobj.group('path')

        webpage = self._download_webpage(url, video_id)

        if clip_id is None:
            video_id = clip_id = self._html_search_regex(
                r'"clipId"\s*,\s*"(\d+)"', webpage, 'clip id')

        affiliate_id = self._search_regex(
            r'affiliateId\s*:\s*\'([^\']+)\'', webpage, 'affiliate id')

        # See __Packages/worldnow/model/GalleryModel.as of WNGallery.swf
        xml_url = update_url_query('http://www.kusi.com/build.asp', {
            'buildtype': 'buildfeaturexmlrequest',
            'featureType': 'Clip',
            'featureid': clip_id,
            'affiliateno': affiliate_id,
            'clientgroupid': '1',
            'rnd': int(round(random.random() * 1000000)),
        })

        doc = self._download_xml(xml_url, video_id)

        video_title = xpath_text(doc, 'HEADLINE', fatal=True)
        duration = float_or_none(xpath_text(doc, 'DURATION'), scale=1000)
        description = xpath_text(doc, 'ABSTRACT')
        thumbnail = xpath_text(doc, './THUMBNAILIMAGE/FILENAME')
        createtion_time = timeconvert(xpath_text(doc, 'rfc822creationdate'))

        quality_options = doc.find('{http://search.yahoo.com/mrss/}group').findall('{http://search.yahoo.com/mrss/}content')
        formats = []
        for quality in quality_options:
            formats.append({
                'url': compat_urllib_parse_unquote_plus(quality.attrib['url']),
                'height': int_or_none(quality.attrib.get('height')),
                'width': int_or_none(quality.attrib.get('width')),
                'vbr': float_or_none(quality.attrib.get('bitratebits'), scale=1000),
            })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': video_title,
            'description': description,
            'duration': duration,
            'formats': formats,
            'thumbnail': thumbnail,
            'timestamp': createtion_time,
        }
