from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta
import pendulum

default_args = {
    'owner': 'nfox',
    'depends_on_past': False,
    'start_date': pendulum.datetime(year=2022, month=6, day=1).in_timezone('Europe/Moscow'),
    'email': ['norteply@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}
dag = DAG('hello_world', description='Hello World DAG',
          schedule_interval='0 12 * * *',
          start_date=datetime(2023, 1, 1
                              ), catchup=False)

def print_hello (): 
    return 'Hello world from Airflow DAG!' 

def skipp():
    return 99

dag2 = DAG( 'hello_world1' , description= 'Hello World DAG' , 
          schedule_interval= '0 12 * * *' , 
          start_date=datetime( 2023 , 1 , 1
          ), catchup= False ) 

hello_operator2 = PythonOperator(task_id= 'hello_task2' , python_callable=print_hello, dag=dag2)
skipp_operator2 = PythonOperator(task_id= 'skip_task2' , python_callable=skipp, dag=dag2)
hello_file_operator2 = BashOperator(task_id= 'hello_file_task2' , bash_command='python3.8 /home/alex/s6t2.py', dag=dag2)
hello_operator2 >> skipp_operator2 >> hello_file_operator2


hello_operator = BashOperator(
    task_id='hello_task', bash_command='echo Hello from Airflow', dag=dag)
hello_file_operator = BashOperator(
    task_id='hello_file_task', bash_command='sh /Users/nfox/Documents/my_docks/data_science/MIPT/2_semester/etl/s6.sh ', dag=dag)
skipp_operator = BashOperator(
    task_id='skip_task', bash_command='exit 99', dag=dag)
hello_operator >> hello_file_operator >> skipp_operator
