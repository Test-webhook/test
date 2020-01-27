import json
from botocore.vendored import requests

ACTION = "action"
ADDITIONS = "additions"
AUTHOR = "author"
BASE = "base"
BODY = "body"
CHANGED_FILES = "changed_files"
CLOSED = "closed"
CLOSED_AT = "closed_at"
COMMITS = "commits"
COMMIT = "commit"
COMMIT_TIME = "commit_time"
COMMENT_TIME = "comment_time"
CREATED_AT = "created_at"
DELETIONS = "deletions"
FULL_NAME = "full_name"
FILES = "files"
FILENAME = "filename"
HEAD = "head"
HEADER = {'key': 'Authorization', 'value': 'token caf764c257fd141192dc4f369bab1d7f1827a'}
ID = "id"
LOGIN = "login"
MERGED_AT = "merged_at"
MERGED_BY = "merged_by"
MESSAGE = "message"
NUMBER = "number"
NAME = "name"
NUMBER_REVIEWERS_ADDED = "number_of_reviewers_added"
NONE = "none"
OPENED = "opened"
PULL_REQUEST = "pull_request"
PATH = "path"
POSITION = "position"
PARTICIPATED_REVIEWERS = "participated_reviewers"
REVIEW_REQUESTED = "review_requested"
REQUESTED_REVIEWERS = "requested_reviewers"
REVIEW = "review"
REVIEWS = "reviews"
REVIEWER = "reviewer"
REVIEWER_PARTICIPATED = "reviewer_participated"
REPO = "repo"
SYNCHRONIZE = "synchronize"
SHA = "sha"
SUBMITTED = "submitted"
SUBMITTED_AT = "submitted_at"
STATS = "stats"
TITLE = "title"
URL = "url"
USER = "user"
UPDATED_AT = "updated_at"


def lambda_handler(event, context):
    event = event[BODY]
    print("event :", event)
    event = json.loads(event)

    if PULL_REQUEST in event and ACTION in event:
        if event[ACTION] == OPENED:
            pr_open_handler(event[PULL_REQUEST])
        elif event[ACTION] == REVIEW_REQUESTED:
            pr_review_requested_handler(event[PULL_REQUEST])
        elif event[ACTION] == CLOSED:
            pr_close_handler(event[PULL_REQUEST])
        else:
            print("This PR action is not required to process")
    else:
        print("It is not a PR event")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda pull request function!')
    }


# process PR open request and sends the payload to data-lake
def pr_open_handler(event):
    payload = {ACTION: OPENED,
               ID: event[ID],
               REPO: event[BASE][REPO][NAME],
               NUMBER: event[NUMBER],
               TITLE: event[TITLE],
               AUTHOR: event[USER][LOGIN],
               CREATED_AT: event[CREATED_AT],
               ADDITIONS: event[ADDITIONS],
               DELETIONS: event[DELETIONS],
               CHANGED_FILES: event[CHANGED_FILES]
               }

    print("pr_open_handler payload :", payload)


# process PR review_requested  event and sends the payload to data-lake
def pr_review_requested_handler(event):
    requested_reviewers = []

    for i in range(len(event[REQUESTED_REVIEWERS])):
        requested_reviewers.append(event[REQUESTED_REVIEWERS][i][LOGIN])

    payload = {ACTION: REVIEW_REQUESTED,
               ID: event[ID],
               REPO: event[BASE][REPO][NAME],
               NUMBER: event[NUMBER],
               REQUESTED_REVIEWERS: requested_reviewers
               }

    print("pr_review_requested_handler :", payload)


