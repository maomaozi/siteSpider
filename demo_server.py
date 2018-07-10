import urllib
import json
import time
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify

import math

from indexer import searcher2
from indexer import bayes

import spider_manager as smgr

app = Flask(__name__, static_url_path='')


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/update/')
def update_page():
    return render_template('update.html')


@app.route('/capture/')
def capture_page():
    return render_template('capture.html')


@app.route('/update/start')
def start_update():
    search_engine = searcher2.get_instance()
    search_engine.start_update()
    return render_template('update.html')


@app.route('/update/stop')
def stop_update():
    search_engine = searcher2.get_instance()
    search_engine.abort_update()
    return render_template('update.html')


@app.route('/update/progress')
def get_progress():
    search_engine = searcher2.get_instance()
    is_running, val = search_engine.get_update_progress()
    return jsonify(status=is_running, progress=val)


@app.route('/search/')
def result_page():
    key = request.args.get('key', '')

    if key != '':
        page = request.args.get('page', 1, type=int)
        pagesize = request.args.get('pagesize', 10, type=int)

        key = urllib.unquote(key)
        search_engine = searcher2.get_instance()
        r = search_engine.create_query(key)
        items_num = search_engine.get_all_items_num(r)

        page_num = int(math.ceil(items_num / pagesize))

        res = search_engine.get_search_result(r, page, pagesize)

        return render_template('key.html', data=res, key=key, page_num=page_num, current_page=page)

    else:
        return render_template('key.html', data=[], key='', page_num=0, current_page=0)


@app.route('/model/', methods=['GET', 'POST'])
def online_learning():
    url = request.values.get("text", 0)
    classType = request.values.get("classType", 0)
    if url != '' and classType != '':
        search_engine = searcher2.get_instance()
        content = search_engine.get_content_from_url(url)
        bayesInstance = bayes.get_instance()
        bayesInstance.learning(content, int(classType))
        return jsonify(success=1)
    else:
        return jsonify(success=0)


@app.route('/capture/list_spiders', methods=['GET', 'POST'])
def list_spiders():
    spider_lst = smgr.get_all_spider_name()

    list = []
    if len(spider_lst):
        pass
    else:
        # TODO no spider job
        return jsonify(list)

    for item in spider_lst:
        domain, pid = smgr.spider_status(item)
        if len(domain) and not len(pid):
            # TODO: spider is created but not running
            # TODO: send domain to web page
            list.append({'domain': domain, 'spider_name': item, 'status': 0})
        elif len(domain) and len(pid):
            # TODO: spider is running
            # TODO: send domain to web page
            list.append({'domain': domain, 'spider_name': item, 'status': 1})
        else:
            # Should not reach here
            raise ValueError("Unknow error")
    return jsonify(list)


@app.route('/capture/add_spider', methods=['GET', 'POST'])
def add_spider():
    # TODO: get domain, spider_name, spider_allow_domain, spider_start_url, request_delay in request
    # spider_create(domain, spider_name, spider_allow_domain, spider_start_url, request_delay)
    # eg. spider_create("localhost", "uestc", "uestc.edu.cn", "http://uestc.edu.cn", 2)
    status = smgr.spider_create(request.values.get("domain", 0), request.values.get("spider_name", 0), request.values.get("spider_allow_domain", 0), request.values.get("spider_start_url", 0), int(request.values.get("request_delay", 0)))

    if status == 0:
        # TODO: success
        return jsonify(success=1)
    else:
        # TODO: failed
        return jsonify(success=0)


@app.route('/capture/get_spider_log', methods=['GET', 'POST'])
def get_spider_log():
    # TODO: spider_name in request
    log = smgr.get_spider_log(request.values.get("spider_name", 0))
    if log == -1:
        # TODO: show some error imformation
        return jsonify(success=1, log="No log for %s here" % request.values.get("spider_name", 0))
    else:
        # TODO: show log
        log = log.replace('\n', '</br>')
        return jsonify(success=1, log=log)


@app.route('/capture/start_spider', methods=['GET', 'POST'])
def start_spider():
    # TODO: spider_name in request
    status = smgr.spider_start(request.values.get("spider_name", 0))

    if status == 0:
        # TODO: success
        return jsonify(success=1)
    else:
        # TODO: failed
        return jsonify(success=0)


@app.route('/capture/stop_spider', methods=['GET', 'POST'])
def stop_spider():
    # TODO: spider_name in request
    status = smgr.spider_stop(request.values.get("spider_name", 0))

    if status == 0:
        # TODO: success
        return jsonify(success=1)
    else:
        # TODO: failed
        return jsonify(success=0)


@app.route('/capture/del_spider', methods=['GET', 'POST'])
def del_spider():
    # TODO: spider_name in request
    status = smgr.spider_delete(request.values.get("spider_name", 0))

    if status == 0:
        # TODO: success
        return jsonify(success=1)
    else:
        # TODO: failed
        return jsonify(success=0)



if __name__ == '__main__':
    searcher2.get_instance()
    app.run(host='0.0.0.0',
            port=8081)
