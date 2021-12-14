
import praw
import json
import csv
from typing import List
import os


def get_client_secrets():
    with open("client_secrets", "r") as f:
        return json.load(f)


def append_new_users_to_file(subreddit, users):
    if not os.path.exists(f"{subreddit}_users.csv"):
        with open(f"{subreddit}_users.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows([[user] for user in users])
            return

    with open(f"{subreddit}_users.csv") as f:
        reader = csv.reader(f)
        existing_users = set(row[0] for row in reader)
    all_users = existing_users.union(users)
    with open(f"{subreddit}_users.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows([[user] for user in all_users])


def get_all_recent_users_for_a_subreddit(reddit: praw.Reddit, subreddit_name, limit=1000) -> List[praw.models.Redditor]:
    sub_reddit: praw.models.Subreddit = reddit.subreddit(subreddit_name)
    print(f"collecting data for: {sub_reddit.title}")

    redditors = set()
    hot_topics = sub_reddit.new(limit=limit)
    for topic in hot_topics:
        try:
            print("Topic title", topic.title)
            print("Topic author", topic.author)
            redditors.add(topic.author.name)

            print("Total number of comments for this topic:", len(topic.comments))
            topic.comments.replace_more(limit=None)
            for comment in topic.comments.list():
                print("Comment author", comment.author)
                if comment.author:
                    redditors.add(comment.author.name)
        except Exception as e:
            print(e)
            continue

    return redditors


def gather():
    secrets = get_client_secrets()
    reddit = praw.Reddit(
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        refresh_token=secrets["refresh_token"],
        user_agent="script")
    china_irl_users = get_all_recent_users_for_a_subreddit(reddit, "china_irl")
    chonglang_tv_users = get_all_recent_users_for_a_subreddit(
        reddit, "chonglangTV")
    print("Total number of users gahtered this time in china_irl: ",
          len(china_irl_users))
    print("Total number of users gathered this time in chonglangTV: ",
          len(chonglang_tv_users))

    append_new_users_to_file("china_irl", china_irl_users)
    append_new_users_to_file("chonglangTV", chonglang_tv_users)


def analysis():
    with open("china_irl_users.csv") as f:
        reader = csv.reader(f)
        china_irl_users = set(row[0] for row in reader)
    with open("chonglangTV_users.csv") as f:
        reader = csv.reader(f)
        chonglang_tv_users = set(row[0] for row in reader)

    print("Total number of users in china_irl: ", len(china_irl_users))
    print("Total number of users in chonglangTV: ", len(chonglang_tv_users))
    print("Total number of users in both: ", len(
        china_irl_users.intersection(chonglang_tv_users)))


if __name__ == "__main__":
    gather()
    analysis()
