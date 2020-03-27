import paramiko
import os
import shutil

ROOT_DIR = "/home/slam/GIdSeg/checkpoints"
MODEL_NAME = "PointConv_semantic"
SAVE_ROOT_DIR = "/home/slambox/gidseg" + "/" + MODEL_NAME
RECOLLECT_DATA = True

SHH = True
SSH_HOST = "fuego.sbp.ri.cmu.edu"  
SSH_PASSWORD = "slam"
SSH_USERNAME = "slam"
SSH_PORT = 17219
THRESHOLD = True
THRESHOLD_VALUE = 0.794772

# First step
# Try to find best value 
def retrieve_folder_find_best():
    log_file = ""
    
    if(SHH):
        client =paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=SSH_HOST,port=SSH_PORT,username=SSH_USERNAME,password=SSH_PASSWORD)
        ssh_client = client.open_sftp()

        for file in ssh_client.listdir(ROOT_DIR + "/" + MODEL_NAME):
            if file.endswith(".log"):
                log_file = ROOT_DIR + "/" + MODEL_NAME + "/" +file
                break
        f = ssh_client.open(log_file, "r")
    else:
        for file in os.listdir(ROOT_DIR + "/" + MODEL_NAME):
            if file.endswith(".log"):
                log_file = ROOT_DIR + "/" + MODEL_NAME + "/" +file
                break
        f = open(log_file, "r")

    best_test_acc = 0
    best_epoch_number = 0
    epoch_line = ""

    for line in f:
        line_elements = line.split()
        if(THRESHOLD):
            if(line_elements[0] == "Test" and float((line_elements[6])[0:-1]) == THRESHOLD_VALUE):
                best_test_acc = float((line_elements[6])[0:-1])
                best_epoch_number = int((line_elements[1])[0:-1])
                epoch_line = line
        else:
            if(line_elements[0] == "Test" and float((line_elements[6])[0:-1]) > best_test_acc):
                best_test_acc = float((line_elements[6])[0:-1])
                best_epoch_number = int((line_elements[1])[0:-1])
                epoch_line = line
    

    f.close()
    
    return (best_epoch_number, epoch_line)

# Second
# Save all six files in the saving directories
def save_results(best_epoch_number, epoch_line):
    if(RECOLLECT_DATA):
        if os.path.exists(SAVE_ROOT_DIR):
            shutil.rmtree(SAVE_ROOT_DIR)
    
    if not os.path.exists(SAVE_ROOT_DIR):
        os.makedirs(SAVE_ROOT_DIR)


    if(SHH):
        client =paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=SSH_HOST,port=SSH_PORT,username=SSH_USERNAME,password=SSH_PASSWORD)
        ssh_client = client.open_sftp()

    # .pth
    if(SHH):
        for file in ssh_client.listdir(ROOT_DIR + "/" + MODEL_NAME + "/" + "models"):
            if file.endswith(".pth") and file.startswith(str(best_epoch_number) + '-'):
                ssh_client.get(ROOT_DIR + "/" + MODEL_NAME + "/" + "models/" + file, SAVE_ROOT_DIR + "/" + file)
                break
    else:
        for file in os.listdir(ROOT_DIR + "/" + MODEL_NAME + "/" + "models"):
            if file.endswith(".pth") and file.startswith(str(best_epoch_number) + '-'):
                shutil.copy(ROOT_DIR + "/" + MODEL_NAME + "/" + "models/" + file, SAVE_ROOT_DIR)
                break

    # .log
    f = open(SAVE_ROOT_DIR + '/' + MODEL_NAME + ".log", "w")
    f.write(epoch_line)
    f.close()

    # 3 .npy
    if(SHH):
        for file in ssh_client.listdir(ROOT_DIR + "/" + MODEL_NAME + "/" + "results"):
            if file.endswith('_' + str(best_epoch_number) + ".npy") and file.startswith("test"):
                ssh_client.get(ROOT_DIR + "/" + MODEL_NAME + "/" + "results/" + file, SAVE_ROOT_DIR + "/" + file)
    else:
        for file in os.listdir(ROOT_DIR + "/" + MODEL_NAME + "/" + "results"):
            if file.endswith('_' + str(best_epoch_number) + ".npy") and file.startswith("test"):
                shutil.copy(ROOT_DIR + "/" + MODEL_NAME + "/" + "results/" + file, SAVE_ROOT_DIR)

    # .npy
    if(SHH):
        for file in ssh_client.listdir(ROOT_DIR + "/" + MODEL_NAME):
            if file.endswith(".npy"):
                ssh_client.get(ROOT_DIR + "/" + MODEL_NAME + "/" + file, SAVE_ROOT_DIR + "/" + file)
    else:
        for file in os.listdir(ROOT_DIR + "/" + MODEL_NAME):
            if file.endswith(".npy"):
                shutil.copy(ROOT_DIR + "/" + MODEL_NAME + "/" + file, SAVE_ROOT_DIR)

def main():
    [best_epoch_number, epoch_line] = retrieve_folder_find_best()
    save_results(best_epoch_number, epoch_line)

main()
