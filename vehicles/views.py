import ciso8601
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import last_modified
from django.views.generic.detail import DetailView
from django.utils import timezone
from busstops.views import get_bounding_box
from .models import Vehicle, VehicleLocation, VehicleJourney, Operator, Service


def operator_vehicles(request, slug):
    operator = get_object_or_404(Operator, slug=slug)
    return render(request, 'operator_vehicles.html', {
        'breadcrumb': [operator.region, operator],
        'object': operator,
        'today': timezone.now().date(),
        'vehicles': operator.vehicle_set.order_by('fleet_number').select_related('vehicle_type',
                                                                                 'latest_location__journey__service')
    })


def vehicles(request):
    return render(request, 'vehicles.html')


def vehicles_last_modified(request):
    locations = VehicleLocation.objects.filter(current=True)
    if 'service' in request.GET:
        locations = locations.filter(journey__service=request.GET['service'])

    try:
        location = locations.values('datetime').latest('datetime')
        return location['datetime']
    except VehicleLocation.DoesNotExist:
        return


def location_json(location):
    journey = location.journey
    vehicle = journey.vehicle
    operator = vehicle and vehicle.operator
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': tuple(location.latlong),
        },
        'properties': {
            'vehicle': vehicle and {
                'url': vehicle.get_absolute_url(),
                'name': str(vehicle),
                'type': vehicle.vehicle_type and str(vehicle.vehicle_type),
            },
            'operator': operator and str(operator),
            'service': journey.service and {
                'line_name': journey.service.line_name,
                'url': journey.service.get_absolute_url(),
            },
            'journey': journey.code,
            'delta': location.early,
            'direction': location.heading,
            'datetime': location.datetime
        }
    }


@last_modified(vehicles_last_modified)
def vehicles_json(request):
    locations = VehicleLocation.objects.filter(current=True).order_by()

    try:
        bounding_box = get_bounding_box(request)
        locations = locations.filter(latlong__within=bounding_box)
    except KeyError:
        pass

    if 'service' in request.GET:
        locations = locations.filter(journey__service=request.GET['service'])

    locations = locations.select_related('journey__service', 'journey__vehicle__operator',
                                                             'journey__vehicle__vehicle_type')

    return JsonResponse({
        'type': 'FeatureCollection',
        'features': [location_json(location) for location in locations]
    })


def service_vehicles_history(request, slug):
    service = get_object_or_404(Service, slug=slug)
    date = request.GET.get('date')
    if date:
        try:
            date = ciso8601.parse_datetime(date).date()
        except ValueError:
            date = None
    journeys = service.vehiclejourney_set
    if not date:
        try:
            date = journeys.values_list('datetime', flat=True).latest('datetime').date()
        except VehicleJourney.DoesNotExist:
            date = timezone.now().date()
    journeys = journeys.filter(datetime__date=date).select_related('vehicle').prefetch_related('vehiclelocation_set')
    operator = service.operator.select_related('region').first()
    return render(request, 'vehicles/vehicle_detail.html', {
        'breadcrumb': [operator.region, operator, service],
        'date': date,
        'object': service,
        'journeys': journeys
    })


class VehicleDetailView(DetailView):
    model = Vehicle
    queryset = model.objects.select_related('operator', 'operator__region')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.operator:
            context['breadcrumb'] = [self.object.operator.region, self.object.operator]
        date = self.request.GET.get('date')
        if date:
            try:
                date = ciso8601.parse_datetime(date).date()
            except ValueError:
                date = None
        journeys = self.object.vehiclejourney_set
        if not date:
            try:
                date = journeys.values_list('datetime', flat=True).latest('datetime').date()
            except VehicleJourney.DoesNotExist:
                date = timezone.now().date()
        context['date'] = date
        journeys = journeys.filter(datetime__date=date)
        context['journeys'] = journeys.select_related('service').prefetch_related('vehiclelocation_set')
        return context