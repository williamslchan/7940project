FROM python
WORKDIR /app
COPY chatbot.py chatbot.py
COPY requirements.txt requirements.txt
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN =1671967756:AAHcCpbe8H3KFd_4cM3EVdwXABjkNgxnoy0
ENV HOST = "redis-15314.c54.ap-northeast-1-2.ec2.cloud.redislabs.com"
ENV PASSWORD = "0nT2xVWCapbse70FIuXV74ewdLStAJwB"
ENV REDISPORT = "15314"
CMD python chatbot.py
