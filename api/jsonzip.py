import zipfile
import glob
import os
import progressbar


def main():
    file_set = set()
    os.system("mkdir -p /tmp/jsonzip/")
    files = glob.glob("/tmp/json/*")
    for f in files:
        file_set.add(f.split('.')[0].split('/')[-1])
    l = list(file_set)
    l.sort()
    bar = progressbar.ProgressBar()
    mode = zipfile.ZIP_DEFLATED
    for i in bar(l):
        files = glob.glob("/tmp/json/{}.*".format(i))
        with zipfile.ZipFile('/tmp/jsonzip/{}.zip'.format(i), 'w', compression=mode) as myzip:
            for f in files:
                myzip.write(f, arcname=f.split('/')[-1])
    for i in ["toc", "main"]:
        files = glob.glob("/tmp/json/{}.*".format(i))
        with zipfile.ZipFile('/tmp/jsonzip/{}.zip'.format(i), 'w', compression=mode) as myzip:
            for f in files:
                myzip.write(f, arcname=f.split('/')[-1])


if __name__ == '__main__':
    main()
