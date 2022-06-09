# Python-Socket-Chat-Room

![](/src/source/demo.gif)

## How to use
1. write config.txt
    ```
    server_ip=xxx.xxx.xxx.xxx 
    server_port=xxxx
    message_len_bytes=3
    ```


2. server
    ```
    python ./src/server.py
    ```
    client
    ```
    python ./src/client.py
    ```

## 補充
### config
- message_len_bytes

    - tcp 只保證訊息抵達時的順序，有可能會把資訊拆開發送或一起發送
        ```python
            client.send("Connected to server!".encode("utf-8"))
            broadcast(f"{nickname} joined")
        ```
        比如原本未處理的時候，這兩句話有可能一起發送
        所以 utils/message.py 有對這做處理<br/>
        message_len_bytes 可以設定每次訊息要用幾個 bytes 來儲存接下來的訊息長度<br/>
        如果訊息的長度超過 bytes 可表示的數量，就拆開多次發送
