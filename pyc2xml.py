import struct
from xml.dom import minidom
import sys
import time

intern_str = []

def main():
    script,fname = sys.argv
    while not fname.endswith('.pyc'):
        fname = raw_input('input a pyc file >\n')
    a = open(fname)
    b = a.read()
    a.close()
    x = struct.unpack_from('c'*len(b),b)
    return x

def get_length(pyc,cursor):
    tmp = ''
    for i in range(cursor,cursor+4):
        tmp += pyc[i]
    y = struct.unpack('i',tmp)
    return y[0]


def parse_obj(pyc,cursor):
    figure = pyc[cursor]
    if figure not in "(itsNc{R":
        figure = '('
        cursor += 4
    figure = pyc[cursor]
    if figure == 'i':
        cursor += 5
        return get_length(pyc,cursor-4),cursor
    elif figure == 't' or figure == 's':
        cursor += 5
        length = get_length(pyc,cursor-4)
        tmp = figure + ' '
        for i in range(cursor,cursor+length):
            tmp += pyc[i]
        cursor += length
        if figure == 't':
            intern_str.append(tmp)
        return tmp,cursor
    elif figure == '(':
        cursor += 5
        tmp_list = []
        items = get_length(pyc,cursor-4)
        for i in range(items):
            one = parse_obj(pyc,cursor)
            cursor = one[1]
            tmp_list.append(one[0])
        return tmp_list,cursor
    elif figure == 'N':
        return None,cursor+1
    elif figure == 'R':
        return 'ref '+ intern_str[get_length(pyc,cursor+1)],cursor+5
    elif figure == 'c':
        return parse_code(pyc,cursor)
    else:
        return None,cursor+1

def parse_code(pyc,cursor):
    tmp_list = []
    cursor += 1
    a = get_length(pyc,cursor)
    cursor += 4
    b = get_length(pyc,cursor)
    cursor += 4
    c = get_length(pyc,cursor)
    cursor += 4
    flag = get_length(pyc,cursor)
    cursor += 5
    stringlen = get_length(pyc,cursor)
    cursor += stringlen
    cursor += 4
    figure = pyc[cursor]
    args = [a,b,c]
    tmp_list.append(a)
    tmp_list.append(b)
    tmp_list.append(c)
    tmp_list.append(stringlen)
    for i in range(8):
        if figure in "sti(NcR{":
            one = parse_obj(pyc,cursor)
            tmp_list.append(one[0])
            cursor = one[1]
        else:
            return None,cursor+1
    return tmp_list,cursor


class parse_pyc():
    def __init__(self,pycfile):
        self.pycfile = pycfile
        self.cursor = 26      #the starting of the co_code item

    def get_time(self):
        tmp_string = ''
        for i in range(4,8):
            tmp_string += self.pycfile[i]
        y = struct.unpack('i',tmp_string)
        return time.ctime(y[0])
    
    def get_all_args(self):
        arguments = []
        args_count = ''
        for i in range(3):
            for j in range(9,13):
                args_count += self.pycfile[i*4 + j]
            y = struct.unpack('i',args_count)
            arguments.append(y[0])
            args_count = ''
        return arguments

    def get_code(self):
        cursor = self.cursor
        self.cursor += 4 #the length is 4
        tmp = ''
        for i in range(cursor,cursor+4):
            tmp += self.pycfile[i]
        y = struct.unpack('i',tmp)
        self.cursor += y[0]
        return y[0]

    def get_consts(self):
        consts,self.cursor = parse_obj(self.pycfile,self.cursor)
        #print "here %d"%self.cursor
        return consts

    def get_names(self):
        names,self.cursor = parse_obj(self.pycfile,self.cursor)
        return names

    def get_varnames(self):
        varnames,self.cursor =  parse_obj(self.pycfile,self.cursor)
        return varnames

    def get_freevars(self):
        freevars,self.cursor = parse_obj(self.pycfile,self.cursor)
        return freevars

    def get_cellvars(self):
        cellvars,self.cursor = parse_obj(self.pycfile,self.cursor)
        return cellvars

    def get_filename(self):
        filename,self.cursor = parse_obj(self.pycfile,self.cursor)
        return filename

    def get_lineno(self):
        lineno,self.cursor = parse_obj(self.pycfile,self.cursor)
        return lineno

    def get_lnotab(self):
        lnotab,self.cursor = parse_obj(self.pycfile,self.cursor)
        return list(lnotab)

