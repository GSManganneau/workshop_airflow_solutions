from utils.parsing_apis import parse_journey
from airflow import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime(2019, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG('workshop_airflow_exo_1',
          default_args=default_args,
          schedule_interval="0 6 * * *")

get_data_from_api = SimpleHttpOperator(
    task_id='get_data_from_api',
    method='GET',
    http_conn_id='navitia',
    endpoint='journeys?from=2.2728894%3B48.8812988&to=2.2950275%3B48.8737917&',
    headers={'Authorization': '9cdfa8dd-4ed8-4411-a6eb-690d361fddf6'},
    xcom_push=True,
    dag=dag)


parse_data_from_api = PythonOperator(
    task_id='parse_json',
    provide_context=True,
    python_callable=parse_journey,
    dag=dag)

send_mail = EmailOperator(
    task_id='send_mail',
    to=['guy-stephane.manganneau@openvalue.fr'],
    subject="Your next trip!!!",
    html_content="Available journeys : {{ task_instance.xcom_pull(task_ids='parse_json',key='itinerary') }}",
    dag=dag)

get_data_from_api >> parse_data_from_api >> send_mail





