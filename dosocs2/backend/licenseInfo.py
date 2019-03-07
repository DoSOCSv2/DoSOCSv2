
import json
import re
import subprocess
import os

def license():
    print("LICENSE INFO")
    return "OK"

def retrieve_license_information(owner, repo):
    print("PULLING")
    repo_url = 'https://github.com/' + owner + '/' + repo + '.git'

    cwd = os.path.dirname(os.path.realpath(__file__))

    temp = open("temp.txt", "r+")
    subprocess.call(['sudo', 'git', 'clone', repo_url, cwd + '/repodl/' + repo], shell=False)
    pope = subprocess.Popen(['sudo', 'dosocs2', 'oneshot', cwd + '/repodl/' + repo], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call(['sudo', 'dosocs2', 'oneshot', cwd + '/repodl/' + repo], shell=False, stdout=temp)
    out, err = pope.communicate()
    #if out:
    #    print(out)
    if err:
         print(err.decode('UTF-8'))

    splitOut = out.decode('UTF-8').splitlines()
    #print(splitOut)
    temp = {}
    license_info = []
    j = 0
    section = "NONE"
    for value in splitOut:
        if ":" in value:
            valSplit = value.split(":")
            print(valSplit)
            temp[str(j) + " " + valSplit[0]] = valSplit[1]
            j += 1
        if "#" in value:
            if bool(temp) != 0:
                license_info.append(temp)
            section = value
            j = 0
            temp = {}
    print(temp)
    return json.dumps(license_info)
