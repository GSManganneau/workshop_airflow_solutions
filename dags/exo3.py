from utils.parsing import parse_data_from_apis
from airflow import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime(2019, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG('workshop_airflow_exo_3',
          default_args=default_args,
          schedule_interval="0 6 * * *")

get_data_from_api = SimpleHttpOperator(
    task_id='get_data_from_api',
    method='GET',
    http_conn_id='navitia',
    endpoint='journeys?from=2.2728894%3B48.8812988&to=2.295016%3B48.873779&',
    headers={'Authorization': '9cdfa8dd-4ed8-4411-a6eb-690d361fddf6'},
    xcom_push=True,
    dag=dag)

get_weather = SimpleHttpOperator(
    task_id='get_weather',
    method='GET',
    http_conn_id='weather_api',
    endpoint='v1/current.json?key=c285ac3bd7f84e88904144311182808&q=Paris',
    xcom_push=True,
    dag=dag)


parse_data_from_apis = PythonOperator(
    task_id='parse_data_from_apis',
    provide_context=True,
    python_callable=parse_data_from_apis,
    dag=dag)

send_mail_walk = EmailOperator(
    task_id='send_mail_walk',
    to=['xavier.durand-smet@openvalue.fr'],
    subject="It's sunny!",
    html_content="You can walk to your destination: {{ task_instance.xcom_pull(task_ids='parse_data_from_apis', key='destination') }}",
    dag=dag)

send_mail_take_metro = EmailOperator(
    task_id='send_mail_take_metro',
    to=['xavier.durand-smet@openvalue.fr'],
    subject="Bad weather, take the metro!",
    html_content="Your arrival time is: {{ task_instance.xcom_pull(task_ids='parse_data_from_apis', key='arrival_time') }}",
    trigger_rule=TriggerRule.ALL_FAILED,
    dag=dag)

get_weather >> parse_data_from_apis
get_data_from_api >> parse_data_from_apis
parse_data_from_apis >> send_mail_walk
parse_data_from_apis >> send_mail_take_metro









