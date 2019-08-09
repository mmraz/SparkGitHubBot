from flask import Flask, request, abort
import json 
import urllib2
import hmac
import hashlib

app = Flask(__name__)

#Secret provided in the Github webhook config. Change this to your own secret phrase
SECRET_TOKEN = "123EventsToSparkRoom"

@app.route('/', methods =['POST'])

def githubCommits():
    '''This function validates if the request is properly signed by Github.
       (If not, this is a spoofed webhook).
       Then collects the webhook payload sent from Github and parses the parameters you want to send to Spark Room.
    '''
    headers = request.headers
    incoming_signature = headers.get('X-Gitlab-Token')
    signature = 'sha1=' + hmac.new(SECRET_TOKEN, request.data, hashlib.sha1).hexdigest()
    
    if incoming_signature is None:
       abort(401)
    
    elif signature == incoming_signature:
        
        json_file = request.json
        
        
        if 'Push Hook' == headers.get('X-Gitlab-Event'):
            commit = json_file['commits'][0]
            commit_id = commit['id']
            commit_message = commit['message']
            commit_time = commit['timestamp']
            commit_url = commit['url']
            commit_author_name = commit['author']['name']
            pusher_name = json_file['user_name']['name']
            repo_name = json_file['repository']['name']
            results = """**Author**: {0}\n\n**Pusher**: {1}\n\n**Commit Message**: {2}\n\n**Commit id**: {3}\n\n**Time**: {4}\n\n**Repository**: {5}\n\n**Commit Link**: {6}<br><br>""".format(commit_author_name,pusher_name,commit_message,commit_id,commit_time,repo_name,commit_url)
            toSpark(results)
            return 'Ok'
            
        elif 'Note Hook' == headers.get('X-Gitlab-Event'):
            comment_raw = json_file['object_attributes']
            comment_url = comment_raw['url']
            comment_user = json_file['user']['name']
            commit_id = comment_raw['commit_id']
            comment = comment_raw['note']
            comment_repo = json_file['project']['name']
            results = """**User**: {0}\n\n**Comment on Commit**: {1}\n\n**Comment url**: {2}\n\n**Commit id**: {3}\n\n**Repository**: {4}<br><br>""".format(comment_user,comment,comment_url,commit_id,comment_repo)
            toSpark(results)
            return 'Ok'
     
    else:
        print "Spoofed Hook"
        abort(401)
        
        
# POST Function  that sends the commits & comments in markdown to a Spark room    
def toSpark(commits):
    url = 'https://api.ciscospark.com/v1/messages'
    headers = {'accept':'application/json','Content-Type':'application/json','Authorization': 'Bearer ZDU0ZjkyNDAtODBlMS00NzExLWJjYmMtOGE5YzU1NWYyMjIyNWJmYTNmOTItMDk4_PF84_e21bb5d5-a909-4502-9608-2708d7ac58c3'}
    values =   {'roomId':'Y2lzY29zcGFyazovL3VzL1JPT00vNWI5ZWFlMjktZGNmNi0zODE5LWFiNjUtODVhNGY1ODBlMGVm', 'markdown': commits }
    data = json.dumps(values)
    req = urllib2.Request(url = url , data = data , headers = headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return the_page

if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=8080, debug=True)
