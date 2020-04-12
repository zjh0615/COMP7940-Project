import requests
from bs4 import BeautifulSoup
import redis


HOST = "redis-16933.c15.us-east-1-4.ec2.cloud.redislabs.com"
PWD = "yBFMT0bNR2mpF3HjviE45Ig9xGIPxKtI"
PORT = "16933"
redis1 = redis.Redis(host=HOST, password=PWD, port=PORT)

redis1.delete("mask1")
redis1.delete("mask2")
redis1.delete("mask3")
redis1.delete("port1")
redis1.delete("policy1")

#mask: three regions
hongkong={1:"https://www.ukzooly.com.cn/Uploads/201808/5b62758d033b2.jpg Watsons Shop_No.927-928,9th_Floor,Times_Square,Matheson_St,Causeway_Bay 11:00-20:00 400 180 (852)26088383 https://watsons.com.hk @22.2781233,114.1809866",
                  2:"https://www.ukzooly.com.cn/Uploads/201808/5b62758d033b2.jpg Watsons Fortune_Center,Shop_3-10_of_G/F,Whole_1/F&2/F,44-48_Yun_Ping_Rd,Causeway_Bay 10:30-20:00 200 230 (852)26088383 https://watsons.com.hk @22.2793539,114.1822525",
                  3:"https://www.ukzooly.com.cn/Uploads/201808/5b62758d033b2.jpg Watsons Shun_Talk_Center,291-293_Connaught_Road_Central,Sheung_Wan,HongKong 9:30-19:30 300 170 (852)26088383 https://watsons.com.hk @22.2859361,114.1481228",
                  4:"https://www.ukzooly.com.cn/Uploads/201808/5b62758d033b2.jpg Watsons Comm.Ctr_Apleichau,HK,Shop112,112A&113_Rear_Portion,1/F,South_Horizon_Marina_Square_West 10:30-19:30 100 190 (852)26088383 https://watsons.com.hk @22.2437987,114.1446274",
                  5:"https://www.ukzooly.com.cn/Uploads/201808/5b62758d033b2.jpg Watsons K-Gold_Jewellery_Infinity_Ltd 10:00-20:00 600 140 (852)26088383 https://watsons.com.hk @22.2784689,114.163072"
                  }
redis1.hmset('mask1', hongkong)

kowloon = {1:"https://www.hksasa.cn/img/logo_wap_3x.png Sasa Ground_Floor_and_1st_Floor,Chengxin_Building,73_Beijing_Road,Tsim_Sha_Tsui,Kowloon 10:00-23:00 500 200 (852)23676322 http://corp.sasa.com @22.2995513,114.1698018 ",
                 2:"https://www.hksasa.cn/img/logo_wap_3x.png SaSa Shop_E,G/F,Man_Wah,240-244_Portland_Street,Mong_Kok,Kowloon 10.30-19.30 300 200 (852)22170138 http://corp.sasa.com @22.2778842,114.1809742",
                 3:"https://www.hksasa.cn/img/logo_wap_3x.png SaSa Shop_345-346,Level3,Hollywood_Plaza,Diamond_Hill,Kowloon 11:00-20:00 150 150 (852)23272997 http://corp.sasa.com @22.3216634,114.1026553",
                 4:"https://www.hksasa.cn/img/logo_wap_3x.png SaSa Shop_G19&G20,G/F,Treasure_Place,Whampoa_Garden,Hung_Hom,Kowloon 11:00-20:00 180 180 (852)23681681 http://corp.sasa.com @22.3044953,114.1896229",
                 5:"https://www.hksasa.cn/img/logo_wap_3x.png SaSa Shop_148,Level_1,New_Century_Plaza,Mongkok,Kowloon 11:00-20:00 500 220 (852)24098282 http://corp.sasa.com @22.3045365,114.173162"
                 }
redis1.hmset('mask2',kowloon)

