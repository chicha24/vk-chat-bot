import os
import vk_api, json, operator
from functools import reduce
from vk_api.exceptions import ApiError
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType


def appendArrToMsg(arr, msg) -> str:
    for el in arr:
        msg += el + '\n'
    return msg


def getFromDict(dataDict, mapList) -> reduce:
    return reduce(operator.getitem, mapList, dataDict)


def cleanUserIdFromMsgMention(msg) -> int:
    msg = event.message.text
    return int(''.join(i for i in msg if i.isdigit()))


def appendChatJSON(newData):
    with open('chatLists.json', 'r+') as cl:
        dataLoaded = json.load(cl)
        dataLoaded['chats'].update(newData)
        cl.seek(0)
        json.dump(dataLoaded, cl, indent=4)


def appendToFaggotsJSON(newData, chatID):
    with open('chatLists.json', 'r+') as cl:
        dataLoaded = json.load(cl)
        dataLoaded['chats']['chat{}'.format(chatID)]['faggots'].update(newData)
        cl.seek(0)
        json.dump(dataLoaded, cl, indent=4)


def deleteFromFaggotsJSON(userId):
    with open('chatLists.json', 'r+') as cl:
        dataLoaded = json.load(cl)
        del dataLoaded['chats']['chat{}'.format(event.chat_id)]['faggots']['user{}'.format(userId)]
        cl.seek(0)
        json.dump(dataLoaded, cl, indent=4)


def getUserName(userId, session) -> str:
    user = session.users.get(user_ids=userId)
    firstName = user[0]['first_name']
    lastName = user[0]['last_name']
    fullName = firstName + ' ' + lastName
    return fullName


def sendMessage(text, chatId):
    vk.messages.send(
        key='99b9dafd8feed221ef34121e72ef201f7ed73453',
        server='https://lp.vk.com/wh207881931',
        ts='3',
        random_id=get_random_id(),
        message=text,
        chat_id=chatId
    )


token = '8c1281b16533d4b0e8ec8387ddf29cb8c4ed022d0bf80f47fec71ccaca1f1fdc23f2960279aa92ea4fb03'
group_id = '207881931'

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id)

if not os.path.exists('chatLists.json'):
    startDict = {
        'chats': {

        }
    }

for event in longpoll.listen():
    users = vk.messages.getConversationMembers(peer_id=event.message.peer_id, group_id=group_id)
    conversation = vk.messages.getConversationsById(peer_ids=event.message.peer_id, group_id=group_id)
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            try:
                actionType = event.message.action['type']
                actionUserId = event.message.action['member_id']
            except:
                actionType = ''
                actionUserId = -100
            if "чича кик" in event.message.text.lower():
                for u in users['items']:
                    if u['member_id'] == event.message.from_id:
                        admin = u.get('is_admin', False)
                        if admin:
                            try:
                                vk.messages.removeChatUser(chat_id=event.chat_id,
                                                           user_id=cleanUserIdFromMsgMention(event.message.text))
                            except ApiError:
                                sendMessage('Указаный пользователь отсутствует', event.chat_id)
                        else:
                            sendMessage('Недостаточно прав', event.chat_id)
            if actionType == 'chat_kick_user':
                vk.messages.removeChatUser(chat_id=event.chat_id, user_id=actionUserId)

            if "чича стартуй" in event.message.text.lower():
                for u in users['items']:
                    if u['member_id'] == event.message.from_id:
                        admin = u.get('is_admin', False)
                        if admin:
                            sendMessage('Успешно начал работу!', event.chat_id)
                            data = {'chat{}'.format(event.chat_id): {
                                'is_muted': 'False',
                                'faggots': {

                                }
                            }
                            }
                            appendChatJSON(data)
            if "чича добавить пидораса" in event.message.text.lower():
                for u in users['items']:
                    if u['member_id'] == event.message.from_id:
                        admin = u.get('is_admin', False)
                        if admin:
                            repliedMessage = event.message.reply_message
                            data = {'user{}'.format(repliedMessage['from_id']): {
                                'id': repliedMessage['from_id']
                            }
                            }
                            appendToFaggotsJSON(data, event.chat_id)
                            sendMessage(
                                '{} причислен к списку пидорасов'.format(getUserName(repliedMessage['from_id'], vk)),
                                event.chat_id)
                        else:
                            sendMessage('Недостаточно прав', event.chat_id)
            if "чича покажи пидорасов" in event.message.text.lower() or "чича показать пидорасов" in event.message.text.lower():
                faglist = []
                with open('chatLists.json', 'r') as cl:
                    data = json.load(cl)

                fagmsg = 'Список пидорасов этой беседы:\n'

                fagJSON = getFromDict(data, ['chats', 'chat{}'.format(event.chat_id), 'faggots'])
                for key, value in fagJSON.items():
                    faglist.append(getUserName(value['id'], vk))
                sendMessage(appendArrToMsg(faglist, fagmsg), event.chat_id)
            if "чича удалить пидораса" in event.message.text.lower() or "чича убрать из пидорасов" in event.message.text.lower():
                try:
                    deleteFromFaggotsJSON(cleanUserIdFromMsgMention(event.message.text))
                    sendMessage('{} успешно вынесен из списка пидорасов'.format(
                        getUserName(cleanUserIdFromMsgMention(event.message.text), vk)))
                except Exception as ex:
                    sendMessage('Пользователь не найден в списке.{}'.format(ex.message), event.chat_id)
                    print(cleanUserIdFromMsgMention(event.message.text))
