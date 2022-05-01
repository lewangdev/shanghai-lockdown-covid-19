from python:3.10.4-bullseye

WORKDIR /root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
