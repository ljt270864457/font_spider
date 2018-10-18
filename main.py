# coding=utf-8

import re

import requests
from PIL import ImageDraw, ImageFont, Image
from fontTools.ttLib import TTFont
import pytesseract
import base64
from scrapy.selector import Selector


def get_html():
    url = 'https://bj.58.com/hezu/35762485615942x.shtml?from=1-list-2&iuType=z_0&PGTID=0d3090a7-0000-1d18-cd0c-225cc1843040&ClickID=2&adtype=3'
    r = requests.get(url)
    html = r.content
    with open('test.html','w') as f:
        f.write(html)
    return html

def get_origin_price(html):
    '''
    获取html中的租金信息
    '''
    sel = Selector(text=html)
    price = sel.xpath('//span[@class="c_ff552e"]/b/text()').extract_first()
    return price

class Font(object):
    def __init__(self,html):
        self.html = html
        self.regex = re.compile(r'base64,(.*)\'\) format')
    
    def save_ttf(self,ttf_path='test.ttf'):
        '''
        存储字库
        '''
        font_content = base64.b64decode(self.regex.search(html).group(1))
        with open(ttf_path,'wb') as f:
            f.write(font_content)
        return font_content

    def save_ttf_xml(self, ttf_path='test.ttf', xml_path='test.xml'):
        '''
        存储字体库的xml
        '''
        font = TTFont(ttf_path)
        font.saveXML(xml_path)

    def get_all_char(self, ttf_path='test.ttf'):
        '''
        获取字库中的所有字符
        '''
        font = TTFont(ttf_path)
        uni_char_list = []
        for table in font['cmap'].tables:
            for char_code, glyph_name in table.cmap.items():
                uni_char_list.append(unichr(char_code))
        uni_char_list = list(set(uni_char_list))
        return ''.join(uni_char_list)

    def get_mapping(self, content, ttf_path='test.ttf'):
        '''
        获取字库映射
        '''
        font = ImageFont.truetype(ttf_path, size=21, encoding="unic")
        width = 150
        height = 20
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), content, font=font, fill="#000000")
        image.save('test.jpg', dpi=(300.0, 300.0))
        mapping_value = pytesseract.image_to_string(image, config='-psm 3')
        result = dict(zip(content, mapping_value))
        return result

if __name__ == '__main__':
    html = get_html()
    price = get_origin_price(html)
    print u'原始租金：{}'.format(price)
    font_instance = Font(html)
    font_instance.save_ttf()
    font_instance.save_ttf_xml()
    process_string = font_instance.get_all_char()
    print u'奇葩字符是：{}'.format(process_string)
    mapping_value = font_instance.get_mapping(process_string)
    print mapping_value
    for each_str in price:
        price = re.sub(each_str, mapping_value[each_str], price)
    print u'处理后租金:{}'.format(price)

