import os
import sys
import random

import config as cfg


def rexec(domain, cmd, cwd='./'):
    log_id = -1
    if domain == 'localhost' or domain == '127.0.0.1':
        if not os.path.exists(cfg.TMP_DIR):
            os.mkdir(cfg.TMP_DIR)

        retry = 0
        log_id = hex(random.randint(10000000, 99999999))[2:]
        tmp_filename = "%s.log" % log_id

        while os.path.exists('%s' % os.path.join(cfg.TMP_DIR, tmp_filename)) and retry < 3:
            log_id = hex(random.randint(10000000, 99999999))[2:]
            tmp_filename = "%s.log" % log_id
            retry += 1

        if retry == 3:
            return -1

        os.system("cd %s && nohup %s >%s 2>&1 &" % (cwd, cmd, os.path.join(cfg.TMP_DIR, tmp_filename)))
        #print("cd %s && nohup %s >%s 2>&1 &" % (cwd, cmd, os.path.join(cfg.TMP_DIR, tmp_filename)))
    else:
        raise

    return log_id


def list_tasks(domain):
    task_lst = []
    if domain == 'localhost' or domain == '127.0.0.1':
        try:
            dir_list = os.listdir(cfg.TMP_DIR)
        except OSError, e:
            return task_lst

        for file_name in dir_list:
            full_path = os.path.join(cfg.TMP_DIR, file_name)
            name_seg = full_path.split('.')
            if os.path.isfile(full_path) and len(name_seg) and name_seg[-1] == 'tsk':
                task_lst.append(name_seg[0].split('/')[-1])
    else:
        raise

    return task_lst


def set_task_info(domain, task_id, info):
    if domain == 'localhost' or domain == '127.0.0.1':
        if type(info) != dict:
            raise ValueError("Info must be dict")

        taskfile_fullpath = os.path.join(cfg.TMP_DIR, task_id + '.tsk')

        with open(taskfile_fullpath, 'wb') as f:
            f.write(str(info))
    else:
        raise


def get_task_info(task_id, domain):
    if domain == 'localhost' or domain == '127.0.0.1':
        taskfile_fullpath = os.path.join(cfg.TMP_DIR, task_id + '.tsk')

        if not os.path.exists(taskfile_fullpath):
            raise OSError("Task id=%s not found" % task_id)

        with open(taskfile_fullpath, 'rb') as f:
            return eval(f.read())
    else:
        raise


def get_log_tail_by_taskid(domain, task_id, size=1000):
    logfile_fullpath = os.path.join(cfg.TMP_DIR, task_id + '.log')

    if domain == 'localhost' or domain == '127.0.0.1':

        if not os.path.exists(logfile_fullpath):
            return -1

        filesize = os.path.getsize(logfile_fullpath)
        with open(logfile_fullpath, 'rb') as f_log:
            f_log.seek(-size if filesize > size else (-filesize), 2)
            res = f_log.read()
        return res
    else:
        raise

if __name__ == "__main__":
    print(get_log_tail_by_taskid('localhost', '1'))
