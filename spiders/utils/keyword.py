import jieba
from db import db
from time import sleep

video_filter = {'aid': 1, 'channel': 1,
                'subChannel': 1, 'title': 1, 'author': 1, 'tag': 1}


class KeywordAdder():

  def __init__(self):
    super().__init__()
    self.db = db

  def get_video_by_aid(self, aid):
    return self.db.video.find_one({'aid': aid}, video_filter)

  def get_video(self):
    return self.db.video.find({}, video_filter)

  def get_keyword_by_video(self, video):
    keywords = set()
    if 'title' in video:
      keywords.update(jieba.lcut_for_search(video['title']))
    if 'tag' in video:
      keywords.update(video['tag'])
      for each_tag in video['tag']:
        keywords.update(jieba.lcut_for_search(each_tag))
    for key in ['channel', 'subChannel', 'author']:
      if key in video:
        keywords.add(video[key])
        keywords.update(jieba.lcut_for_search(video[key]))
    keywords.difference_update(
        {'的', '】', '【', '·', '_', ' ', '~', '!', '！', '。', '.', '-', '/', '、', '丶', ' ', '"', '(', ')', '（', '）'})
    for each_word in keywords:
      jieba.add_word(each_word)
    return list(keywords)

  def get_keyword_by_aid(self, aid):
    return self.get_keyword_by_video(self.get_video_by_aid(aid))

  def update_keyword_by_aid(self, aid):
    keyword = self.get_keyword_by_aid(aid)
    self.db.video.update({'aid': aid}, {
        '$set': {
            'keyword': keyword
        }
    })
    return keyword

  def update_keyword_by_video(self, video):
    keyword = self.get_keyword_by_video(video)
    self.db.video.update({'aid': video['aid']}, {
        '$set': {
            'keyword': keyword
        }
    })
    return keyword

  def add_all(self):
    for each_video in self.get_video():
      keywords = self.update_keyword_by_video(each_video)
      print(keywords)

  def auto_add(self):
    while True:
      sleep(10)
      for each_video in self.db.video.find({'keyword': {'$exists': False}, 'tag': {'$exists': True}}, video_filter):
        print(each_video['aid'])
        pass


if __name__ == "__main__":
  ka = KeywordAdder()
  ka.auto_add()
  pass
