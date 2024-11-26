from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from bs4 import BeautifulSoup
import pandas as pd

# 初始化存储所有页面数据的列表
all_descriptions = []
all_locations = []
all_prices = []
all_years = []

# 需要抓取的总页数
total_pages = 4

# 启动 Safari 浏览器
driver = webdriver.Safari()

# 循环抓取每页的数据
for page in range(total_pages):
    try:
        # 修改 URL 中的页码部分
        url = f'https://boston.craigslist.org/search/cta?postal=02134&query=Toyota%20Camry&search_distance=100#search=1~list~{page}~0'
        driver.get(url)

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cl-search-result")))

        # 获取页面的 HTML 内容
        html_content = driver.page_source

        # 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找包含搜索结果的 <li> 标签
        list_items = soup.find_all('li', class_="cl-search-result cl-search-view-mode-list")

        # 遍历每个 <li> 标签，提取数据
        for li in list_items:
            # 提取汽车描述
            description = li.find('span', class_='label').text if li.find('span', class_='label') else 'null'
            all_descriptions.append(description)

            # 提取地址
            address = li.find('div', class_='supertitle').text if li.find('div', class_='supertitle') else 'null'
            all_locations.append(address)

            # 提取并处理价格
            raw_price = li.find('span', class_='priceinfo').text if li.find('span', class_='priceinfo') else 'null'

            # 使用正则表达式提取第一个以 $ 开头的数字（包括千位逗号）
            price_match = re.search(r'\$\d{1,3}(,\d{3})*', raw_price)

            # 如果匹配到价格，移除 $ 和 ,，否则返回 'null'
            if price_match:
                price = price_match.group(0).replace('$', '').replace(',', '')
            else:
                price = 'null'
            all_prices.append(price)

            # 提取年份（从描述中通过正则表达式匹配年份）
            year_match = re.search(r'\b(19|20)\d{2}\b', description)
            year = year_match.group(0) if year_match else 'null'
            all_years.append(year)

        print(f"Page {page + 1} scraped successfully.")
    except Exception as e:
        print(f"Error on page {page + 1}: {e}")

# 关闭浏览器
driver.quit()

# 将所有数据存入 pandas DataFrame
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

# 保存到 CSV 文件
# df.to_csv('craigslist_data_all_pages.csv', index=False)