import json, requests
from urllib.request import Request, urlopen


url = 'http://127.0.0.1:5000/classify'
prod_url = 'http://0.0.0.0:8080/classify'
#url = 'http://httpbin.org/post'

payload = {'client': 'a2b'}

mult_files = [
	('file',('civ_1.pdf', open('data/civ/civ_1.pdf', 'rb'), 'file/pdf')),
	('file',('d_pkd_1.docx', open('data/pkd/d_pkd_1.docx', 'rb'), 'file/doc')),
	('file',('hbl_2.pdf', open('data/hbl/hbl_2.pdf', 'rb'), 'file/pdf')),
	('file',('pkd_1.pdf', open('data/pkd/pkd_1.pdf', 'rb'), 'file/pdf')),
	('file',('pkd_3.jpg', open('data/pkd/pkd_3.jpg', 'rb'), 'file/image')),
	('file',('pkl_1.pdf', open('data/pkl/pkl_1.pdf', 'rb'), 'file/pdf')) ]

#print(type(mult_files))

doc_files = [('file',('d_pkd_1.docx', open('data/pkd/d_pkd_1.docx', 'rb'), 'file/doc'))]

excel_files = [('file',('x_pkl_1.xls', open('data/pkl/x_pkl_1.xls', 'rb'), 'file/excel')),
('file',('x_pkl_3.xlsx', open('data/pkl/x_pkl_3.xlsx', 'rb'), 'file/excel'))]

#req = Request('https://templatelab.com/wp-content/uploads/2017/02/bill-of-lading-01.jpg', headers={'User-Agent': 'Mozilla/5.0'})
#img = urlopen(req).read()

image_files = [('file',('pkl.jpeg', open('data/pkl/pkl.jpeg', 'rb'), 'file/image'))
]

pdf_files = [('file',('civ_1.pdf', open('data/civ/civ_1.pdf', 'rb'), 'file/pdf'))]

other_files = [('file',('SO2583108 AU Fumigation.pdf', open('data/other/SO2583108 AU Fumigation.pdf', 'rb'), 'file/pdf')),
('file',('TELEX RELEASE MARGONO.pdf', open('data/other/TELEX RELEASE MARGONO.pdf', 'rb'), 'file/pdf'))]

r = requests.post(url, data=payload, files=pdf_files)
print(r.text)


"""file1 = open("myfile.txt","w") 
file1.write(str(r.text))
body = open("body.txt","w") 
body.write(str(r.request.body))
header = open("header.txt","w") 
header.write(str(r.request.headers))"""


