from os.path import join
from datetime import date
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from multigtfs.models import Feed
from ...models import Operator, Service, ServiceCode, DataSource
from .import_ie_gtfs import download_if_modified


class Command(BaseCommand):
    @staticmethod
    def process_gtfs(collection, feed):
        scheme = '{} GTFS'.format(collection)
        ServiceCode.objects.filter(scheme=scheme).delete()

        thebus = Operator.objects.update_or_create(id='thebus', name='TheBus', region_id='HI')[0]

        for route in feed.route_set.all():
            if collection == 'hi':
                route.long_name = route.long_name.replace('-', ' - ')
            service = Service.objects.update_or_create(
                {
                    'line_name': route.short_name,
                    'description': route.long_name,
                    'date': date.today(),
                    'region_id': 'HI',
                    'show_timetable': True
                },
                service_code='{}-{}'.format(collection, route.short_name)
            )[0]
            service.operator.add(thebus)
            ServiceCode.objects.update_or_create(
                service=service,
                scheme=scheme,
                code=route.route_id
            )
            print(route, route.short_name, route.long_name)

    @classmethod
    def handle_collection(cls, collection, url):
        print(collection)

        archive_name = join(settings.DATA_DIR, 'google_transit_{}.zip'.format(collection))
        # modified = download_if_modified(archive_name, url)

        source, _ = DataSource.objects.get_or_create(name=collection)

        # if not modified:
        #     return

        with transaction.atomic():
            feed = Feed.objects.get(name=collection)
            # feed = Feed.objects.create(name=collection)
            # feed.import_gtfs(archive_name)

            if collection == 'hi':
                cls.process_gtfs(collection, feed)
            elif collection == 'bordersbuses':
                scheme = '{} GTFS'.format(collection)
                ServiceCode.objects.filter(scheme=scheme).delete()
                services = Service.objects.filter(current=True, operator__in=['BORD', 'PERY'])
                for route in feed.route_set.all():
                    existing = services.filter(line_name=route.short_name)
                    if existing.exists():
                        print(route.short_name)
                        service = existing.first()
                        existing.exclude(pk=service.pk).update(current=False)
                        service.geometry = route.geometry
                        service.source = source
                        service.save()
                        ServiceCode.objects.update_or_create(
                            service=service,
                            scheme=scheme,
                            code=route.route_id
                        )
        # Feed.objects.filter(name=collection).exclude(id=feed.id).delete()

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Import data even if the GTFS feeds haven\'t changed')

    def handle(self, *args, **options):
        # # Hawaii
        # self.handle_collection('hi', 'http://webapps.thebus.org/transitdata/Production/google_transit.zip')

        # # West Midlands
        # self.handle_collection('tfwm', 'http://api.tfwm.org.uk/gtfs/tfwm_gtfs.zip?' + urlencode(settings.TFWM))

        for collection, url in [
            ('bordersbuses',
             'https://s3-eu-west-1.amazonaws.com/passenger-sources/bordersbuses/gtfs/bordersbuses_1556866091.zip')
        ]:
            self.handle_collection(collection, url)
