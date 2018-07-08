#!/usr/bin/env python
# --*-- coding:utf-8 --*--
# author:zili.jin

import lxml.etree
import os

def get_url():
    xml_path_par = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    xml_path = os.path.join(xml_path_par, 'public', 'baidusitemap.xml')
    print xml_path
    with open(xml_path, 'r') as file:
        xml_string = file.read()
        print xml_string
        doc = lxml.etree.fromstring(xml_string)
        ns = doc.nsmap
        default_ns = ns[None]
        print default_ns
        path = '{0}url/{0}loc'.format('{' + default_ns + '}')
        # print '{%s}url/{%s}loc' % (default_ns, default_ns)
        urls = []
        for node in doc.findall(path):
            url = node.text.replace('https://jinzili.github.io', 'http://www.jinzili.cc')
            print url
            urls.append(url)
        print urls
        with open('./urls.txt', 'w') as url_txts:
            for url in urls:
                url_txts.writelines(url + '\n')

if __name__ == '__main__':
    get_url()

