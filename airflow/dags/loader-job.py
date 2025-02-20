import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner'                 : 'airflow',
    'description'           : 'Document loader to vector store',
    'depend_on_past'        : False,
    'start_date'            : datetime(2024, 1, 1),
    'email_on_failure'      : False,
    'email_on_retry'        : False,
    'retries'               : 1,
    'retry_delay'           : timedelta(minutes=5)
}

with DAG('doc_loader_dag', default_args=default_args, schedule_interval="@once", catchup=False) as dag:
    start_dag = DummyOperator(
        task_id='start_dag'
        )

    end_dag = DummyOperator(
        task_id='end_dag'
        )
    
    t1 = BashOperator(
        task_id='print_current_date',
        bash_command='date'
        )
        
    t2 = DockerOperator(
        task_id='document_loader',
        image='docloader_task',
        container_name='document_loader',
        api_version='auto',
        auto_remove=True,
        command="",
        environment={
                  'PG_VECTOR_PWD': os.environ["PG_VECTOR_PWD"]
                },
        docker_url="tcp://docker-proxy:2375",
        network_mode="container:postgres_server",
        mount_tmp_dir = False
        )

    t3 = BashOperator(
        task_id='print_hello',
        bash_command='echo "hello world"'
        )

    start_dag >> t1 
    
    t1 >> t2 >> t3

    t3 >> end_dag
    