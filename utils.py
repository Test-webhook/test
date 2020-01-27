import requests

PULL_REQUEST = "pull_request"
ACTION = "action"
CLOSED = "closed"
OPENED = "opened"
REVIEWS = "reviews"
REVIEW_REQUESTED = "review_requested"
REQUESTED_REVIEWERS = "requested_reviewers"
SYNCHRONIZE = "synchronize"
HEADER = {'key': 'Authorization', 'value': 'token caf764c257fd141192dc4f369bab1d7f1827a'}
URL = "url"
NUMBER = "number"
TITLE = "title"
USER = "user"
LOGIN = "login"
BODY = "body"
CREATED_AT = "created_at"
CLOSED_AT = "closed_at"
REPO = "repo"
NAME = "name"
BASE = "base"
ADDITIONS = "additions"
DELETIONS = "deletions"
CHANGED_FILES = "changed_files"
NUMBER_REVIEWERS_ADDED = "number_of_reviewers_added"
NUMBER_REVIEWERS_PARTICIPATED = "number_of_reviewers_participated"
FIRST_COMMENT_TIME = "first_comment_time"
COMMIT_ID = "commit_id"
NIL = "nil"
NUMBER_OF_COMMENTS_ADDED = "number_of_comments_added"
NUMBER_OF_COMMITS = "number_of_commits"
COMMITS = "commits"


def store_data_in_dictionary(event_data, pr_dict):
    if PULL_REQUEST in event_data and ACTION in event_data:
        if event_data[ACTION] == OPENED:
            return store_pr_open_data_in_dictionary(event_data, pr_dict)
        elif event_data[ACTION] == REVIEW_REQUESTED:
            return store_pr_review_requested_data_in_dictionary(event_data, pr_dict)
        elif event_data[ACTION] == SYNCHRONIZE:
            return store_pr_synchronized_data_in_dictionary(event_data, pr_dict)
        elif event_data[ACTION] == CLOSED:
            return store_pr_closed_data_in_dictionary(event_data, pr_dict)
        else:
            print("not in given format")
            return pr_dict
    else:
        print("not PULL request")
        return pr_dict


def store_pr_open_data_in_dictionary(event_data, pr_dict):
    pr_data = fetch_pr_data_using_github_api(event_data[PULL_REQUEST][URL])
    key = generate_key(pr_data)
    pr_dict[key] = {NUMBER: pr_data[NUMBER],
                    TITLE: pr_data[TITLE],
                    USER: pr_data[USER][LOGIN],
                    BODY: pr_data[BODY],
                    CREATED_AT: pr_data[CREATED_AT],
                    CLOSED_AT: NIL,
                    REPO: pr_data[BASE][REPO][NAME],
                    ADDITIONS: pr_data[ADDITIONS],
                    DELETIONS: pr_data[DELETIONS],
                    CHANGED_FILES: pr_data[CHANGED_FILES],
                    NUMBER_REVIEWERS_ADDED: 0,
                    NUMBER_REVIEWERS_PARTICIPATED: 0,
                    FIRST_COMMENT_TIME: NIL,
                    COMMIT_ID: NIL,
                    NUMBER_OF_COMMENTS_ADDED: 0,
                    NUMBER_OF_COMMITS: 0}
    return pr_dict


def store_pr_review_requested_data_in_dictionary(event_data, pr_dict):
    pr_data = fetch_pr_data_using_github_api(event_data[PULL_REQUEST][URL])
    key = generate_key(pr_data)
    pr_dict[key][NUMBER_REVIEWERS_ADDED] = pr_dict[key][NUMBER_REVIEWERS_ADDED] + 1

    return pr_dict


def store_pr_synchronized_data_in_dictionary(event_data, pr_dict):
    pr_data = fetch_pr_data_using_github_api(event_data[PULL_REQUEST][URL])
    key = generate_key(pr_data)
    pr_dict[key][NUMBER_OF_COMMITS] = pr_data[COMMITS]
    pr_dict[key][ADDITIONS] = pr_data[ADDITIONS]
    pr_dict[key][DELETIONS] = pr_data[DELETIONS]
    pr_dict[key][CHANGED_FILES] = pr_data[CHANGED_FILES]

    return pr_dict


def store_pr_closed_data_in_dictionary(event_data, pr_dict):
    pr_data = fetch_pr_data_using_github_api(event_data[PULL_REQUEST][URL])
    reviews_data = fetch_pr_data_using_github_api(event_data[PULL_REQUEST][URL] + "/" + REVIEWS)
    key = generate_key(pr_data)
    pr_dict[key][CLOSED_AT] = pr_data[CLOSED_AT]
    pr_dict[key][NUMBER_REVIEWERS_PARTICIPATED] = pr_dict[key][NUMBER_REVIEWERS_ADDED] - len(
        pr_data[REQUESTED_REVIEWERS])
    pr_dict[key][NUMBER_OF_COMMENTS_ADDED] = len(reviews_data)

    return pr_dict


def fetch_pr_data_using_github_api(url):
    # sending get request and saving the response as response object
    resPull = requests.get(url=url, headers=HEADER)
    # extracting data in json format
    pr_data = resPull.json()

    return pr_data


def generate_key(pr_data):
    prNumber = pr_data[NUMBER]
    repoName = pr_data[BASE][REPO][NAME]
    key = str(repoName) + "_" + str(prNumber)
    return key

# def pr_commit_handler(event):
#     payload = {SHA: event[HEAD][SHA],
#               ID: event[ID],
#               AUTHOR: event[USER][LOGIN],
#               COMMIT_TIME: event[UPDATED_AT]
#               }

#     print("pr_commit_handler payload :",payload)

# def pr_comment_handler(event):
#     payload = { ID : event[PULL_REQUEST][ID],
#                 REVIEWER : event[REVIEW][USER][LOGIN],
#                 COMMENT_TIME : event[REVIEW][SUBMITTED_AT]
#               }
#     print("pr_comment_handler :",payload)

