import httplib

r_headers = {
"Cookie" : "__jsluid=3ff4ce8e5e2c3ffb10149fe95cc79c7c; __jsl_clearance=1517653132.071|0|bQercjeTuc8KTTfdmL3yYTwvkU4%3D",
"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
}

r_header={}

def get_cookie_str(s):

	s = s.replace('https://', '')
	s = s.replace('http://', '')
	s_l = s.split('/')
	
	s = s_l[0]
	p = '/' + '/'.join(s_l[1:])
	
	print(s, p)

	cookie_str = ''

	conn = httplib.HTTPConnection(s)
	conn.request('GET', p, headers=r_headers)
	response = conn.getresponse()
	print response.status
	headers = response.getheaders()
	conn.close()

	
	for item in headers:
		if item[0] == 'set-cookie':
			cookies = item[1].split(", ")
			for item in cookies:
				if not '=' in item[:20]:
					continue
				cookie_str += item[:item.find(';')] + '; '
			break
		
	cookie_str = cookie_str[:-2]
	
	return cookie_str
	

if __name__ == '__main__':
	print get_cookie_str('http://www.court.gov.cn')
