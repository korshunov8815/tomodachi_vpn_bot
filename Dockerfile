FROM python:3

WORKDIR /usr/src/tomodachi_vpn_bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./tomodachi_vpn_bot.py", "nl" ]