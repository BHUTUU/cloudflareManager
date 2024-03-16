from cloudflareManager import CloudflareManager
a=CloudflareManager
stat = a.startCloudflareServer("127.0.0.1", 8080)
print(stat)
# import re
# with open("not.txt", "r") as ab:
#     fc = ab.read()
#     ab.close()
# link = re.findall(r'https://[-0-9a-z]*\.trycloudflare.com', fc)
# print(link)