import requests
import json
import csv
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

nhacuadoisong_page_url = "https://tiki.vn/api/v2/products?limit=12&include=advertisement&is_mweb=1&aggregations=1&trackity_id=57cfc372-e11d-193c-0342-37ff3ebdadb6&src=c.1883.hamburger_menu_fly_out_banner&urlKey=nha-cua-doi-song&categoryId=1883&category=1883&page=1"

product_url = "https://tiki.vn/api/v2/products/{}"
rating_url = "https://tiki.vn/api/v2/reviews?product_id=76149032&include=comments&page=1&limit=-1&top=true&spid=76149033&seller_id=153539"

product_id_file = "./data/product-id.txt"
product_file = "./data/product.txt"
product_file2 = "./data/product-detail.txt"
rating_file = "./data/rating.csv"

def crawl_product_id():
    product_list = np.array([])
    i = 1
    while(i<22):
        payload = {}
        headers = {
            'user - agent': "Mozilla / 5.0(Linux; Android 6.0; Nexus 5 Build / MRA58N) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 88.0.4324.202 Mobile Safari / 537.36"
        }
        params = {
            'page' : i
        }
        response = requests.request(
            "GET",nhacuadoisong_page_url, headers=headers, data=payload,params=params
        )
        print(response)
        print("page", i)
        y =response.json()
        print(len(y["data"]))
        for j in range(len(y["data"])):
            idproduct = y["data"][j]['id']
            product_list = np.append(product_list,idproduct,axis=0)
        i+=1
        product_list=product_list.astype(int)
        print("product_list",product_list)
        print("len_product_list", len(product_list))
    return product_list
def write_csv_file(data_matrix,file_path,mode='a'):
    df = pd.DataFrame(data=data_matrix)
    df.to_csv(file_path,sep='\t',header=None, index=None, mode=mode)

def read_matrix_file(file_path):
    f= pd.read_csv(
        file_path,sep='\t', encoding='utf-8', header=None)
    f=f.to_numpy()
    return f

def crawl_product(product_list):
    product_detail_list=np.array(
        [['id','ten','gia','phanloai','thuonghieu','xuatxu','xuatxuthuonghieu','sku','mota']])
    print('product_detail_list',product_detail_list)
    for product_id in product_list:
        id =-1
        ten=-1
        gia=-1
        phanloai=-1
        thuonghieu=-1
        xuatxu=-1
        xuatxuthuonghieu=-1
        sku=-1
        mota=-1
        print("product_id",product_id)
        payload = {}
        headers = {
            'user - agent': "Mozilla / 5.0(Linux; Android 6.0; Nexus 5 Build / MRA58N) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 88.0.4324.202 Mobile Safari / 537.36"
        }
        response = requests.get(product_url.format(
            product_id
        ), headers=headers,data=payload)
        y=response.json()
        if(response.status_code==200):
            id=y['id']
            ten=y['name']
            gia=y['price']
            phanloai=y['productset_group_name']
            thuonghieu=y['brand']['name']
            for i in range(len(y['specification'][0]['attributes'][0]['attributes'])):
                if(y['specification'][0]['attributes'][i]['name']=="Xuất Xứ"):
                    xuatxu=y['specification'][0]['attributes'][i]['value']
                if (y['specification'][0]['attributes'][i]['name']=="Xuất Xứ thương hiệu"):
                    xuatxuthuonghieu=y['specification'][0]['attributes'][i]['value']
            sku=y['sku']
            mota= BeautifulSoup(y['description'],'html.parser').get_text()
        product_detail_list=np.append(
            product_detail_list,[[id,ten,gia,phanloai,thuonghieu,xuatxu,xuatxu,sku,mota]]
        )
    return product_detail_list
def crawl_rating(product_list):
    for product_id in product_list:
        userid=-1
        itemid=-1
        rateing=-1
        timetamp=-1
        comment=-1
        i=1
        print("product_id",product_id)
        payload={}
        params={"page": i}
        headers={
            'user - agent': "Mozilla / 5.0(Linux; Android 6.0; Nexus 5 Build / MRA58N) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 88.0.4324.202 Mobile Safari / 537.36"
        }
        response=requests.get(rating_url.format(
            product_id
        ),headers=headers,data=payload,params=params)
        print("response",response)
        y=response.json()
        total_page = y['paging']['last_page']
        if (y['paging']['total']>0):
            while(i<=total_page):
                payload={}
                params={'page':i}
                headers={
                    'user - agent': "Mozilla / 5.0(Linux; Android 6.0; Nexus 5 Build / MRA58N) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 88.0.4324.202 Mobile Safari / 537.36"
                }
                res=requests.get(rating_url.format(
                    product_id
                ),headers=headers,data=payload,params=params)
                x=res.json()
                for j in range (len(x["data"])):
                    userid=x["data"][j]['customer_id']
                    itemid-product_id
                    rateing=x["data"][j]['rating']
                    timetamp=x["data"][j]['created_at']
                    comment=x["data"][j]['content']
                    rating_list=np.array(
                        [[userid,itemid,rateing,timetamp,comment]]
                    )
                    write_csv_file(rating_list,rating_file,mode='a')
                i+=1
    return 1
# crawl id tat ca sp
product_list = crawl_product_id()
# ghi file cac id sp vao file product-id.txt
write_csv_file(product_list,product_id_file,mode='w')
# doc danh sach id sp de tien hanh crawl chi yiet sp va ratings
product_list=read_matrix_file(product_id_file).flatten()
#crawl chi tiet sp va ghi vao file product.csv
product_detail_list=crawl_product(product_list)
write_csv_file(product_detail_list,product_file2,mode='w')
#crawl tat ca rating trong product_list ghi vao file rating.csv
rating_list=crawl_rating(product_list)
