import configparser

import vk_api

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


class VkGroupParser:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=config['vk']['ACCESS_TOKEN'])
        self.vk = self.vk_session.get_api()
        self.tools = vk_api.VkTools(self.vk_session)

    def vk_wall_search(
            self,
            owner_id=int(config['vk']['VK_COMMUNITY_ID']),
            query=config['vk']['VK_SEARCH_QUERY'],
            count=1
    ):
        posts = []
        for item in self.vk.wall.search(owner_id=owner_id, query=query, count=count)['items']:
            img_url = None
            for size in item['attachments'][0]['photo']['sizes']:
                if size['type'] == 'w':
                    img_url = size
                    break
                elif size['type'] == 'z':
                    img_url = size
                    break
                elif size['type'] == 'y':
                    img_url = size
                    break
            posts.append({'title': self.__vk_post_edit(item['text']), 'url': img_url['url']})
        return posts

    @staticmethod
    def __vk_post_edit(text):
        return text.replace(
            ' \n \n#киновГубахе #кинозалвГубахе #кинотеатрвГубахе'
            ' #кинозалКиноЛит #расписаниесеансов #кино #Губаха #КиноЛит',
            '',
        )


if __name__ == '__main__':
    vk = VkGroupParser()
    print(vk.vk_wall_search())
