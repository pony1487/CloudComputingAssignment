from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename
import sys
app = Flask(__name__)

def main():
    menu()


def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
   # if stderr.startswith('Error'):
   #     print('Error: {0} -> {1}'.format(' '.join(cmd), stderr))
    return stderr + stdout


def index():
    print("Available API endpoints:")
    print("GET /containers                     List all containers")
    print("GET /containers?state=running      List running containers (only)")
    print("GET /containers/<id>                Inspect a specific container")
    print("GET /containers/<id>/logs           Dump specific container logs")
    print("GET /images                         List all images")
    print("POST /images                        Create a new image")
    print("POST /containers                    Create a new container")
    print("PATCH /containers/<id>              Change a container's state")
    print("PATCH /images/<id>                  Change a specific image's attributes")
    print("DELETE /containers/<id>             Delete a specific container")
    print("DELETE /containers                  Delete all containers (including running)")
    print("DELETE /images/<id>                 Delete a specific image")
    print("DELETE /images                      Delete all images")

#1)list all containers
def containers_index():
    print("---------CONTAINERS---")
    output = docker('ps')
    output = output.decode('utf-8')
    print(output)
#2)list images
def images_index():
    print("---------IMAGES--------")
    output = docker('images')
    #the output is diagonal if you dont do the decode bit
    output = output.decode('utf-8')
    print(output)

#3)inspect specific container
def containers_show(id):
    output = docker('inspect','--format=\'{{.Config.Image}}\'',id)
    output = output.decode('utf-8')
    print("\tContainer name: \t" + output)
    print("\tID: \t" + id)

#4)Dump a specifici container log
def dump_container_log(id):
    print("---------CONTAINER LOG--")
    output = docker('logs',id)
    output = output.decode('utf-8')
    print(output)

#5)Delete a specific image
def images_remove(id):
    print("---------IMAGE REMOVE---")
    print(id)
    output = docker('rmi','-f',id)
    output = output.decode('utf-8')
    print(output)

#6)Delete a specific container: must be stopped
def containers_remove(id):
    print("-----CONTAINER REMOVE----")
    docker('stop',id)
    docker('rm',id)
    print(id + ' has been removed')
    

#7)Remove all containers
def containers_remove_all():
    print("----REMOVE ALL CONTAINER--")
    '''
    #I tried this way but it doesnt work
    output = docker('stop','$(docker ps -a -q)')
    output = output.decode('utf-8')
    print(output)
    '''
    #list all the containers
    output = docker('ps','-a')
    #put them in a array so each container can be accessed
    containerList = []
    containerList = docker_ps_to_array(output)

    #make sure there is containers in the list so it doesnt get stuck infintely
    if len(containerList) == 0:
        print("No containers running")
    else:    
        #loop through array and stop each container indiviually
        for container in containerList:
            #get the id of each container so it can be used for the docker commands
            id = container['id']
            docker('stop',id)
            docker('rm', id)

#8)Remove all images
def images_remove_all():
    print("-----REMOVE ALL CONTAINER---")
    #list all the images
    output = docker('images')
    #put them in a array so each image can be accessed
    imageList = []
    imageList = docker_images_to_array(output)

    #make sure there is containers in the list so it doesnt get stuck infintely
    if len(imageList) == 0:
        print("No images available")
    else:    
        #loop through array and stop each container indiviually
        for image in imageList:
            #get the id of each image so it can be used for the docker commands
            id = image['id']
            docker('rmi','-f',id)
        

#9)Create a container-using existing image
def containers_create(imageName):
    print("containers create called")
    #not working :-/
    docker('run','-p','80:5000','-d',imageName)

#10)Create image from uploaded Dockerfile(Pass path to it?)
def images_create(dockerFilePath):
    print("images_create")
    print(dockerFilePath)
    #not working
    docker('build', '-t', 'newImage',dockerFilePath)

#11)Update containers attributes
def containers_update(id):
    print("containers create called")
    print(id)
    #I couldnt get these working. I put the command here to show I tried
    docker('container','update','--memory',id)
#12)update image
def images_update(id):
    #same as above. 
    print("images_update called")
    print(id)
'''
#get from cmd line
if(sys.argv[1] == "/"):
    index()
elif(sys.argv[1] == "containers"):
    containers_index()
elif(sys.argv[1] == "images"):
    images_index()
'''

def menu():
    ##Run menu
    menu_running = True
    while(menu_running):
        print("--------MENU---------")
        print("1)  List all containers")
        print("2)  List images")
        print("3)  Inspect specific container")
        print("4)  Dump specific container log")
        print("5)  Delete a specific image")
        print("6)  Delete a specific container-must be already stopped")
        print("7)  Remove all containers")
        print("8)  Remove all images")
        print("9)  Create a  container using existing image id or name")
        print("10) Create image from uploaded Dockerfile")
        print("11) Update a containers attributes")
        print("12) Update image attributes")
        print("13) EXIT\n")
        print("----------------------")
        user_choice = int(input("Enter a menu choice\n\n"))
        

        if(user_choice == 1):
            containers_index()
        elif(user_choice == 2):
            images_index()
        elif(user_choice == 3):
            id = str(input("Enter id for container\n"))
            containers_show(id)
        elif(user_choice == 4):
            id = str(input("Enter id for container(Log)\n"))
            dump_container_log(id)
        elif(user_choice == 5):
            id = str(input("Enter id for delete image\n"))
            images_remove(id)
        elif(user_choice == 6):
            id = str(input("Enter id for deleting container\n"))
            containers_remove(id)
        elif(user_choice == 7):
            containers_remove_all()
        elif(user_choice == 8):
            images_remove_all()
        elif(user_choice == 9):
            imageID = str(input("Enter image NAME to build docker container\n"))
            containers_create(imageID)
        elif(user_choice == 10):
            filePath = str(input("Enter file path to Dockerfile\n"))
            images_create(filePath)
        elif(user_choice == 11):
            id = int(input("Enter id of container to update\n"))
            containers_update(id)
        elif(user_choice == 12):
            id = int(input("Enter id of image to upadte\n"))
            images_update(id)
        elif(user_choice == 13):
            menu_running = False

    print("goodbye")




#]rses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0]
        each['image'] = c[1]
        each['name'] = c[-1]
        each['ports'] = c[-2]
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2]
        each['tag'] = c[1]
        each['name'] = c[0]
        all.append(each)
    return all


if __name__ == "__main__":
    main()
