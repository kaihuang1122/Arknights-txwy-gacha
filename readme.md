# Arknights txwy server gacha record scraping / 明日方舟繁中服尋訪紀錄抓取

## Warning / 警告

* This project is not affiliated with, endorsed by, or authorized by the game developers or publishers (such as Hypergryph, Longcheng, Yostar, or Studio Montagne). This project involves web scraping, and **anyone using this project does so at their own risk**. The author makes **no guarantees** that using this project does not violate any terms of service or laws in your jurisdiction. The author also **does not guarantee** that the use of this project will not lead to personal data leaks. The author **assumes no responsibility** for any damage or loss resulting from the use of this project, and **offers no implied warranties** of any kind. This project is provided **for academic research and personal use only**; **commercial use or redistribution is strictly prohibited**.

* 本專案與遊戲開發商或發行商（如鷹角網路、龍成網路、悠星網路或蒙塔山工作室）無任何關聯，也未經其授權。本專案屬於爬蟲，任何使用本專案的人士，須自行承擔一切風險，專案作者不保證使用本專案不會違反任何使用條款或任何地區的法律法規，專案作者不保證使用本專案不會造成任何個人資料的洩漏，專案作者不會負責任何因使用本專案而引致之損失，專案作者不會作出任何默示的擔保。本專案僅供學術研究與個人用途，禁止用於任何商業用途或轉售。

* Due to the instability of the record merging mechanism, please **manually back up** your `visit_records.json` to prevent older records from being overwritten.


* 由於新舊紀錄合併機制的不穩定性，請**自行備份** `visit_records.json` 以防舊紀錄被覆蓋。

## Feature / 功能

* Based on the structure of the webpage at `https://ak.gryphline.com/user/visit`, this project automates the following steps:

  * Automatically fills in the account and password to log in.
  * Continuously turns pages and collects recruitment records until the last page.
  * Merges the newly fetched records with previously saved data.
  * Saves all records into `visit_records.json`.

* 基於 `https://ak.gryphline.com/user/visit` 的網頁設計，本專案會依序自動化完成：
    * 帳號密碼輸入並登入。
    * 重複換頁並抓取尋訪紀錄直到最後一頁。
    * 與先前的抓取結果進行合併。
    * 將尋訪紀錄寫入 `visit_records.json`。

* Since some banners are not shown in the official “Recruitment” tab, this project merges old and new records **based only on the operator's name and the recruitment date**, under the following assumptions:

  * It is assumed that each scraping session completes successfully and fully.
  * It is assumed that any 10-pull recruitment record will not be split by boundary data.

* 由於「尋訪卡池」欄目無法顯示部分卡池，合併新舊紀錄時僅會依照 `幹員名稱` 與 `尋訪日期` 並基於以下假設進行合併：
    * 假設每次抓取都有完整完成。
    * 假設任意十連尋訪的紀錄不會被有效數據的邊界分割。

## Prerequisites / 前置需求：
Ensure you have Google Chrome 133.0 or higher installed. / 請確保您的電腦已安裝 Google Chrome 133.0 或以上版本。
Ensure you have Python 3.11 or higher installed. / 請確保您的電腦已安裝 Python 3.11 或以上版本。

## Getting Started / 使用方法

1. **Clone the Repository**: / **複製項目**：  
    Open a terminal and run: / 打開終端機後執行：  
    ```bash
    git clone https://github.com/kaihuang1122/arknights-txwy-gacha
    ```
2. **Navigate to the Project Directory**: / **進入專案目錄**：  
    ```bash
    cd arknights-txwy-gacha
    ```
3. **Create a Virtual Environment (Recommended)**: / **創建虛擬環境（推薦）**：
    ```bash
    python -m venv venv
    .\venv\Scripts\activate (windows)
    source tutorial-env/bin/activate (Unix or MacOS)
    ```
4. **Install Dependencies**: / **安裝套件**：  
    ```bash
    pip install -r requirements.txt
    ```
5. **Adjust Configuration**: / **調整設置**：

    Open`main.py` and adjust the following section: / **打開`main.py`，並調整以下欄位**：
    ```python
    # ========= Please enter the following configuration=========
    EMAIL = "your_email@example.com"
    PASSWORD = "your_password_here"
    ACCOUNT_ENTERING_TIME = 10
    PAGE_CHANGE_TIME = 1
    # ===========================================================
    ```
    If you keep the example email, the program will wait for `ACCOUNT_ENTERING_TIME` seconds for you to enter manually. / 若將EMAIL維持示例狀態，程式將等待`ACCOUNT_ENTERING_TIME`秒讓你手動輸入。
    During scraping, the script waits PAGE_CHANGE_TIME seconds for each page to load. Adjust this value based on your network speed. / 抓取時，會在換頁後等待載入 `PAGE_CHANGE_TIME` 秒，你可以依照網路狀況進行調整。


6. **Run the code**: / **執行程式**：  
    ```bash
    python main.py
    ```

## Future works

- 做一個漂亮的紀錄分析介面