# process PR close request and sends the payload to data-lake
def pr_close_handler(event):
    url = event[URL]
    reviews, participated_reviewers = get_pr_reviews_and_reviewers(url + "/reviews")
    comments = get_pr_comments(url + "/comments")
    commits = get_pr_commits(url + "/commits")

    payload = {ACTION: CLOSED,
               ID: event[ID],
               REPO: event[BASE][REPO][NAME],
               NUMBER: event[NUMBER],
               TITLE: event[TITLE],
               AUTHOR: event[USER][LOGIN],
               CREATED_AT: event[CREATED_AT],
               CLOSED_AT: event[CLOSED_AT],
               MERGED_AT: NONE,
               MERGED_BY: NONE,
               ADDITIONS: event[ADDITIONS],
               DELETIONS: event[DELETIONS],
               CHANGED_FILES: event[CHANGED_FILES],
               PARTICIPATED_REVIEWERS: participated_reviewers,
               REVIEWS: reviews,
               COMMENTS: comments,
               COMMITS: commits
               }

    if MERGED_BY != "null":
        payload[MERGED_AT] = event[MERGED_AT]
        payload[MERGED_BY] = event[MERGED_BY][LOGIN]

    print("pr_close_handler payload :", payload)


def get_pr_reviews_and_reviewers(url):
    reviews_data = fetch_pr_data_using_github_api(url)
    reviews = []

    if MESSAGE in reviews_data:
        print(" Git hub API limit accceded")
        return reviews

    for i in range(len(reviews_data)):
        if reviews_data[BODY] != "":
            review = {ID: reviews_data[i][ID],
                      AUTHOR: reviews_data[i][USER][LOGIN],
                      BODY: reviews_data[i][BODY],
                      SUBMITTED_AT: reviews_data[i][SUBMITTED_AT]
                      }
            reviews.append(review)

    print("pr_reviews_payload :", reviews)

    participated_reviewers = get_participated_reviewers(reviews_data)
    return reviews, participated_reviewers


def get_participated_reviewers(reviews_data):
    reviewers = {}

    for i in range(len(reviews_data)):
        reviewers[reviews_data[i][USER][LOGIN]] = reviews_data[i][USER][LOGIN]

    participated_reviewers = []

    for key in reviewers:
        participated_reviewers.append(reviewers[key])

    return participated_reviewers


def get_pr_comments(url):
    comments_data = fetch_pr_data_using_github_api(url)
    comments = []

    if MESSAGE in comments_data:
        print(" Git hub API limit accceded")
        return comments

    for i in range(len(comments_data)):
        comment = {ID: comments_data[i][ID],
                   PATH: comments_data[i][PATH],
                   POSITION: comments_data[i][POSITION],
                   AUTHOR: comments_data[i][USER][LOGIN],
                   BODY: comments_data[i][BODY],
                   CREATED_AT: comments_data[i][CREATED_AT]
                   }
        comments.append(comment)

    print("pr_review_comments :", comments)
    return comments


def get_pr_commits(url):
    commits = []
    commits_data = fetch_pr_data_using_github_api(url)

    for i in range(len(commits_data)):
        _url = commits_data[COMMIT][URL]
        _url = _url.split("/git")
        commit_url = str(_url[0] + _url[1])
        commit_data = fetch_pr_data_using_github_api(commit_url)
        commit = fetch_required_data_from_specific_commit(commit_data)
        commits.append(commit)

    return commits


def fetch_required_data_from_specific_commit(commit_data):
    files = []

    for i in range(len(commit_data[FILES])):
        file_info = {FILENAME: commit_data[FILES][i][FILENAME],
                     ADDITIONS: commit_data[FILES][i][ADDITIONS],
                     DELETIONS: commit_data[FILES][i][DELETIONS]
                     }
        files.append(file_info)

    stats = {ADDITIONS: commit_data[STATS][ADDITIONS],
             DELETIONS: commit_data[STATS][DELETIONS]
             }
    commit = {AUTHOR: commit_data[COMMIT][AUTHOR][NAME],
              MESSAGE: commit_data[COMMIT][MESSAGE],
              FILES: files,
              STATS: stats
              }

    return commit


def fetch_pr_data_using_github_api(url):
    # sending get request and saving the response as response object
    res_pull = requests.get(url=url)

    # extracting data in json format
    pr_data = res_pull.json()

    return pr_data
