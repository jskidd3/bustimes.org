from time import sleep
from datetime import timedelta
from ciso8601 import parse_datetime_as_naive
from requests.exceptions import RequestException
from django.utils import timezone
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models import Extent
from busstops.models import Service, StopPoint
from ...models import VehicleLocation, VehicleJourney
from ..import_live_vehicles import ImportLiveVehiclesCommand


def get_latlong(item):
    return Point(item['geo']['longitude'], item['geo']['latitude'])


class Command(ImportLiveVehiclesCommand):
    url = 'http://api.otrl-bus.io/api/bus/nearby'
    source_name = 'Go-Ahead'
    operators = {
        'GOEA': ('KCTB', 'CHAM', 'HEDO'),
        'CSLB': ('OXBC', 'CSLB', 'THTR'),
        'GNE': ('GNEL',),
        'BH': ('BHBC',),
        'SQ': ('SVCT',),
        'TT': ('TDTR',),
    }

    opcos = {
        'eastangliabuses': ('KCTB', 'CHAM'),
        'oxford': ('OXBC', 'CSLB', 'THTR'),
        'gonortheast': ('GNEL',),
        'brightonhove': ('BHBC',),
        'swindon': ('TDTR',),
    }

    @staticmethod
    def get_datetime(item):
        return timezone.make_aware(parse_datetime_as_naive(item['recordedTime']))

    def get_vehicle(self, item):
        vehicle = item['vehicleRef']
        operator, fleet_number = item['vehicleRef'].split('-', 1)
        operators = self.operators.get(operator)
        if not operators:
            print(operator)
        defaults = {
            'source': self.source
        }
        if fleet_number.isdigit():
            defaults['fleet_number'] = fleet_number

        return self.vehicles.get_or_create(defaults, code=vehicle)

    def get_bounding_boxes(self, extent):
        extent = extent['latlong__extent']
        lng = extent[0]
        while lng <= extent[2]:
            lat = extent[1]
            while lat <= extent[3]:
                yield (lng, lat)
                lat += 0.2
            lng += 0.2

    def get_items(self):
        for opco in self.opcos:
            for operator in self.opcos[opco]:
                stops = StopPoint.objects.filter(service__operator=operator, service__current=True)
                extent = stops.aggregate(Extent('latlong'))
                stops = stops.filter(stopusageusage__datetime__lt=self.source.datetime + timedelta(minutes=5),
                                     stopusageusage__datetime__gt=self.source.datetime - timedelta(hours=1),
                                     stopusageusage__journey__service__operator=operator)
                for lng, lat in self.get_bounding_boxes(extent):
                    bbox = Polygon.from_bbox(
                        (lng - 0.1, lat - 0.1, lng + 0.1, lat + 0.1)
                    )
                    if stops.filter(latlong__within=bbox).exists():
                        params = {'lat': lat, 'lng': lng}
                        headers = {'opco': opco}
                        try:
                            response = self.session.get(self.url, params=params, timeout=30, headers=headers)
                            for item in response.json()['data']:
                                yield item
                        except (RequestException, KeyError):
                            continue
                        sleep(1)

    def get_journey(self, item, vehicle):
        journey = VehicleJourney()

        journey.code = str(item['datedVehicleJourney'])
        journey.destination = item['destination']['name']
        journey.route_name = item['lineRef']

        operator, fleet_number = item['vehicleRef'].split('-', 1)
        operators = self.operators.get(operator)
        if not operators:
            print(operator)

        if operators:
            if vehicle.latest_location and vehicle.latest_location.journey.code == journey.code and (
                                           vehicle.latest_location.journey.route_name == journey.route_name
            ):
                journey.service = vehicle.latest_location.journey.service
            else:
                if item['lineRef'] == 'CSR' and operators[0] == 'BHBC':
                    item['lineRef'] = 'CSS'
                services = Service.objects.filter(operator__in=operators, line_name__iexact=item['lineRef'],
                                                  current=True)
                try:
                    try:
                        journey.service = self.get_service(services, get_latlong(item))
                    except Service.MultipleObjectsReturned:
                        destination = item['destination']['ref']
                        journey.service = services.filter(stops__locality__stoppoint=destination).distinct().get()
                except (Service.DoesNotExist, Service.MultipleObjectsReturned) as e:
                    print(e, operators, item['lineRef'])

                if journey.service:
                    try:
                        operator = journey.service.operator.get()
                        if vehicle.operator_id != operator.id:
                            vehicle.operator_id = operator.id
                            vehicle.save()
                    except journey.service.operator.model.MultipleObjectsReturned:
                        pass

        return journey

    def create_vehicle_location(self, item):
        bearing = item['geo']['bearing']
        if bearing == 0 and item['vehicleRef'].startswith('BH-'):
            bearing = None
        return VehicleLocation(
            latlong=get_latlong(item),
            heading=bearing
        )
