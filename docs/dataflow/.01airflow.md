# Airflow

## Orquestación de flujos de trabajo

## Apache Airflow

Apache Airflow is the most popular open-source workflow orchestration platform (at the time of this writing). The project started out as an internal project at Airbnb late in 2014. It materialized from the general need to solve the common problem of increasingly complex workflows in a centralized way, thus enabling programmatic authoring and scheduling of jobs through a simple UI. Essentially, a job defines its own schedule and configuration within a simple Python script. This code-driven approach to job scheduling allows for a level of rich customization that is difficult to achieve with static configuration alone. You may be thinking to yourself that this is great for a company the size of Airbnb, but why would you need to use Airflow, or any kind of automated workflow orchestrator?

## Puesta en marcha

https://medium.com/swlh/using-airflow-to-schedule-spark-jobs-811becf3a960

https://anant.us/blog/modern-business/airflow-and-spark-running-spark-jobs-in-apache-airflow/
https://github.com/yTek01/apache-airflow-spark/blob/main/scripts/airflow_installer.sh

## Hola Airflow

Una vez arrancado, entraremos mediante el usuario `airflow` y contraseña `airflow`.

From the Airflow main screen, you’ll see all your job definitions, job metadata, and statistics about the prior runs (if any) across each job. This is also a branching-off point for general security and common administration tasks.

For starters, your job definitions are officially called DAGs. This is because each job is defined as a directed acyclic graph (DAG) of one or more operations, and essentially each DAG is in and of itself a pipeline operation or an entire complex workflow.

Para probar Airflow, vamos a ejecutar uno de los ejemplos instalados, en concreto `example_bash_operator`.

## Componentes

### Tareas

Within each DAG, there exists a series of one or more tasks that are executed to fulfill the obligations set forth by a given DAG. Tasks are the basic unit of execution in Airflow, which is also the case for Spark applications. The overlap here is that with Spark, you have jobs, and each job is comprised of stages that distribute tasks. With Airflow, your DAGs are composed of tasks, which run in a specific pre-defined order, and work is completed within the context of the Airflow executor managing a specific DAG. Tasks can execute arbitrary code using operators, and so each DAG can handle many tasks. Each task can execute local or remotely depending on the operator in use.

### Operadores

Airflow operators are templated tasks. Think of this as a blueprint that can be reused to wrap generic use cases, enabling common Python code to be reused to fulfill a given operation. In the example DAG (example_bash_operator), you were introduced to two of the core Airflow operators—BashOperator and DummyOperator.
The BashOperator does exactly what you think it does; it will run a bash (or command-line) operation. The DummyOperator is used to ensure the DAG has a final common node in a graph of tasks. The DummyOperator can also be used as a placeholder while you are building more complicated DAGs

Más adelante veremos operadores más específicos, como SparkSubmitOperator y SparkSQLOperator para interactuar con Spark.

### Planificadores y Ejecutores

The executor is the process in Airflow responsible for kicking off the tasks in your DAG based on a schedule. For example, say you have a job that needs to be run every day at the end of the day. The properties for scheduling this DAG are shown in Listing 8-10.

``` python
DAG(
  dag_id="daily_active_users_reporting_job",
  start_date=days_ago(2),
  default_args=args,
  tags=["coffee_co","core"],
  schedule_interval="@daily",
)
```

DAG definitions are parsed by Airflow initially on startup, and periodically to support adding DAGs at runtime. When a new dag_id is encountered, the DAG metadata is written to the RDBMS and the scheduler executor process will trigger the DAG run (if the job is not disabled) as soon as the threshold of the start_date is crossed.

The schedule configured in Listing 8-10 sets the start_date to days_ago(2) with a schedule_interval of @daily. This is an example of a backfill job. It will look at today’s date (on the Airflow server) and rewind so that the prior two days run before it begins running on a daily schedule, which runs at the start of each day (or midnight). For more information you can look at the Cron Presets section under DAG Runs in the official Airflow documentation.

The Airflow executor waits for the scheduler to notify it that a DAG is ready to run. In fact, the executor itself runs within the scheduler process. Due to this relationship, you can only assign one mode of execution for a given Airflow cluster, given the tight coupling between scheduling and execution.

Airflow ships with several useful executors, offering local or remote styles of execution.

#### Local Execution

The SequentialExecutor or LocalExecutor can be used if you are running a small cluster. Local execution means that task execution will be collocated within the executor process, and the executor process itself runs inside the scheduler process. This process inception can be good for testing things out, but this pattern won’t scale to run multiple DAGs in parallel.

#### Remote Execution

For production environments where you have critical workflows that must run, you have no choice but to use remote execution. This enables the workloads of multiple DAGS to be executed in parallel across a network of Airflow worker nodes. To view what execution mode your Airflow cluster is running in, execute the command shown in Listing 8-11.
docker exec \
  -it airflow_airflow-webserver_1 \
  airflow config get-value core executor
Listing 8-11Viewing the Airflow Executor Config
The output will show you the CeleryExecutor, which is one of the more popular remote executor options available in Airflow. The CeleryExecutor uses Redis for scheduling and distributes its work across the Airflow Worker processes. Let’s turn our attention now to integrating Apache Spark with Airflow.

## Interacción con Spark

Airflow is a robust external scheduler you can rely on to run your mission-critical Apache Spark batch jobs. Furthermore, workflow orchestration is becoming an essential data platform component used to automate increasingly complex data pipelines and meet the needs of many internal and external data customers. As you learned in Exercise 8-1, running a DAG on Airflow is a piece of cake (once you’ve learned the basics). To get started with Airflow and Spark, all that is needed is the Spark Airflow Provider, which enables you to use a few different Spark operators.

Let’s begin by using the version of Airflow you set up in Exercise 8-1. You’ll be executing the pip install commands directly on the webserver and worker Airflow containers because the Spark Python modules must be available locally.

pip install \
  --no-cache-dir \
  --user \
  apache-airflow-providers-apache-spark

Listing 8-14Install the Spark Provider Using Pip

When the DAG is triggered, for each independent DAG run, all tasks encapsulating the DAG will run until they have all succeeded or a critical task fails, thereby blocking the rest of the tasks from completing. In the real-world use, you’ll see worker nodes easily spanning tens to hundreds of instances, and at an even larger scale within enterprise clusters. Now imagine that you were tasked at ensuring that this full system was in sync, keeping in mind that you’d have to repeat this step for each deployment to ensure consistency. Would you want to be tasked with keeping everything in sync?

Of course not. This is clearly an anti-pattern, especially given we are running things using containers in the first place. Sure, you could add some scripts to run when the container is starting up, but that just means you are subject to potential runtime errors due to failed dependencies. You’ve probably seen such issues when centralized package repositories (like Pypi or Maven) have outages, or when package locations change (as is often the case with archived artifact versions).

## Referencias

https://www.youtube.com/watch?v=GIztRAHc3as

## Actividades

https://learning.oreilly.com/library/view/modern-data-engineering/9781484274521/html/505711_1_En_8_Chapter.xhtml

https://towardsdatascience.com/interconnecting-airflow-with-a-nifi-etl-pipeline-8abea0667b8a