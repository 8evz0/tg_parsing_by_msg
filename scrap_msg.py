from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import telethon.tl.types as tl_types
import csv

api_id = 21836109
api_hash = 'ce6540c6ea12bb5d8e58ed919bd6c075'
phone = '+79991145562'
client = TelegramClient(phone, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup == True:
            groups.append(chat)
    except:
        continue

print('Choose groups to scrape messages from (separated by commas):')
for i, g in enumerate(groups):
    print(str(i) + '- ' + g.title)

selected_indices = input("Enter Numbers (e.g., 0,2,3): ").split(',')
selected_groups = [groups[int(index.strip())] for index in selected_indices]


print('Fetching Messages and Users...')
messages_with_users = []
seen_message_ids = set()  # Set to keep track of seen message IDs
seen_user_ids = set()  # Set to keep track of seen user IDs

for target_group in selected_groups:
    messages = client.iter_messages(target_group, limit=10000)
    for message in messages:
        if message.id not in seen_message_ids:
            seen_message_ids.add(message.id)
            if message.sender:
                user = message.sender
                if isinstance(user, tl_types.User):
                    if user.id not in seen_user_ids:
                        seen_user_ids.add(user.id)
                        messages_with_users.append((user, message))

file_name = input("Enter the file name for saving (including extension, e.g., messages.csv): ")

print('Saving to file...')
with open(file_name, "a", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
    for user, _ in messages_with_users:
        if isinstance(user, tl_types.User):
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""
            name= (first_name + ' ' + last_name).strip()
            writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])  
print('Messages and users successfully collected and saved.')

