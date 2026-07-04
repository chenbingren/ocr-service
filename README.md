# ocr-service

独立 OCR 服务，对外提供 `/ocr` 图片识别接口。

## Local run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Docker

```bash
# build image and start container
bash build.sh

# build image only
RUN_CONTAINER=false bash build.sh

# restart container with an existing image
BUILD_IMAGE=false bash build.sh

# optional: join a Docker network only when container-name DNS is required
DOCKER_NETWORK=mehup-ai bash build.sh
```

服务内访问地址：

```text
http://<server-ip>:8003/ocr
```

curl.exe -G "http://127.0.0.1:8003/test/ocr" ` --data-urlencode "filePath=D:\test.jpg"

curl -G "http://127.0.0.1:8003/test/ocr" --data-urlencode "filePath=/data/app/file_data/test.jpg"

docker rm -f ocr-service || true

docker run -d \
  --name ocr-service \
  --restart unless-stopped \
  -p 8003:8003 \
  -v /data/app/file_data:/data/app/file_data:ro \
  mehup/ocr-service:latest