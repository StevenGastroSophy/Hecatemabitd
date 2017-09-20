Hecatemabitd
一個線上遊戲道具購物網站，包含購物車、結帳及訂單查詢功能。
         https://hecatemabitd.herokuapp.com 
         https://github.com/kaspersky518/Hecatemabitd 
1.使用Flask+SQLAlchemy+PostgreSQL來做後端、htnl+CSS+Jquery做前端。 先將檔案上傳到Github再部署到HEROKU。 
2.在商品介紹頁面使用Ajax來替換圖片及文字。 
3.用Session來保存使用者的購物車狀態，以Flask-Session來取代原生的Session模組。 
4.使用Flask-SocketIO，透過特定連結以Websocket來即時修改右下角的「在線狀態」。 
    觸發連結  -> 修改資料庫table內容   -> Server每10秒讀取table   -> 改變在線狀態
    https://hecatemabitd.herokuapp.com/status/online/ + 「分流編號(1~99)」可以將狀態設為"ONLINE"並加上分流編號。 
    例如: https://hecatemabitd.herokuapp.com/status/online/7 
    https://hecatemabitd.herokuapp.com/status/offline 可以將狀態設為"OFFLINE"。
5.使用者在結帳後會得到一組由timestamp+隨機碼+毫秒組成的訂單代碼，用於訂單查詢。
