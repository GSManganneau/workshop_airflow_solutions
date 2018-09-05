from datetime import datetime, timedelta
import json


def parse_section(section):
    from_ = section['from']['name']
    duration = section['duration']
    to = section['to']['name']
    if section['type'] == "street_network":
        mode = " by walking <br>"
        res = str(duration) + "s from " + from_ + " to " + to + mode
        return res
    elif section['type'] == "public_transport":
        network = section["display_informations"]["network"]
        code = section["display_informations"]["code"]
        direction = section["display_informations"]["direction"] + " <br>"
        return str(duration) + "s from " + from_ + " to " + to + " by " + network + " " + code + " direction " + direction
    else:
        return "this case is not handled yet"


def get_section(response, journey_id, section_id):
    if journey_id >= len(response['journeys']):
        raise BaseException("this journey doesn't exist")
    else:
        if section_id >= len(response['journeys'][journey_id]['sections']):
            raise BaseException("This section doesn't exist")
        else:
            section = response['journeys'][journey_id]['sections'][int(section_id)]
            return parse_section(section)


def parse_journey(**context):
    response_json = json.loads(context['task_instance'].xcom_pull(task_ids='get_data_from_api'))
    number_of_journeys = len(response_json['journeys'])
    itinerary = ""
    if number_of_journeys > 0:
        for i in range(0, number_of_journeys):
            departure_time = datetime.strptime(response_json['journeys'][i]['requested_date_time'], '%Y%m%dT%H%M%S')
            itinerary = itinerary + " Journey number " + str(i + 1) + ": <br>"
            itinerary = itinerary + "Departure time : " + str(departure_time) + "<br>"
            number_of_section = len(response_json['journeys'][i]['sections'])
            for j in range(0, number_of_section):
                itinerary = itinerary + get_section(response_json, i, j)
            arrival_time = datetime.strptime(response_json['journeys'][i]['arrival_date_time'], '%Y%m%dT%H%M%S')
            itinerary = itinerary + "Arrival time : " + str(arrival_time) + "<br>"
        print("itinerary", itinerary)
        context['task_instance'].xcom_push(key='itinerary', value=str(itinerary))
    else:
        raise BaseException("No journey for this demand")


time = "20180903T143000"


def check_if_time_to_leave(response):
    json_response = json.loads(response.content)
    arrival_time = datetime.strptime(json_response['journeys'][0]['arrival_date_time'], '%Y%m%dT%H%M%S')
    goal_time = datetime.strptime(time, '%Y%m%dT%H%M%S')
    print("goal_time + 5 min: " + str(goal_time + timedelta(minutes=5)))
    print("arrival_time: " + str(arrival_time))
    return goal_time + timedelta(minutes=5) < arrival_time


def parse_data_from_apis(**context):
    response_json = json.loads(context['task_instance'].xcom_pull(task_ids='get_data_from_api'))
    weather_json = json.loads(context['task_instance'].xcom_pull(task_ids='get_weather'))
    current_weather = weather_json['current']['condition']['text']
    print("weather is " + current_weather)
    if current_weather is not "Sunny":
        arrival_time = datetime.strptime(response_json['journeys'][0]['arrival_date_time'], '%Y%m%dT%H%M%S')
        context['task_instance'].xcom_push(key='arrival_time', value=str(arrival_time))
        raise BaseException("It is not sunny today!")
    context['task_instance'].xcom_push(key='destination',
                                       value=response_json['journeys'][0]['sections'][-1]['to']['address']['label'])
