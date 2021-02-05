import json, requests

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

doc_files = [('file',('d_pkd_1.docx', open('data/pkd/d_pkd_1.docx', 'rb'), 'file/doc'))]

excel_files = [('file',('x_pkl_1.xls', open('data/pkl/x_pkl_1.xls', 'rb'), 'file/excel')),
('file',('x_pkl_3.xlsx', open('data/pkl/x_pkl_3.xlsx', 'rb'), 'file/excel'))]

image_files = [('file',('pkl.jpeg', open('data/pkl/pkl.jpeg', 'rb'), 'file/image')),
('file',('pkl.png', open('data/pkl/pkl.png', 'rb'), 'file/image'))
]

color_files = [('file',('pkd_2.jpg', open('data/pkd/pkd_2.jpg', 'rb'), 'file/image'))
]

r = requests.post(prod_url, data=payload, files=mult_files)
print(r)
print(r.text)