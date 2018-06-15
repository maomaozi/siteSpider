# -*- coding: utf-8 -*-

import threading
import os, sys
import time
import logging

import helper
import bayes
import config as cfg

from whoosh.fields import Schema, TEXT, ID
import whoosh.index as windex
import whoosh.highlight as highlight
from whoosh.query import *
from whoosh.qparser import QueryParser

from jieba.analyse import ChineseAnalyzer


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %Y %H:%M:%S'
                    )

instance = None

RUN = True

class Ticker(object):
    def __init__(self):
        self.tick = True

    def run(self):
        global RUN
        while RUN:
            if self.tick:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(1.0)


class Searcher():
    def __init__(self):
        global RUN

        print('Initial searcher')

        self.schema = Schema(
            url=ID(stored=True, unique=True),
            store_path=TEXT(stored=True),
            timestamp=TEXT(stored=True),
            content=TEXT(stored=False, analyzer=ChineseAnalyzer())
        )

        try:
            print("Open index dir")
            self.my_idx = windex.open_dir(cfg.storage_dir)
        except:
            print("Index dir not found, create new index dir")
            self.my_idx = windex.create_in(cfg.storage_dir, self.schema)

        self.searcher = self.my_idx.searcher()

        self.content_reader = helper.content_reader()

        print("All documents: %s" % self.searcher.doc_count_all())
        print("Valid documents: %s" % self.searcher.doc_count())

        print("Init bayes model, may take some times...")
        self.bayesData = bayes.get_instance()

        RUN = True
        self.ticker = Ticker()
        self.ticker.tick = False
        threading.Thread(target=self.ticker.run).start()

        self.update_lock = threading.Lock()
        self.read_lock = threading.RLock()

        self.aborted_update = False
        self.is_update_in_progress = False
        self.update_progress = 0

    def to_hex(self, id):
        s = hex(id)
        if len(s) == 3:
            return '0' + s[-1]
        else:
            return s[-2:]

    def update(self, info, path):
        query = Term("url", info["url"])
        docs = self.searcher.search(query, limit=1)
        if len(docs) > 0:
            old_timestamp = float(docs[0]['timestamp'])
            new_timestamp = float(info['timestamp'])
            if new_timestamp - old_timestamp > cfg.update_elapse:
                self.writer.update_document(
                    url=info["url"].decode('utf-8'), store_path=path, timestamp=str(info["timestamp"]).decode('utf-8'),
                    content=helper.remove_html_js(info["content"]))
        else:
            self.writer.add_document(
                url=info["url"].decode('utf-8'), store_path=path, timestamp=str(info["timestamp"]).decode('utf-8'),
                content=helper.remove_html_js(info["content"]))

    def get_content_from_url(self, url):
        query = Term("url", url)
        docs = self.searcher.search(query, limit=1)

        if len(docs) == 0:
            return ''

        doc = docs[0]
        info = self.content_reader.read(doc["store_path"])
        return helper.remove_html_js(info["content"])


    def update_worker(self):
        if self.aborted_update:
            # 如果正在中止的过程中，不允许再启动更新线程
            print "Aborting update, cannot start update now"
            return
        if self.is_update_in_progress:
            # 如果有正在更新的过程，不允许再启动更新线程（未加锁控制，可能有bug）
            print "Update still in progress"
            return
        self.update_lock.acquire()
        try:
            print('Start update index')
            self.is_update_in_progress = True
            self.ticker.tick = True

            self.writer = self.my_idx.writer()

            target_dirs = os.listdir(cfg.cache_dir)

            for e, target_dir in enumerate(target_dirs):
                if self.aborted_update:
                    break

                site_path = os.path.join(cfg.cache_dir, target_dir)
                for j in range(0, 0xff + 1):
                    if self.aborted_update:
                        break
                    self.update_progress = (float(j) + 0xff * e) / 0xff / len(target_dirs)

                    path = os.path.join(site_path, self.to_hex(j))

                    if not os.path.exists(path):
                        continue

                    dir_list = os.listdir(path)

                    for cache_path in dir_list:
                        if self.aborted_update:
                            break
                        full_path = os.path.join(path, cache_path)
                        info = self.content_reader.read(full_path)

                        if info is None:
                            continue

                        self.update(info, full_path.decode('utf-8'))
                    sys.stdout.write('*')
                    sys.stdout.flush()

            if self.aborted_update:
                # 用户中断更新
                self.writer.cancel()
                print('Update aborted')
                return

            # commit的时候不允许查询
            self.read_lock.acquire()
            print('Commit updates')
            try:
                self.writer.commit()
                self.searcher.close()
                self.my_idx.close()

                self.my_idx = windex.open_dir(cfg.storage_dir)
                self.searcher = self.my_idx.searcher()

                print('Commit updates success')
            except:
                print('Commit updates failed')
            finally:
                self.read_lock.release()
        except NameError:
            pass
        except Exception, e:
            print('Update job failed', e)
        finally:
            self.update_lock.release()
            self.is_update_in_progress = False
            self.ticker.tick = False
            print('Update index finished')


    def start_update(self):
        self.update_progress = 0
        threading.Thread(target=self.update_worker).start()

    def abort_update(self):
        # 中断更新
        self.aborted_update = True

        # 等待获取更新锁，代表更新已经结束
        self.update_lock.acquire()
        self.aborted_update = False
        self.update_lock.release()

    def get_update_progress(self):
        return self.update_progress

    def create_query(self, kws):

        if len(kws) > cfg.max_keywords_length:
            print('keywords length must under %d' % cfg.max_keywords_length)
            kws = kws[:cfg.max_keywords_length]

        self.read_lock.acquire()

        try:
            query = QueryParser("content", self.schema).parse(kws)
            score_docs = self.searcher.search(query, limit=cfg.max_result_return)
        except:
            score_docs = []
        finally:
            self.read_lock.release()

        return kws, score_docs, len(score_docs)


    def get_all_items_num(self, kws_query):
        return kws_query[2] if kws_query[2] <= 100 else 100


    def get_search_result(self, kws_query, page=1, page_len=10):
        page -= 1
        res = []

        score_docs = kws_query[1]

        score_docs.fragmenter.maxchars = cfg.max_result_return
        score_docs.fragmenter.surround = cfg.preview_surround_length

        score_docs.formatter = highlight.HtmlFormatter()

        try:
            for i in range(page * page_len, (page + 1) * page_len):
                score_doc = score_docs[i]
                info = self.content_reader.read(score_doc["store_path"])

                if info is None:
                    continue

                title_start = info['content'].find('<title>')
                title_end = info['content'].find('</title>')

                if title_start != -1 and title_end != -1:
                    title = info['content'][title_start + 7: title_end]
                else:
                    title = kws_query[0]

                if len(title) > cfg.max_title_length:
                    title = title[:cfg.max_title_length] + '.....'

                text = helper.remove_html_js(info['content'])
                class_label = self.bayesData.contextTest(text)

                preview = score_doc.highlights("content", text=text)
                res.append({'url': score_doc["url"], 'title': title,
                            'preview': preview, 'classLable': class_label,
                            'snapshot': ''})
        except Exception, e:
            print "Get search result failed", e

        return res

    def __enter__(self):
        if self.my_idx is None:
            self.__init__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global RUN
        self.my_idx.close()
        self.my_idx = None
        self.searcher.close()
        self.searcher = None
        RUN = False
        print("Searcher destructed")

    def exit(self):
        self.__exit__(0, 0, 0)


def get_instance():
    global instance
    if instance is None:
        instance = Searcher()
    return instance

if __name__ == '__main__':
    with get_instance() as s:
        s.start_update()

        for i in range(3):
            print s.get_update_progress()
            time.sleep(1)

        s.abort_update()

        s.start_update()

        for i in range(3):
            print s.get_update_progress()
            time.sleep(1)

        s.abort_update()

        #r = s.create_query(u"快播")
        #print(s.get_search_result(r))
        #RUN = False
