# -*- coding: utf-8 -*-

import gzip
import os
import re

from bs4 import BeautifulSoup

remove_css = re.compile(r'\..*{.*}', re.S)

def remove_html_js(text):
    text_l = list(text)
    pos_end = text.find("</script>")
    pos_start = text.rfind("<script", 0, pos_end)

    limit = 0

    while pos_end != -1 and pos_start != 1 and limit < 50:
        for i in range(pos_start, pos_end + 9):
            text_l[i] = ' '
        text = ''.join(text_l)
        text_l = list(text)

        pos_end = text.find("</script>")
        pos_start = text.rfind("<script", 0, pos_end)

        limit += 1
    try:
        text = BeautifulSoup(text, 'html.parser').get_text(strip=True)
    except:
        pass
    text = remove_css.sub('', text)
    return text



class content_reader:
    def __init__(self):
        pass

    def read(self, path):
        ret_dict = {'content': ''}
        try:
            with open(os.path.join(path, 'meta'), 'rb') as f:
                ret_dict.update(eval(f.read().decode('utf-8')))
            try:
                with gzip.open(os.path.join(path, 'response_body'), 'rb') as f:
                    text = f.read()
                    try:
                        text = text.decode('gb2312')
                    except:
                        try:
                            text = text.decode('utf-8')
                        except:
                            text = text.decode('ISO-8859-1')
            except IOError:
                with open(os.path.join(path, 'response_body'), 'rb') as f:
                    text = f.read()
                    text = text.decode('ISO-8859-1')

            ret_dict['content'] = text
            
        except Exception, e:
            print("Unexpect error occured while load folder %s\n" % path, e)
            return None
        
        return ret_dict


if __name__ == "__main__":
    reader = content_reader()
    a = reader.read("./00a0ba6aa8c60c99c5f2ea68ec75f28eb9f61aa9")


    print(remove_html_js(a['content']))