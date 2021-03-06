from .import_bushub import Command as BusHubCommand


class Command(BusHubCommand):
    source_name = 'Hotel Hoppa'
    url = 'http://portal.hotelhoppa.co.uk/api/buses/nearby?latitude&longitude'

    def get_vehicle(self, item):
        item['OperatorRef'] = 'NXHH'
        return super().get_vehicle(item)
