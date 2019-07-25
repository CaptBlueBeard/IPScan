# Import modules
import subprocess
import ipaddress
import time
import csv
import os.path
import os
import socket


def newline():
    print('')


def listFiles():
    # list the .scan files in the working directory
    files = os.listdir(".\\")
    newline()
    print("{:<15} {:<15}".format('CIDR', 'Name'))
    for f in files:
        if '.scan' in f:
            splitFile = f.split('_')
            splitExt = splitFile[2].split('.')
            print("{:<15} {:<15}".format(
                (splitFile[1] + "/" + splitExt[0]), splitFile[0]))
    newline()


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
    elif detail == '':
        newline()
        openRead(".\help\helpShort.txt")
    elif detail == 'scan' or detail == 'scan ' or detail == 'scan ?':
        newline()
        openRead(".\help\helpScan.txt")
    elif detail == 'note' or detail == 'note ' or detail == 'note ?':
        newline()
        openRead(".\help\helpScan.txt")


def fileName(fileArg):
    # accepts the users input and returns the file name for the scan
    fileSplit = fileArg.split(' ')
    netAddr = fileSplit[1]
    f = fileSplit[2] + '_' + \
        netAddr.split('/')[0] + '_' + netAddr.split('/')[-1]+".scan"
    return f


def delete(deleteArg):
    # deletes a file associated with a scan.
    if deleteArg == 'delete' or deleteArg == 'delete ?' or deleteArg == 'delete ':
        newline()
        openRead(".\help\helpDelete.txt")
        return
    f = fileName(deleteArg)
    if os.path.isfile(f):
        if input("Are you sure you want to delete " + f + "? (y/n) ") == "y":
            os.unlink(f)
            print('Scan deleted')
    else:
        print('No scan found')


def ipscan(scanArg):
    # Scans network defined by user
    # Creates a file if there isn't one, updates the file if there is
    if '?' in scanArg:
        newline()
        openRead(".\help\helpScan.txt")
        return
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
        host = ''
        with open(file_path) as f:
            rows = csv.DictReader(f)
            rows = [row for row in rows]
        # For each IP address in the subnet,
        # run the ping command with subprocess.popen interface
        for i in range(len(all_hosts)):
            output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])],
                                      stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
            try:
                hostName = (socket.gethostbyaddr(str(all_hosts[i])))
                host = str(hostName[0])
            except socket.herror:
                pass
            print('.', end='', flush=True)
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
            fieldnames = ['ip', 'host', 'status', 'date', 'notes']
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
        scan_list = [('{},{},{},{},{}\n'.format(
            'ip', 'host', 'status', 'date', 'notes'))]
        ip = ''
        status = ''
        date = ''
        notes = ''
        host = ''
        # For each IP address in the subnet,
        # run the ping command with subprocess.popen interface
        for i in range(len(all_hosts)):
            output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])],
                                      stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
            try:
                hostName = (socket.gethostbyaddr(str(all_hosts[i])))
                host = str(hostName[0])
            except socket.herror:
                pass
            print('.', end='', flush=True)
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
            scan_list.append('{},{},{},{},{}\n'.format(
                ip, host, status, date, notes))
        # Write list to file
        for ip in scan_list:
            text_file.write(ip)
        print("Scan Complete")
    else:
        print("Error")


def notes(notesArg):
    if notesArg == 'notes' or notesArg == 'notes ?' or notesArg == 'notes ':
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
            elif userCmd == '?':
                help(userCmd)
        except:
            continue


def display(displayArg):
    # displays scans to the terminal
    if displayArg == 'display' or displayArg == 'display ?' or displayArg == 'display ':
        newline()
        openRead(".\\help\\helpDisplay.txt")
        return
    f = fileName(displayArg)
    print("{:<17} {:<40} {:<10} {:<20} {:<50}".format(
        'ip', 'host', 'status', 'date contacted', 'notes'))
    if os.path.isfile(f):
        # Read the file into the OrderedDict
        with open(f) as f:
            rows = csv.DictReader(f)
            rows = [row for row in rows]
        for row in rows:
            print("{:<17} {:<40} {:<10} {:<20} {:<50}".format(
                row['ip'], row['host'], row['status'], row['date'], row['notes']))
    else:
        print('No scan to display')


commandTree()
