"""
Tests for the sync course runs management command.
"""
import ddt
import mock

from django.core.management import call_command

from openedx.core.djangoapps.catalog.tests.factories import CourseRunFactory
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

COMMAND_MODULE = 'openedx.core.djangoapps.catalog.management.commands.sync_course_runs'


@ddt.ddt
@mock.patch(COMMAND_MODULE + '.get_catalog_course_runs')
class TestSyncCourseRunsCommand(ModuleStoreTestCase):
    """
    Test for the sync course runs management command.
    """
    def setUp(self):
        super(TestSyncCourseRunsCommand, self).setUp()
        # create mongo course
        self.course = CourseFactory.create()
        # load this course into course overview
        CourseOverview.get_from_id(self.course.id)
        # create a catalog course run with the same course id.
        self.catalog_course_run = CourseRunFactory(
            key=unicode(self.course.id),
            marketing_url='test_marketing_url'
        )

    def get_course_overview_marketing_url(self, course_id):
        """
        Get course overview marketing url.
        """
        return CourseOverview.objects.get(id=course_id).marketing_url

    def test_marketing_url_on_sync(self, mock_catalog_course_runs):
        """
        Verify course overview's marketing url after the execution of management command.
        """
        mock_catalog_course_runs.return_value = [self.catalog_course_run]
        earlier_marketing_url = self.get_course_overview_marketing_url(self.course.id)

        call_command('sync_course_runs')
        updated_marketing_url = self.get_course_overview_marketing_url(self.course.id)
        self.assertNotEqual(earlier_marketing_url, updated_marketing_url)
        self.assertEqual(updated_marketing_url, 'test_marketing_url')

    def test_course_overview_does_not_exist(self, mock_catalog_course_runs):
        """
        Verify no error in case if course run record does not have associated record in course overview.
        """
        mock_catalog_course_runs.return_value = [self.catalog_course_run, CourseRunFactory()]

        call_command('sync_course_runs')
        updated_marketing_url = self.get_course_overview_marketing_url(self.course.id)
        self.assertEqual(updated_marketing_url, 'test_marketing_url')

    @ddt.data(
        (2, 's '),
        (1, ' '),
        (0, 's '),
    )
    @ddt.unpack
    @mock.patch(COMMAND_MODULE + '.log.info')
    def test_command_logs(self, course_runs_count, course_word_end, mock_log_info, mock_catalog_course_runs):
        """
        Verify logging on execution of the command.
        """
        mock_catalog_course_runs.return_value = [CourseRunFactory() for _ in xrange(course_runs_count)]

        call_command('sync_course_runs')
        self.assertEqual(mock_log_info.call_count, 2)
        mock_log_info.assert_any_call('Fetching course runs from catalog service.')
        mock_log_info.assert_any_call(
            'Ended, %d course%sretrieved from catalog service.',
            course_runs_count,
            course_word_end,
        )
