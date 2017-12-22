hexo cl
hexo g
hexo d
python baidu_urls/generate_urls.py
cd baidu_urls
curl -H 'Content-Type:text/plain' --data-binary @urls.txt "http://data.zz.baidu.com/urls?site=www.jinzili.cc&token=3Iv54hsqE99X65n4"

