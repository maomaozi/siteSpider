import os
import re

import taskexec

import commands
import sqlite3 as sql
import config as cfg

conn = sql.connect("./task.db")
print("Task database connected")
remove_illegle = re.compile(r'[^a-zA-Z0-9]', re.S)

def create_spider_script(domain, spider_name, spider_allow_domain, spider_start_url, request_delay):
    if domain == 'localhost' or domain == '127.0.0.1':

        if len(spider_name) >= 3 and spider_name != 'template':
            spider_name = remove_illegle.sub('', spider_name) + "Spider"
        else:
            return -1

        with open(cfg.SPIDER_TEMPLATE_FILE, 'rb') as f:
            template = f.read()

            script = template % (spider_name, spider_name,
                                 request_delay, spider_allow_domain,
                                 spider_start_url, spider_name, spider_name)

            script_fullpath = os.path.join(cfg.SPIDER_DIR, spider_name + '.py')
            if os.path.exists(script_fullpath):
                return -1

            with open(script_fullpath, 'wb') as f:
                f.write(script)

            return 0
    else:
        raise


def invoke_spider_task(domain, spider_name):
    if domain == 'localhost' or domain == '127.0.0.1':
        task_id = taskexec.rexec('localhost', 'scrapy crawl %sSpider' % spider_name, cfg.SCRAPY_HOME)
        taskexec.set_task_info(domain, task_id, {'spider_name': spider_name})
        return task_id

    else:
        raise


def get_spidername_by_taskid(domain, task_id):
    info_dict = taskexec.get_task_info(task_id, domain)
    return info_dict['spider_name']


def get_task_by_spidername(spider_name):
    spider_name = remove_illegle.sub('', spider_name)
    c = conn.cursor()
    r = c.execute("SELECT DOMAIN, TASK_ID FROM TASK WHERE SPIDER_NAME = '%s'" % spider_name)
    try:
        i = r.next()
        domain = i[0]
        task_id = i[1]
    except:
        return "", ""
    return domain, task_id


def get_all_spider_name():
    c = conn.cursor()
    r = c.execute("SELECT SPIDER_NAME FROM TASK")
    ids = []
    for row in r:
        ids.append(row[0])
    return ids


def spider_create(domain, spider_name, spider_allow_domain, spider_start_url, request_delay):
    spider_name = remove_illegle.sub('', spider_name)
    # spider_name += hex(random.randint(10000000, 99999999))[2:]
    if create_spider_script(domain, spider_name, spider_allow_domain, spider_start_url, request_delay) != 0:
        return -1

    if not len(spider_status(spider_name)[0]):
        c = conn.cursor()
        r = c.execute("INSERT INTO TASK (DOMAIN, TASK_ID, SPIDER_NAME) VALUES('%s', '%s', '%s')" % (domain, '', spider_name))
        conn.commit()

        return 0
    else:
        return -1


def spider_start(spider_name):
    spider_name = remove_illegle.sub('', spider_name)
    domain, pid = spider_status(spider_name)

    if domain != '' and pid == '':

        if not len(spider_name):
            return -1

        task_id = invoke_spider_task(domain, spider_name)

        try:
            c = conn.cursor()
            r = c.execute("UPDATE TASK set TASK_ID = '%s' WHERE SPIDER_NAME = '%s'" % (task_id, spider_name))
            conn.commit()
        except:
            spider_stop(spider_name)
            conn.unroll()

        return 0
    else:
        return -1


def spider_stop(spider_name):
    spider_name = remove_illegle.sub('', spider_name)
    domain, pid = spider_status(spider_name)

    # TODO: need handle SQL failed satuation
    if pid != '':
        if taskexec.rexec(domain, "kill -9 %s" % pid) >= 0:
            c = conn.cursor()
            r = c.execute("UPDATE TASK set TASK_ID = '%s' WHERE SPIDER_NAME = '%s'" % ("", spider_name))
            conn.commit()
            return 0
        else:
            return -1
    else:
        return -1


def spider_delete(spider_name):
    spider_name = remove_illegle.sub('', spider_name)
    domain, pid = spider_status(spider_name)

    if domain == '':
        return -1
    elif pid != '':
        return -1
    else:
        if spider_name != 'template':
            c = conn.cursor()
            r = c.execute("DELETE from TASK WHERE SPIDER_NAME = '%s'" % spider_name)
            conn.commit()

            taskexec.rexec(domain, "rm -f %s" % os.path.join(cfg.SPIDER_DIR, spider_name + 'Spider.py'))
        else:
            return -1
        return 0


def spider_status(spider_name):
    spider_name = remove_illegle.sub('', spider_name)
    if not len(spider_name):
        return '', ''

    domain, task_id = get_task_by_spidername(spider_name)

    if len(domain) and not len(task_id):
        return domain, ''

    if not len(domain) and not len(task_id):
        return '', ''

    task_lst = taskexec.list_tasks(domain)

    if task_id not in task_lst:
        c = conn.cursor()
        r = c.execute("UPDATE TASK set TASK_ID = '%s' WHERE SPIDER_NAME = '%s'" % ("", spider_name))
        conn.commit()
        return '', ''

    if domain == 'localhost' or domain == '127.0.0.1':

        pid0 = commands.getoutput('pgrep -of %s' % spider_name).split('\n')[0]
        pid1 = commands.getoutput('pgrep -of %s' % spider_name).split('\n')[0]

        if len(pid1) and pid1.isdigit() and pid0 == pid1:
            return domain, pid1
        else:
            c = conn.cursor()
            r = c.execute("UPDATE TASK set TASK_ID = '%s' WHERE SPIDER_NAME = '%s'" % ("", spider_name))
            conn.commit()
            return '', ''
    else:
        raise


    def get_spider_log(spider_name):

        spider_name = remove_illegle.sub('', spider_name)
        if not len(spider_name):
            return -1

        domain, task_id = get_task_by_spidername(spider_name)

        if task_id == '':
            return -1

        return taskexec.get_log_tail_by_taskid(domain, task_id)


if __name__ == "__main__":
    print spider_create("localhost", "uestc", "uestc.edu.cn", "http://uestc.edu.cn", 2)
    print get_all_spider_name()
    print spider_status('uestc')
    print spider_start("uestc")
    print spider_status('uestc')
    print spider_stop("uestc")
    print spider_status('uestc')
    print spider_delete("uestc")
    print get_all_spider_name()
