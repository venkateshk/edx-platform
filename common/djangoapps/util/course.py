"""
Utility methods related to course
"""
import logging
from django.conf import settings

log = logging.getLogger(__name__)


def get_link_for_about_page(course_overview):
    """
    Arguments:
        course_overview: A course metadata object.

    Returns the course sharing url, this can be one of course's social sharing url, marketing url, or
    lms course about url.
    """
    is_social_sharing_enabled = (
        hasattr(settings, 'SOCIAL_SHARING_SETTINGS') and
        settings.SOCIAL_SHARING_SETTINGS.get('CUSTOM_COURSE_URLS')
    )
    if is_social_sharing_enabled and course_overview.social_sharing_url:
        course_about_url = course_overview.social_sharing_url
    elif settings.FEATURES.get('ENABLE_MKTG_SITE') and course_overview.marketing_url:
        course_about_url = course_overview.marketing_url
    else:
        course_about_url = u'{about_base_url}/courses/{course_key}/about'.format(
            about_base_url=settings.LMS_ROOT_URL,
            course_key=unicode(course_overview.id),
        )

    return course_about_url
