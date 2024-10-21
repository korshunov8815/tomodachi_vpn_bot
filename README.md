# tomodachi_vpn_bot
Bot for telegram which can provide Outline keys: free and paid (payments work on RU payments provider Youkassa)

To start using:

1. Checkout repo
2. Create your own *_cfg.py file (check stub_cfg.py for example)
3. Create database.db sqlite3 database using create_db.sql
```
sqlite3 database.db < create_db.sql
```
4. Populate servers table of the created database with Outline server, e.g.
```
INSERT INTO servers (location, url)
VALUES
    ('NL', 'https://ip.here:4523/key.here'),
```
Make sure that server location in DB matches server location in *_cfg.py file

5. Edit Dockerfile so bot will run with an argument which matches the beginning of your configuration file. For example, if your configuration file is stub_cfg.py, you should use "stub" as an argument for running bot in Dockerfile

6. Build docker-image and run
```
docker build --tag 'tomodachi_bot' . --network=host
docker run --detach --network=host 'tomodachi_bot'
```
