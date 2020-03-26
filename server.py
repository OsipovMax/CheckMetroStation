from aiohttp import web, ClientSession
import json


class Server:
    def __init__(self):
        application = web.Application()
        application.add_routes([web.post('/api/v1/metro/verificate/', self.post_handler)])
        web.run_app(application)

    async def post_handler(self, request):
        input_data = await request.json()
        set_input_stations = {metro_station for metro_station in input_data['stations list']}
        data_from_hh = await self.get_data('https://api.hh.ru/metro/1')
        set_statiton_from_hh = self.parse_data(data_from_hh)
        unchanged = list(set_statiton_from_hh.intersection(set_input_stations))
        updated = list(set_input_stations.difference(set_statiton_from_hh))
        deleted = list(set_statiton_from_hh.difference(set_input_stations))
        result = json.dumps({
            'unchanged': unchanged, 'update': updated, 'deleted': deleted}, ensure_ascii=False)
        return web.json_response(result)

    async def get_data(self, request_point):
        async with ClientSession() as session:
            async with session.get(request_point) as resp:
                return await resp.json()

    def parse_data(self, analyze_data):
        metro_stations_hh = set()
        for line in analyze_data['lines']:
            for station in line['stations']:
                metro_stations_hh.add(station['name'])
        return metro_stations_hh