def out(parsed_file):
    a,b,c = parsed_file.get_all_args()
    code_len = parsed_file.get_code()
    consts = parsed_file.get_consts()
    names = parsed_file.get_names()
    varnames = parsed_file.get_varnames()
    freevars = parsed_file.get_freevars()
    cellvars = parsed_file.get_cellvars()
    filename = parsed_file.get_filename()
    name = parsed_file.get_names()
    firstLineNo = parsed_file.get_lineno()
    return [a,b,c,code_len,consts,names,varnames,freevars,cellvars,filename,\
            name,firstLineNo]


def output_child(parsed_lst):
    xml_tags = ['argCount','localCount','stackSize','Code','consts','names','varnames','freevars','cellvars','filename','name','firseLineNo']
    doc = minidom.Document()
    pycfile = doc.createElement("PycFile")
    codeobj = doc.createElement('codeObject')
    for i in range(len(parsed_lst)):
        tmp_node = doc.createElement(xml_tags[i])
        if i >= 0 and i < 3:
            tmp_node.setAttribute("value",str(parsed_lst[i]))
        elif i == 3:
            sub_node = doc.createElement('str')
            sub_node.setAttribute('len',str(parsed_lst[i]))
            tmp_node.appendChild(sub_node)
        elif i == 4:
            for j in parsed_lst[i]:
                if isinstance(j,list):
                    sub_node = doc.createElement("codeObject")
                    sub_node.appendChild(output_child(j))
                    tmp_node.appendChild(sub_node)
                elif isinstance(j,int):
                    sub_node = doc.createElement('int')
                    sub_node.setAttribute('value',str(j))
                    tmp_node.appendChild(sub_node)
                elif isinstance(j,str):
                    tiny = j.split()
                    if tiny[0] == 't':
                        sub_node = doc.createElement('internStr')
                        sub_node.setAttribute('index',str(intern_str.index(j)))
                    else:
                        sub_node = doc.createElement('Str')
                    sub_node.setAttribute('length',str(len(tiny[1])))
                    sub_node.setAttribute('value',tiny[1])
                    tmp_node.appendChild(sub_node)
                else:
                    sub_node = doc.createElement("NoneObject")
                    tmp_node.appendChild(sub_node)
        else:
            if isinstance(parsed_lst[i],str):
                parsed_lst[i] = [parsed_lst[i]]
            for j in parsed_lst[i]:
                if isinstance(j,int):
                    sub_node = doc.createElement('int')
                    sub_node.setAttribute('value',str(j))
                    tmp_node.appendChild(sub_node)
                elif isinstance(j,str):
                    tiny = j.split()
                    if tiny[0] == 't':
                        sub_node = doc.createElement('internStr')
                        sub_node.setAttribute('index',str(intern_str.index(j)))
                    else:
                        sub_node = doc.createElement('Str')
                    sub_node.setAttribute('length',str(len(tiny[1])))
                    sub_node.setAttribute('value',tiny[1])
                    tmp_node.appendChild(sub_node)
                else:
                    sub_node = doc.createElement('NoneObject')
                    tmp_node.appendChild(sub_node)

        codeobj.appendChild(tmp_node)
    pycfile.appendChild(codeobj)
    doc.appendChild(pycfile)
    return pycfile


if __name__ == "__main__":
    pycfile = main()
    parse_py = parse_pyc(pycfile)
    doc = output_child(out(parse_py))
    print doc.toprettyxml(indent='    ')
