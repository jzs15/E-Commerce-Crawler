from celery import task
from crawler import jdEngine, azEngine, snEngine, tbEngine

@task()
def Task_print():
    print('Run Task')

@task()
def Task_az(message):
    az = azEngine.AZEngine()
    az.run()
    return message

@task()
def Task_jd(message):
    jd = jdEngine.JDEngine()
    jd.run()
    return message

@task()
def Task_sn(message):
    sn = snEngine.SDEngine()
    sn.run()
    return message


@task()
def Task_tb(message):
    tb = tbEngine.TBEngine()
    tb.run()
    return message
