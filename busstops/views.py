"View definitions."
from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import DetailView
from django.contrib.gis.geos import Polygon
from busstops.models import Region, StopPoint, AdminArea, Locality, District, Operator, Service


def index(request):
    "The home page with a list of regions"
    context = {
        'regions': Region.objects.all()
    }
    return render(request, 'index.html', context)


def cookies(request):
    "Cookie policy"
    return render(request, 'cookies.html')


def data(request):
    "Data sources"
    return render(request, 'data.html')


def hugemap(request):
    "The biggish JavaScript map"
    return render(request, 'map.html')


def stops(request):
    """
    JSON endpoint accessed by the JavaScript map,
    listing the active StopPoints within a rectangle,
    in standard GeoJSON format
    """

    bounding_box = Polygon.from_bbox(
        [request.GET[key] for key in ('xmin', 'ymin', 'xmax', 'ymax')]
    )
    results = StopPoint.objects.filter(
        latlong__within=bounding_box, active=True
    )

    data = {
        'type': 'FeatureCollection',
        'features': []
    }
    for stop in results:
        data['features'].append(
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [stop.latlong.x, stop.latlong.y]
                },
                'properties': {
                    'name': str(stop),
                    'url': stop.get_absolute_url()
                    }
                }
            )
    return JsonResponse(data)


def search(request):
    """
    A list of up to 10 localities
    whose names all contain the `request.GET['q']` string
    """
    data = []
    query = request.GET.get('q')
    if query:
        query = query.strip()
        for locality in Locality.objects.filter(name__icontains=query)[:12]:
            data.append({
                'name': locality.get_qualified_name(),
                'url':  locality.get_absolute_url()
            })
    return JsonResponse(data, safe=False)


class RegionDetailView(DetailView):
    "A single region and the administrative areas in it"

    model = Region

    def get_context_data(self, **kwargs):
        context = super(RegionDetailView, self).get_context_data(**kwargs)

        context['areas'] = AdminArea.objects.filter(region=self.object).order_by('name').distinct() # TODO exclude national coach?
        context['operators'] = Operator.objects.filter(region=self.object, service__isnull=False).distinct().order_by('name')

        return context


class AdminAreaDetailView(DetailView):
    "A single administrative area, and the districts, localities (or stops) in it"

    model = AdminArea

    def get_context_data(self, **kwargs):
        context = super(AdminAreaDetailView, self).get_context_data(**kwargs)

        # Districts in this administrative area
        context['districts'] = District.objects.filter(admin_area=self.object).distinct()

        # Districtless localities in this administrative area
        context['localities'] = Locality.objects.filter(
            admin_area_id=self.object.id,
            district=None,
            parent=None,
        ).exclude(stoppoint=None, locality=None).distinct().order_by('name')

        # National Rail/Air/Ferry stops
        if len(context['localities']) == 0 and len(context['districts']) == 0:
            context['stops'] = StopPoint.objects.filter(
                admin_area=self.object,
                active=True
            ).order_by('common_name')

        context['breadcrumb'] = [self.object.region]
        return context


class DistrictDetailView(DetailView):
    "A single district, and the localities in it"

    model = District

    def get_context_data(self, **kwargs):
        context = super(DistrictDetailView, self).get_context_data(**kwargs)
        context['localities'] = Locality.objects.filter(
            district=self.object,
            parent=None
        ).exclude(stoppoint=None, locality=None).distinct().order_by('name')
        context['breadcrumb'] = [self.object.admin_area.region, self.object.admin_area]
        return context


class LocalityDetailView(DetailView):
    "A single locality, its children (if any), and  the stops in it"

    model = Locality

    def get_context_data(self, **kwargs):
        context = super(LocalityDetailView, self).get_context_data(**kwargs)

        context['stops'] = StopPoint.objects.filter(
            locality=self.object,
            active=True
        ).order_by('common_name')

        context['localities'] = Locality.objects.filter(
            Q(stoppoint__active=True) |
            Q(locality__stoppoint__active=True),
            parent=self.object,
        ).distinct().order_by('name')

        context['services'] = Service.objects.filter(
            stops__locality=self.object
        ).distinct().order_by('service_code')

        context['breadcrumb'] = filter(None, [
            self.object.admin_area.region,
            self.object.admin_area,
            self.object.district,
            self.object.parent
        ])

        return context


class StopPointDetailView(DetailView):
    "A stop, other stops in the same area, and the services servicing it"

    model = StopPoint

    def get_context_data(self, **kwargs):
        context = super(StopPointDetailView, self).get_context_data(**kwargs)
        if self.object.stop_area_id is not None:
            context['nearby'] = StopPoint.objects.filter(
                stop_area=self.object.stop_area_id
            ).exclude(atco_code=self.object.atco_code).order_by('atco_code')
        context['services'] = Service.objects.filter(stops=self.object).order_by('service_code')
        context['breadcrumb'] = filter(None, [
            self.object.admin_area.region,
            self.object.admin_area,
            self.object.locality.district,
            self.object.locality.parent,
            self.object.locality,
        ])
        return context


class OperatorDetailView(DetailView):
    "An operator and the services it operates"

    model = Operator

    def get_context_data(self, **kwargs):
        context = super(OperatorDetailView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.filter(operator=self.object).order_by('service_code')
        context['breadcrumb'] = [self.object.region]
        return context


class ServiceDetailView(DetailView):
    "A service and the stops it stops at"

    model = Service

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)
        context['operators'] = self.object.operator.all()

        if bool(context['operators']):
            context['breadcrumb'] = [self.object.region, context['operators'][0]]
        context['stops'] = self.object.stops.all()
        return context
