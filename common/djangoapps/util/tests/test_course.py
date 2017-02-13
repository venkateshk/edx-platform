"""
Tests for course utils.
"""
import ddt
import mock

from django.conf import settings
from django.test import TestCase

from opaque_keys.edx.keys import CourseKey
from util.course import get_link_for_about_page


@ddt.ddt
class TestCourseSharingLinks(TestCase):
    """
    Tests for course sharing links.
    """
    def setUp(self):
        super(TestCourseSharingLinks, self).setUp()
        # mock a course overview object.
        self.course_overview = mock.Mock(
            id=CourseKey.from_string('course-v1:test_org+test_number+test_run'),
            social_sharing_url='test_social_sharing_url',
            marketing_url='test_marketing_url',
        )

    def get_course_sharing_link(self, enable_social_sharing, enable_mktg_site):
        """
        Get course sharing link.

        Parameters:
             enable_social_sharing(Boolean): To indicate whether social sharing is enabled.
             enable_mktg_site(Boolean): A feature flag to decide activation of marketing site.

        Returns course sharing url.
        """
        mock_settings = {
            'FEATURES': {
                'ENABLE_MKTG_SITE': enable_mktg_site
            },
            'SOCIAL_SHARING_SETTINGS': {
                'CUSTOM_COURSE_URLS': enable_social_sharing
            },
        }

        with mock.patch.multiple('django.conf.settings', **mock_settings):
            course_sharing_link = get_link_for_about_page(self.course_overview)

        return course_sharing_link

    @ddt.data(
        (True, True, 'test_social_sharing_url'),
        (False, True, 'test_marketing_url'),
        (True, False, 'test_social_sharing_url'),
        (False, False, '{}/courses/course-v1:test_org+test_number+test_run/about'.format(settings.LMS_ROOT_URL)),
    )
    @ddt.unpack
    def test_get_course_about_page(self, enable_social_sharing, enable_mktg_site, expected_course_sharing_link):
        """
        Verify the method gives correct course sharing url on settings manipulations.
        """
        actual_course_sharing_link = self.get_course_sharing_link(
            enable_social_sharing=enable_social_sharing,
            enable_mktg_site=enable_mktg_site,
        )
        self.assertEqual(actual_course_sharing_link, expected_course_sharing_link)

    @ddt.data(
        (['social_sharing_url'], 'test_marketing_url'),
        (['marketing_url'], 'test_social_sharing_url'),
        (
            ['social_sharing_url', 'marketing_url'],
            '{}/courses/course-v1:test_org+test_number+test_run/about'.format(settings.LMS_ROOT_URL)
        ),
    )
    @ddt.unpack
    def test_get_about_page_on_none_attr(self, overview_attrs, expected_course_sharing_link):
        """
        Verify the method gives correct course sharing url even if marketing url, social
        sharing url, or both aren't set.
        """
        for overview_attr in overview_attrs:
            setattr(self.course_overview, overview_attr, None)

        actual_course_sharing_link = self.get_course_sharing_link(
            enable_social_sharing=True,
            enable_mktg_site=True,
        )
        self.assertEqual(actual_course_sharing_link, expected_course_sharing_link)
