import configparser

import vk_api

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


class VkGroupParser:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=config['vk']['ACCESS_TOKEN'], api_version='5.126')
        self.vk = self.vk_session.get_api()
        self.tools = vk_api.VkTools(self.vk_session)

    def vk_wall_search(
            self,
            owner_id=int(config['vk']['VK_COMMUNITY_ID']),
            query='#расписаниесеансов',
            count=1
    ):
        posts = []
        for item in self.vk.wall.search(owner_id=owner_id, query=query, count=count)['items']:
            img_url = None
            try:
                for size in item['attachments'][0]['photo']['sizes']:
                    if '&proxy=1&' in size['url']:
                        img_url = size['url']
            except KeyError:
                img_url = item['attachments'][0]['doc']['url']
            posts.append({'title': self.__vk_post_edit(item['text']), 'url': img_url})
        return posts

    def __vk_post_edit(self, text):
        return text.replace(
            ' \n \n#киновГубахе #кинозалвГубахе #кинотеатрвГубахе'
            ' #кинозалКиноЛит #расписаниесеансов #кино #Губаха #КиноЛит',
            '',
        )


if __name__ == '__main__':
    vk = VkGroupParser()
    print(vk.vk_wall_search())