newterritories= {1:"https://www.mp4cn.com/logoimg/5/20170109060436_97670.jpg Mannings Shau_Keia_Wan_Rd,326-332,Hong_Tai_Building,Shop_4,G/F 10:00-22:00 500 200 (852)24166244 https://mannings.com.hk @22.2811575,114.1570975",
                 2:"https://www.mp4cn.com/logoimg/5/20170109060436_97670.jpg Mannings Kwai_Shing_West_Estate_Shopping_CentreShops_20-21 9:00-21.30 300 200 (852)22993381 https://mannings.com.hk @22.3623058,114.1214421",
                 3:"https://www.mp4cn.com/logoimg/5/20170109060436_97670.jpg Mannings LiberteShop_Nos.130&132,1/F 10:00-22:00 150 150 (852)22993381 https://mannings.com.hk @22.3347276,114.1467204",
                 4:"https://www.mp4cn.com/logoimg/5/20170109060436_97670.jpg Mannings Nina_Tower_Shop_No.135,Level_1 10:00-22:00 180 180 (852)22993381 https://mannings.com.hk @22.3686159,114.1107976",
                 5:"https://www.mp4cn.com/logoimg/5/20170109060436_97670.jpg Mannings Shek_Lei_Shoppong_Centre_Pharse_2Shop_235,2/F 9:00-22:00 500 220 (852)22993381 https://mannings.com.hk @22.3649749,114.136142"
                 }
redis1.hmset('mask3', newterritories)

# shop = []
# s=redis1.hvals("mask1")
# print(s)
# for i in range(redis1.hlen("mask1")):
#     x = redis1.hget("mask1", i+1)
#     if x:
#         x=x.strip().split()
#         print(x[0],x[5],x[6],x[7])
#     else:
#         break

#confirmation information
def n_conf():
    case_source = 'https://en.wikipedia.org/wiki/2019%E2%80%9320_coronavirus_pandemic_by_country_and_territory'
    html = requests.get(case_source)
    bs = BeautifulSoup(html.text, 'lxml')

    case_list = []
    world = ''
    tables = bs.find('table', {'class': 'wikitable'})
    table = tables.find('tbody')
    cases_detail = table.find_all('tr')
    cases_detail = cases_detail[2:-2]
    top10 = 0
    for case in cases_detail:
        country = case.find('a')
        country = country.text
        #    print(country)

        nums = case.find_all('td')
        nums = nums[:3]
        numls = []
        for i in nums:
            num = i.text
            num = num[:-1]
            numls.append(num)
        cases = numls[0]
        deaths = numls[1]
        recove = numls[2]
        detail = f'Cases: {cases}\nDeaths: {deaths}\nRecov.: {recove}'
        redis1.set(country,detail)
        top10 += 1
        if top10 <= 10 :
            world += f'{country}:\n**Cases: {cases}\n**Deaths: {deaths}\n**Recov.: {recove}\n\n'
    return world
# redis1.set('world', n_conf())
# print(redis1.get('world'))


#port information
def port():
    port_source = 'https://www.coronavirus.gov.hk/eng/control-points.html'
    html = requests.get(port_source)
    bs = BeautifulSoup(html.text, 'lxml')

    port_ = ''
    port_table = bs.find('tbody')
    port_detail = port_table.find_all('tr')
    # port_={}
    x=1
    for port in port_detail:
        info = []
        port_info = port.find_all('td')
        for i in port_info:
            t = i.text
            t = t.replace('\n', '')
            t = t.replace('\t', '')
            t = t.replace('\r', ';')
            info.append(t)
        if len(info) < 2:
            info.append('Passenger clearance services suspended')
        #    print(info)
        port_ += f'{info[0]}:  {info[1]}\n\n'
        # port_[x]=f"{info[0]}: {info[1]}"
        x+=1
    return port_
redis1.set(1,port())
# ports=redis1.get(1)
# print(ports.decode())

#hotcall
hotcall={"p1":'''Centre for Health Protection Hotline: 2125 1111 / 2125 1122 (8 am to 12 midnight)\n\nHome Affairs Department Hotline: 2835 1473 (24 hours)'''}
redis1.hmset('policy1',hotcall )

#inbound
redis1.set("inbound1","https://www.coronavirus.gov.hk/eng/inbound-travel.html")
# x=redis1.hget("inbound1","i1")
# print(x.decode())
# s=redis1.hget("policy1","p1")
# print(s.decode())
# print(s[0].decode(),"\n",s[1].decode())
