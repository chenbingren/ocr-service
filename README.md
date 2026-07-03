# ocr-service

独立 OCR 服务，对外提供 `/ocr` 图片识别接口。

## Local run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Docker

```bash
bash build.sh
bash run.sh
```

服务内访问地址：

```text
http://ocr-service:8003/ocr
```

curl.exe -G "http://127.0.0.1:8003/test/ocr" `
  --data-urlencode "filePath=D:\test.jpg"