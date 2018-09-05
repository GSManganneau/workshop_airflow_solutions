from utils.parsing import check_if_time_to_leave
from airflow import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.sensors import HttpSensor
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime(2019, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG('workshop_airflow_exo_2',
          default_args=default_args,
          schedule_interval="0 6 * * *")


wait_for_right_time = HttpSensor(
    task_id='wait_for_right_time',
    http_conn_id='navitia',
    endpoint='journeys?from=2.2728894%3B48.8812988&to=2.2950275%3B48.8737917&',
    headers={'Authorization': '9cdfa8dd-4ed8-4411-a6eb-690d361fddf6'},
    response_check=check_if_time_to_leave,
    dag=dag)




send_mail = EmailOperator(
    task_id='send_mail',
    to=['xavier.durand-smet@openvalue.fr'],
    subject="You need to leave now!",
    html_content="Leave now if you want to be on time!",
    dag=dag)

wait_for_right_time >> send_mail









