# Import modules
import subprocess
import ipaddress
import time
import csv
import os.path
import os
import keyboard


def newline():
    print('')


def listFiles():
    # list the .scan files in the working directory
    files = os.listdir(".\\")
    newline()
    print("Name\t\tCIDR")
    for file in files:
        if '.scan' in file:
            splitFile = file.split('_')
            splitExt = splitFile[2].split('.')
            print(splitFile[0] + "\t\t" + splitFile[1] + "/" + splitExt[0])


def openRead(file):
    # Prints contents of file to terminal
    try:
        with open(file) as openFile:
            readFile = openFile.read()
            print(readFile)
            newline()
    except:
        print('\nerror~! Help file ' + file + ' is missing!')
        newline()


def help(detail):
    # Pipes help files to openRead(file)
    if detail == '?' or detail == '? ':
        newline()
        openRead(".\help\helpShort.txt")
    elif detail == 'scan' or detail == 'scan ' or detail == 'scan ?':
        newline()
        openRead(".\help\helpScan.txt")


def ipscan(scanArg):
    # Scans network defined by user
    # Creates a file if there isn't one, updates the file if there is
    if '?' in scanArg:
        newline()
        openRead(".\help\helpScan.txt")
    # Build the network address and name from user input
    splitArg = scanArg.split(' ')
    netAddr = splitArg[1]
    networkName = splitArg[2] + '_' + \
        netAddr.split('/')[0] + '_' + netAddr.split('/')[-1]+".scan"
    # Create the network
    ip_net = ipaddress.ip_network(netAddr)
    all_hosts = list(ip_net.hosts())

    # Configure subprocess to hide the console window
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
    # create the file path (currently working directory)
    file_path = ("./" + networkName)
    # If the file exists
    if os.path.isfile(file_path):
        # Read the file into the OrderedDict
        with open(file_path) as f:
            rows = csv.DictReader(f)
            rows = [row for row in rows]

        # For each IP address in the subnet,
        # run the ping command with subprocess.popen interface
        for i in range(len(all_hosts)):
            output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])],
                                      stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
            # print(output.decode('utf-8'))  # testing
            # Depending on result write status to OrderedDict
            if "Destination host unreachable" in output.decode('utf-8'):
                ip = str(all_hosts[i])
                status = "Offline"
                for row in rows:
                    if row['ip'] == ip:
                        row['status'] = status
            elif "Request timed out" in output.decode('utf-8'):
                ip = str(all_hosts[i])
                status = "Offline"
                for row in rows:
                    if row['ip'] == ip:
                        row['status'] = status
            elif "Reply from" in output.decode('utf-8'):
                ip = str(all_hosts[i])
                status = "Online"
                date = time.strftime('%m/%d/%Y %H:%M:%S')
                for row in rows:
                    if row['ip'] == ip:
                        row['status'] = status
                        row['date'] = time.strftime('%m/%d/%Y %H:%M:%S')
            # Catch all for any other result
            else:
                ip = str(all_hosts[i])
                status = "error"
                for row in rows:
                    if row['ip'] == ip:
                        row['status'] = status
        # print('dict update complete')  # testing

        # Rewrite file with current Dict
        with open(file_path, "w", newline='') as outfile:
            fieldnames = ['ip', 'status', 'date', 'notes']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        print('File Updated')  # test should display file?

    # If file does not exist create new list, scan, and write to file
    elif not os.path.isfile(file_path):
        # Create the CSV file
        text_file = open(networkName, "w")

        # create nested list and variables for fieldnames
        scan_list = [('{},{},{},{}\n'.format('ip', 'status', 'date', 'notes'))]
        ip = ''
        status = ''
        date = ''
        notes = ''

        # For each IP address in the subnet,
        # run the ping command with subprocess.popen interface
        for i in range(len(all_hosts)):
            output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])],
                                      stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
            if "Destination host unreachable" in output.decode('utf-8'):
                ip = str(all_hosts[i])
                status = "Offline"
                date = ""
            elif "Request timed out" in output.decode('utf-8'):
                ip = str(all_hosts[i])
                status = "Offline"
                date = ""
            else:
                ip = str(all_hosts[i])
                status = "Online"
                date = time.strftime('%m/%d/%Y %H:%M:%S')
            scan_list.append('{},{},{},{}\n'.format(ip, status, date, notes))
        # Write list to file
        for ip in scan_list:
            text_file.write(ip)
        print("Scan Complete")
    else:
        print("Error")


def notes(notesArg):
    if '?' in notesArg:
        newline()
        openRead(".\help\helpNote.txt")
    notesSplit = notesArg.split(' ', 4)
    netAddress = notesSplit[1]
    netName = notesSplit[2]
    ip = notesSplit[3]
    note = notesSplit[4]
    filePath = (netName + '_' + netAddress.split('/')
                [0] + '_' + netAddress.split('/')[-1] + ".scan")
    # Read the file into the OrderedDict
    with open(filePath) as n:
        rows = csv.DictReader(n)
        rows = [row for row in rows]
    for row in rows:
        if row['ip'] == ip:
            row['notes'] = note
            newline()
            print(row['ip'] + ',' + row['status'] +
                  ',' + row['date'] + ',' + row['notes'])
    with open(filePath, "w", newline='') as outfile:
        fieldnames = ['ip', 'status', 'date', 'notes']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print('Note Added')


def commandTree():
    # commands for the terminal
    a = 1
    while a == 1:
        try:
            # Terminal prompt that accepts commands from the list below
            userCmd = input("ipscan~$ ")
            if 'scan' in userCmd:
                ipscan(userCmd)
            elif 'list' in userCmd:
                listFiles()
            elif 'delete' in userCmd:
                delete(userCmd)
            elif 'note' in userCmd:
                notes(userCmd)
            elif 'display' in userCmd:
                display(userCmd)
            elif userCmd == 'exit' or userCmd == 'end' or userCmd == 'quit':
                a = 0
            else:
                help(userCmd)
        except:
            continue


commandTree()
