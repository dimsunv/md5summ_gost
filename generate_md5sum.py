#!usr/bin/python3
# -*- coding: UTF-8 -*-

import subprocess
import os
import sys
from datetime import datetime
from docxtpl import DocxTemplate


# Входящие переменные
if __name__ == "__main__":
    if len (sys.argv) > 1:
        in_dir = '{}'.format (sys.argv[1]) #директория с проектом
        out_dir = '{}/'.format (sys.argv[2]) # Папка вывода результата
        method = '{}'.format (sys.argv[3]) # метод подсчета контрольных сумм

doc_tpl = DocxTemplate('/usr/local/bin/md5scr/template.docx') #файл шаблона
os_version = subprocess.getoutput('lsb_release -d | grep "Description:" |  sed "s/Description:\t//"') #Версия ОС
filelist = []
table = []

# Создаем список файлов в каталоге
if not os.listdir(in_dir):
    exit(0)
else:
    for root, dirs, files in os.walk(in_dir):
        for file in files:
            filelist.append(os.path.join(root, file))

def create_report(datestr,MD5_ISO,iso_size): # Генерируем файл отчета
    context = {
        'os_version': os_version,
        'now_date': datestr,
        'MD5_ISO': MD5_ISO.partition(' ')[0],
        'iso_size': iso_size.st_size,
        'tbl_contents': table,
        }
    doc_tpl.render(context)
    doc_tpl.save('{}{}.docx'.format(out_dir,datestr))

def md5(): 
    #Генерация временной метки
    now = datetime.now()
    datestr = now.strftime("%d-%m-%Y_%H-%M-%S")
    
    # Создаем iso и получаем размер образа
    os.system('genisoimage -udf -iso-level 3 -V {} -o "{}{}.iso" "{}" | grep "extents written"'.format(datestr,out_dir,datestr,in_dir))
    iso_size = os.stat('{}{}.iso'.format(out_dir,datestr))
    
    # Считаем контрольную сумму образа
    ISO_block_size = subprocess.getoutput('isoinfo -d -i "{}{}.iso" | grep "Logical block size is:" | sed "s/Logical block size is: //"'.format(out_dir,datestr))
    ISO_volume_size = subprocess.getoutput('isoinfo -d -i "{}{}.iso" | grep "Volume size is:" | sed "s/Volume size is: //"'.format(out_dir,datestr))
    MD5_ISO = subprocess.getoutput('dd if="{}{}.iso" bs={} count={} conv=notrunc,noerror status=none | md5sum -b | sed "s/..-\$//"'.format(out_dir,datestr,ISO_block_size,ISO_volume_size))
    subprocess.getoutput('export LC_ALL=C && find {} -type f -print0 | sort -z | xargs -0 cat | md5sum | sed "s/..-\$//" >> {}DM_{}.txt'.format(in_dir,out_dir,datestr))

    # Считаем контрольную сумму файлов в массиве и записываем в список
    for name in filelist:
        hashsum = subprocess.getoutput('md5sum -b "{}"'.format(name))
        table.append({'file': os.path.basename(name), 'summ': hashsum.partition(' ')[0]})

    create_report(datestr,MD5_ISO,iso_size)
    
def gost256(): 
    now = datetime.now()
    datestr = now.strftime("%d-%m-%Y_%H-%M-%S")
    os.system('genisoimage -udf -iso-level 3 -V {} -o "{}{}.iso" "{}" | grep "extents written"'.format(datestr,out_dir,datestr,in_dir))
    iso_size = os.stat('{}{}.iso'.format(out_dir,datestr))
    MD5_ISO = subprocess.getoutput('gostsum --gost-2012 -d "{}{}.iso"'.format(out_dir,datestr))

    for name in filelist:
        hashsum = subprocess.getoutput('gostsum --gost-2012 -d "{}"'.format(name))
        table.append({'file': os.path.basename(name), 'summ': hashsum.partition(' ')[0]})

    create_report(datestr,MD5_ISO,iso_size,MD5_DM)

def gost512(): 
    now = datetime.now()
    datestr = now.strftime("%d-%m-%Y_%H-%M-%S")
    os.system('genisoimage -udf -iso-level 3 -V {} -o "{}{}.iso" "{}" | grep "extents written"'.format(datestr,out_dir,datestr,in_dir))
    iso_size = os.stat('{}{}.iso'.format(out_dir,datestr))
    MD5_ISO = subprocess.getoutput('gostsum --gost-2012-512 -d "{}{}.iso"'.format(out_dir,datestr))

    for name in filelist:
        hashsum = subprocess.getoutput('gostsum --gost-2012-512 -d "{}"'.format(name))
        table.append({'file': os.path.basename(name), 'summ': hashsum.partition(' ')[0]})

    create_report(datestr,MD5_ISO,iso_size)


if method == 'md5':
    md5()
elif method == 'gost256':
    gost256()
elif method == 'gost512':
    gost512()
