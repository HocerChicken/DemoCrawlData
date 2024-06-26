import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom

def post_request(url, payload):
    try:
        with requests.Session() as session:
            r = session.post(url, data=payload)
            r.raise_for_status()
            return r.content
    except requests.RequestException as e:
        print(f"An error occurred during the request: {e}")

def crawl_data(word, base_url='https://www.nomfoundation.org/nom-tools/Nom-Lookup-Tool/Nom-Lookup-Tool?uiLang=vn'):
    try:
        payload = {'inputText': word}
        data = post_request(base_url, payload)
        soup = BeautifulSoup(data, 'html.parser')
        
        rows = soup.find_all('tr')
        result = [[cell.text.strip() for cell in row.find_all(['td'])] for row in rows[3: -2]]
        return result
    except Exception as e:
        print(f"An error occurred during crawling: {e}")

def normalize(word, data, xml_root):
    if not data:
        return

    word_elem = Element("word")
    quocngu_elem = Element("quocngu")
    quocngu_elem.text = word

    word_elem.append(quocngu_elem)
    dinhnghia_elem = SubElement(word_elem, "dinhnghia")

    for line in data:
        if len(line) == 5:
            #[nom, ngucanh, nguon, phienam] here
            phanloai_elem = SubElement(dinhnghia_elem, "phanloai")

            nom_elem = SubElement(phanloai_elem, "hannom")
            nom_elem.text = line[1]  

            ngucanh_elem = SubElement(phanloai_elem, "ngucanh")
            ngucanh_elem.text = line[2]

            nguon_elem = SubElement(phanloai_elem, "nguon")
            nguon_elem.text = line[3]
            
            phienam_elem = SubElement(phanloai_elem, "phienam")
            phienam_elem.text = line[4]

    xml_root.append(word_elem)

def process_words(words, xml_root):
    for word in words:
        crawl_result = crawl_data(word)
        normalize(word, crawl_result, xml_root)

def prettify(elem):
    rough_string = ET.tostring(elem, encoding='utf-8').decode('utf-8')
    try:
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    except Exception as e:
        print(e)
        print(rough_string)

def main():
    xml_root = Element('dictionary')
    with open('text_u_v_x_filtered.txt', 'r', encoding='utf-8') as file:
        data_list = [line.strip() for line in file.readlines()]
    process_words(data_list, xml_root) 
    pretty_xml = prettify(xml_root)
    if pretty_xml is not None:
        with open('text_u_v_x.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(pretty_xml)
    else:
        print("Error")

if __name__ == "__main__":
    main()