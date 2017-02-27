"""
Sync course runs from catalog service.
"""
import logging

from django.core.management.base import BaseCommand
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.catalog.utils import get_catalog_course_runs
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Purpose is to sync course runs data from catalog service make it accessible in edx-platform.
    It just happens to only be syncing marketing URLs from catalog course runs for now.
    """
    help = 'Refresh marketing urls from catalog service.'

    def update_course_overviews(self, course_runs):
        """
        Refresh marketing urls for the given catalog course runs.

        Arguments:
             course_runs: A list containing catalog course runs.
        """
        # metrics for observability
        # number of catalog course runs retrieved.
        catalog_course_runs_retrieved = len(course_runs)
        # number of catalog course runs found in course overview.
        course_runs_found_in_cache = 0
        # number of course overview records actually get updated.
        course_metadata_updated = 0

        for course_run in course_runs:
            marketing_url = course_run['marketing_url']
            course_key = CourseKey.from_string(course_run['key'])
            try:
                course_overview = CourseOverview.objects.get(id=course_key)
                course_runs_found_in_cache += 1
            except CourseOverview.DoesNotExist:
                # In that case, just log and continue to next iteration.
                log.info(
                    '[sync_course_runs] course overview record is not found for course run: %s',
                    unicode(course_key),
                )
                continue

            # Check whether course overview's marketing url is outdated - this would save a db hit.
            if course_overview.marketing_url != marketing_url:
                course_overview.marketing_url = marketing_url
                course_overview.save()
                course_metadata_updated += 1

        return catalog_course_runs_retrieved, course_runs_found_in_cache, course_metadata_updated

    def handle(self, *args, **options):
        log.info('[sync_course_runs] Fetching course runs from catalog service.')
        course_runs = get_catalog_course_runs()
        course_runs_retrieved, course_runs_found, course_metadata_updated = self.update_course_overviews(course_runs)

        log.info(
            ('[sync_course_runs] course runs retrieved: %d, course runs found in course overview: %d,'
             ' course runs not found in course overview: %d, course overviews metadata updated: %d,'),
            course_runs_retrieved,
            course_runs_found,
            course_runs_retrieved - course_runs_found,
            course_metadata_updated,
        )
