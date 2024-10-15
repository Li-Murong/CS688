import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import re

all_descriptions = []
all_locations = []
all_prices = []
all_years = []

# 读取文件中的 HTML 内容
for page in range(4):
    try:
        url = f"https://boston.craigslist.org/search/cta?postal=02134&query=Toyota%20Camry&search_distance=100#search=1~list~{page}~0"
        response = requests.get(url)

        if response.status_code == 200:
            html_content = response.text
            print('Page received')
        else:
            print(f"Failed to retrieve page: {response.status_code}")

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找包含 JSON-LD 数据的 <script> 标签
        scripts = soup.find_all('script', type='application/ld+json')

        # 解析并提取 JSON-LD 数据
        for script in scripts:
            try:
                json_data = json.loads(script.string)
                # 检查数据是否包含 "itemListElement"
                if 'itemListElement' in json_data:
                    items = json_data['itemListElement']
                    for item in items:
                        product_info = item.get('item', {})
                        # print(f"Name: {product_info.get('name')}")
                        description = product_info.get('name')
                        all_descriptions.append(description)
                        if 'offers' in product_info:
                            # print(f"Price: {product_info['offers'].get('price')}")
                            all_prices.append(float(product_info['offers'].get('price')))
                        if 'availableAtOrFrom' in product_info.get('offers', {}):
                            location = product_info['offers']['availableAtOrFrom'].get('address', {})
                            # print(f"Location: {location.get('addressLocality')}")
                            all_locations.append(location.get('addressLocality'))
                        year_match = re.search(r'\b(19|20)\d{2}\b', description)
                        year = int(year_match.group(0)) if year_match else 'null'
                        all_years.append(year)
                        print('-' * 30)
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error on page {page + 1}: {e}")

data = {
    'Description': all_descriptions,
    'Location': all_locations,
    'Price': all_prices,
    'Year': all_years
}

df = pd.DataFrame(data)

# 输出总条数
print(f"Total number of listings: {len(df)}")

# 输出 DataFrame 的前几行
print(df.head())
