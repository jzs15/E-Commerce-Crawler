from celery import task
from crawler import jdEngine, azEngine, snEngine, tbEngine
from crawler.standardization import standardization


@task()
def Task_print():
    print('Run Task')

@task()
def Task_az(message):
    az = azEngine.AZEngine()
    az.run()
    standardization()
    return message

@task()
def Task_jd_1h(message):
    jd = jdEngine.JDEngine()
    jd.crawler('9987,653,655')
    standardization()
    return message

@task()
def Task_jd_3h(message):
    jd = jdEngine.JDEngine()
    jd.crawler('737,794,878')
    jd.crawler('670,671,673')
    jd.crawler('737,794,798')
    jd.crawler('737,794,880')
    standardization()
    return message

@task()
def Task_jd_6h(message):
    jd = jdEngine.JDEngine()
    jd.crawler('670,671,672')
    standardization()
    return message

@task()
def Task_sn(message):
    sn = snEngine.SDEngine()
    sn.run()
    standardization()
    return message


@task()
def Task_tb(message):
    tb = tbEngine.TBEngine()
    tb.run()
    standardization()
    return message
