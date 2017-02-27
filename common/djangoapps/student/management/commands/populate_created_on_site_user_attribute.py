"""
Command created to back-populate domain of the site the user account was created on.
"""

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from student.models import UserAttribute, Registration


class Command(BaseCommand):
    """
    This commands back-populate domain of the site the user account was created on.
    """
    help = """./manage.py lms populate_created_on_site_user_attribute --users <user_id1>,<user_id2>...
           '--activation-keys <key1>,<key2>... --site-domain <site_domain> --settings=devstack"""

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            '--users',
            help='Enter user ids.',
            type=str
        )
        parser.add_argument(
            '--activation-keys',
            help='Enter activation keys.',
            type=str
        )
        parser.add_argument(
            '--site-domain',
            required=True,
            help='Enter an existing site domain.',
        )

    @staticmethod
    def comma_separated_str_to_list(comma_separated_str):
        if not comma_separated_str:
            return []
        return [item for item in comma_separated_str.split(',')]

    def handle(self, *args, **options):
        site_domain = options['site_domain']
        user_ids = self.comma_separated_str_to_list(options.get('users'))
        activation_keys = self.comma_separated_str_to_list(options.get('activation_keys'))

        if not user_ids and not activation_keys:
            raise CommandError('You must provide user ids or activation keys.')

        try:
            Site.objects.get(domain__exact=site_domain)
        except Site.DoesNotExist:
            raise CommandError('Given site domain does not exist in the system.')

        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                if not UserAttribute.get_user_attribute(user, 'created_on_site'):
                    UserAttribute.set_user_attribute(user, 'created_on_site', site_domain)
            except User.DoesNotExist:
                self.stdout.write("This user id [%s] does not exist", user_id)

        for key in activation_keys:
            try:
                user = Registration.objects.get(activation_key=key).user
                if not UserAttribute.get_user_attribute(user, 'created_on_site'):
                    UserAttribute.set_user_attribute(user, 'created_on_site', site_domain)
            except Registration.DoesNotExist:
                self.stdout.write("This activation key [%s] does not exist", key)
